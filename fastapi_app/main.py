from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.db.database import init_db
from app.api import auth, users, messenger, tasks, olympiads, problems, news, learning, admin, friends
from app.middleware.rate_limiter import RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



gettext_fn = lambda x: x

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["_"] = gettext_fn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Application started successfully")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(messenger.router, prefix="/api/messenger", tags=["Messenger"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(olympiads.router, prefix="/api/olympiads", tags=["Olympiads"])
app.include_router(problems.router, prefix="/api/olympiads", tags=["Problems"])
app.include_router(news.router, prefix="/api", tags=["News"])
app.include_router(learning.router, prefix="/api/learning", tags=["Learning"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(friends.router, prefix="/api/friends", tags=["Friends"])


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("base.html", {
        "request": request,
        "current_user": None
    })


@app.get("/problems")
async def problems_page(request: Request):
    return templates.TemplateResponse("problems.html", {
        "request": request,
        "current_user": None
    })


@app.get("/tasks")
async def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "current_user": None
    })


@app.get("/messenger")
async def messenger_page(request: Request):
    return templates.TemplateResponse("messenger.html", {
        "request": request,
        "current_user": None
    })


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "debug": settings.DEBUG
    }


@app.get("/api")
async def api_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/auth")
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {
        "request": request,
        "current_user": None
    })


@app.get("/news")
async def news_page(request: Request):
    return templates.TemplateResponse("news.html", {
        "request": request,
        "current_user": None
    })


@app.get("/olympiads")
async def olympiads_page(request: Request):
    return templates.TemplateResponse("problems.html", {
        "request": request,
        "current_user": None
    })


@app.get("/learning")
async def learning_page(request: Request):
    return templates.TemplateResponse("learning.html", {
        "request": request,
        "current_user": None
    })


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("auth.html", {
        "request": request,
        "current_user": None
    })


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth.html", {
        "request": request,
        "current_user": None
    })


@app.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse("base.html", {
        "request": request,
        "current_user": None
    })
