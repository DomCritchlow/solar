from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .routes import router
from .services import get_solar_data

app = FastAPI(title="Solar Monitor")
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    data = await get_solar_data()
    return templates.TemplateResponse("index.html", {"request": request, "data": data})
