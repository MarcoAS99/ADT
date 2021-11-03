from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from schemas import User_model
import time
from database import get_conn, get_engine
from models.modelsDb import define_Tables
import docker

app = FastAPI()

client = docker.from_env()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../html")

mydb = None
engine = None


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


@app.on_event("shutdown")
async def shutdown():
    print("Stopping container...")
    mydb.stop()
    print("Container stopped.")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def post_login(request: Request):
    form = await request.form()
    user_log = User_model()
    with engine.connect() as conn:
        is_logged = await user_log.login(conn, form.get("email"), form.get("password"))
    if is_logged:
        return {"login": "logged"}
    return templates.TemplateResponse("login.html", {"request": request, "error": user_log.error_list})


@app.post('/', status_code=status.HTTP_201_CREATED)
async def register(request: Request):
    form = await request.form()
    user_reg = User_model()
    with engine.connect() as conn:
        is_registered = await user_reg.register(conn, form.get("name"), form.get("email"), form.get("phone"), form.get("password"), form.get("paymethod"))
    if is_registered:
        return RedirectResponse(url='/login',  status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": request, "error": user_reg.error_list})


@app.get("/users")
async def get_users():
    with engine.connect() as conn:
        res = conn.execute("SELECT * FROM User;").fetchall()
    return res
