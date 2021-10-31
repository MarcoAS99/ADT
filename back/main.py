from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from schemas import User_model
from database import conn, engine, meta

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../html")


@app.on_event("startup")
async def startup():
    meta.create_all(engine)


@app.on_event("shutdown")
async def shutdown():
    if not conn.closed:
        print("Closing conn...")
        conn.close()


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
    if await user_log.login(form.get("email"), form.get("password")):
        return {"login": "logged"}
    return templates.TemplateResponse("login.html", {"request": request, "error": user_log.error_list})


@app.post('/', status_code=status.HTTP_201_CREATED)
async def register(request: Request):
    form = await request.form()
    user_reg = User_model()
    if await user_reg.register(form.get("name"), form.get("email"), form.get("phone"), form.get("password"), form.get("paymethod")):
        return RedirectResponse(url='/login',  status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": request, "error": user_reg.error_list})


@app.get("/users")
async def get_users():
    return conn.execute("SELECT * FROM User;").fetchall()
