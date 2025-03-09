from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

import secrets
import json

from database import engine, Base, get_db
from auth import authenticate_user, create_user, get_user_by_username, get_user_by_email

from fastapi.staticfiles import StaticFiles
import os

from starlette.middleware.sessions import SessionMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex())

app.mount("/static", StaticFiles(directory="static"), name="static")

def load_places_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'places.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"Places data file not found at {file_path}")
    except json.JSONDecodeError:
        raise RuntimeError("Error decoding JSON data")

places_data = load_places_data()

@app.get("/kazan_kremlin")
async def kazan_kremlin(request: Request):
    return templates.TemplateResponse("kazan_cremlin.html", {"request": request})

@app.get("/all_region_temple")
async def all_region_temple(request: Request):
    return templates.TemplateResponse("all_religions_temple.html", {"request": request})

@app.get("/place/{place_name}", response_class=HTMLResponse)
async def place_detail(request: Request, place_name: str):
    """
    Переход на страницу с информацией о конкретном месте.
    """
    # Отображаем заранее созданные статические HTML-файлы для каждого места
    return templates.TemplateResponse(f"{place_name}.html", {"request": request})

@app.get("/home")
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("test.html", {"request": request, "user": user})

@app.get("/test")
def text_page(request: Request):
    return templates.TemplateResponse("index.html")

@app.get("/routes")
def routes(request: Request):
    return templates.TemplateResponse("routes.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/login")
def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid password. Please try again."
        })
    response = RedirectResponse(url=f"/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="username", value=user.username)
    return response

@app.get("/logout", response_class=RedirectResponse)
def logout(response: RedirectResponse):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="username")
    return response

@app.post("/register")
def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...),
                  db: Session = Depends(get_db)):
    user_by_username = get_user_by_username(db, username)
    user_by_email = get_user_by_email(db, email)

    if user_by_username:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username is already registered. Please choose another username."
        })

    if user_by_email:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email is already registered. Please login instead."
        })

    create_user(db, username, email, password)
    return RedirectResponse(url="login", status_code=status.HTTP_302_FOUND)

@app.get("/profile/{username}", response_class=HTMLResponse)
def profile(request: Request, username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.get("/map/", response_class=HTMLResponse)
async def map_page(request: Request):
    return templates.TemplateResponse("map_page.html", {"request": request})

# Маршрут для отображения страницы с предпочтениями
@app.get("/categories", response_class=HTMLResponse)
def preferences_page(request: Request):
    return templates.TemplateResponse("preferences.html", {"request": request})

@app.post("/recommend/", response_class=HTMLResponse)
async def recommend_places(request: Request, preferences: list = Form(...)):
    """
    Обработка предпочтений пользователя и выдача рекомендаций.
    """
    # Преобразуем preferences в список, если это строка
    if isinstance(preferences, str):
        preferences = [preferences]

    # Найдем места, соответствующие хотя бы одной из выбранных категорий
    recommended_places = []
    for place, data in places_data.items():
        if any(preference in data["categories"] for preference in preferences):
            recommended_places.append(place)

    # Отображаем список мест с ссылками на их статические страницы
    return templates.TemplateResponse("recommendations.html", {
        "request": request,
        "recommended_places": recommended_places
    })


@app.post("/profile/{username}/regenerate-key")
def regenerate_key(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерация нового ключа
    user.key = secrets.token_hex(16)
    db.commit()
    return {"message": "Key successfully regenerated", "key": user.key}

@app.get("/subscribe", response_class=HTMLResponse)
async def get_subscriptions(request: Request):
    return templates.TemplateResponse("subscription.html", {"request": request})

@app.get("/subscribe/under25", response_class=HTMLResponse)
async def get_under_25_subscription(request: Request):
    return templates.TemplateResponse("subscribe_under25.html", {"request": request})

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8009)
