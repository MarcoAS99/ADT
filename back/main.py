from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import User

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../html")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/', status_code=status.HTTP_201_CREATED)
async def register(request: Request):
    form = await request.form()
    user_reg = User()
    if await user_reg.register(form.get("name"), form.get("email"), form.get("phone"), form.get("password"), ''):
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "error": user_reg.error_list})
