import hashlib
from typing import List, Optional
from fastapi import FastAPI, Request, status, HTTPException
from fastapi import security
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.datastructures import Headers
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_302_FOUND
from schemas import Taxi_Model, Request_model, User_model
from models.initializeTaxis import create_taxis
import time
from database import get_conn, get_engine
from models.modelsDb import define_Tables
import docker
from validate_mail import send_validation_email


app = FastAPI()

security = HTTPBasic()

client = docker.from_env()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../html")

mydb = None
engine = None

notifications = {}


@app.on_event("startup")
async def startup():
    #client.images.build(dockerfile="./db/Dockerfile", tag="mymysql")
    global mydb
    global engine
    try:
        print('Trying to find image...')
        client.images.get("mysql")
        print('Image Found...')
    except docker.errors.ImageNotFound:
        print('WARNING: mysql image was not found.')
        print('Pulling mysql image...')
        client.images.pull("mysql")
        print('Done pulling image.')
    try:
        print('Trying to find container...')
        mydb = client.containers.get('mysqldb')
        print('Container found.')
        print('Starting docker container...')
        mydb.start()
        time.sleep(5)
        print('Docker container started.')
    except docker.errors.NotFound:
        print('WARNING: mysql container was not found')
        print('Running docker container...')
        mydb = client.containers.run("mysql", name='mysqldb', environment=[
            "MYSQL_ROOT_PASSWORD=root", "MYSQL_DATABASE=adt"], ports={'3306/tcp': ('127.0.0.1', 3306)}, detach=True)
        time.sleep(40)
        print('docker container running.')

    print('connecting to db...')
    engine = get_engine()
    with engine.connect() as conn:
        print('connection stablished.')
        print("Creating ER model...")
        define_Tables().create_all(conn)
        print('ER model created correctly.')
        print("inserting taxis...")
        create_taxis(conn)
        print("taxis inserted correctly.")


@app.on_event("shutdown")
async def shutdown():
    print("Stopping container...")
    mydb.stop()
    print("Container stopped.")


@app.get("/{email}/validate")
async def validate_email(request: Request, email: str):
    user_validate = User_model()
    with engine.connect() as conn:
        is_validated = await user_validate.validate(conn, email)
    if is_validated:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    else:
        return {"error": "Error"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    print(request.method)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def post_login(request: Request):
    form = await request.form()
    user_log = User_model()
    email = form.get("email")
    with engine.connect() as conn:
        is_logged = await user_log.login(conn, email, form.get("password"))
    if is_logged:
        with engine.connect() as conn:
            priv = await user_log.is_admin(conn, email)
        if priv == 1:
            return {"admin": "admin"}
        # return templates.TemplateResponse("request_taxi.html", {"request": request, "login": "logged"})
        return RedirectResponse(url=f'/{hashlib.md5(email.encode()).hexdigest()}/home', status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": user_log.error_list})


@app.post('/', status_code=status.HTTP_201_CREATED)
async def register(request: Request):
    form = await request.form()
    if len(form.keys()) <= 0:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    user_reg = User_model()
    email = form.get("email")
    name = form.get("name")
    with engine.connect() as conn:
        is_registered = await user_reg.register(conn, name, email, form.get("phone"), form.get("password"), form.get("paymethod"))
    if is_registered:
        # SEND VALIDATION EMAIL
        send_validation_email(name, email)
        return templates.TemplateResponse("validate_register.html", {"request": request})
    return templates.TemplateResponse("register.html", {"request": request, "error": user_reg.error_list})


@app.get("/users")
async def get_users():
    with engine.connect() as conn:
        res = conn.execute("SELECT * FROM User;").fetchall()
    return res


@app.get("/admin")
async def read_current_user():
    return {"admin": "noAdmin"}


@app.get('/test')
async def test(request: Request):
    req = Request_model()
    with engine.connect() as conn:
        test = await req.check_pending_requests(conn)
    if test is None or test == []:
        return templates.TemplateResponse('request_updates.html', {"request": request})
    return templates.TemplateResponse('request_updates.html', {"request": request, "requests": test})


@app.post('/test')
async def testpost(request: Request):
    button = await request.form()

    if button.get('accepted') is not None:
        estado = 'accepted'
        id_req = button.get('accepted')
    else:
        estado = 'canceled'
        id_req = button.get('canceled')

    request_update = Request_model()
    taxi_update = Taxi_Model()
    id_taxi = button.get('id_taxi')
    id_user = button.get('id_user')
    with engine.connect() as conn:
        aux = await request_update.update(conn, id_req, estado)
        if aux:
            aux2 = await taxi_update.update(conn, id_taxi)

    if not notifications.keys().__contains__(f'{id_user}'):
        notifications[id_user] = []
    notifications[id_user].append(
        f"""Tu solicitud con identificador {id_req} sido revisada y {translate_estado(estado)} por un administrador, 
        contacte con atención al cliente ante cualquier duda""")
    return RedirectResponse(url='/test', status_code=HTTP_302_FOUND)


@app.get("/{email_hash}/home")
async def get_user_home(request: Request, email_hash: str):
    user_request = User_model()
    with engine.connect() as conn:
        res, user_id = await user_request.getId(conn, email_hash)
    if res:
        print(user_id, notifications)
        if notifications.keys().__contains__(f'{user_id}'):
            notifs = notifications[f'{user_id}']
        else:
            notifs = []
        print(notifs)
        return templates.TemplateResponse("user_home.html", {"request": request, 'notif': notifs, 'email_hash': email_hash})
    return RedirectResponse(url='/login', status_code=HTTP_200_OK)


@app.get("/{email_hash}/request_taxi")
async def get_request_taxi(request: Request):
    return templates.TemplateResponse("request_taxi.html", {"request": request})


@app.post("/{email_hash}/request_taxi")
async def post_request_taxi(request: Request, email_hash: str):
    form = await request.form()
    origin = form.get('origin')
    destination = form.get('destination')
    date = form.get('date')
    time = form.get('time')
    taxi_request = Request_model()
    user_request = User_model()
    with engine.connect() as conn:
        res, user_id = await user_request.getId(conn, email_hash)
        if res:
            res2, taxi_id = await taxi_request.request(conn, origin, destination)
            if res2:
                await taxi_request.postRequest(
                    conn, user_id, taxi_id, origin, destination, date, time)
    return RedirectResponse(url=f"/{email_hash}/home", status_code=HTTP_302_FOUND)


def translate_estado(estado: str):
    if estado == 'accepted':
        return 'aceptada'
    return 'cancelada'
