from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from codes.database import engine, Base, get_db
from codes.auth import authenticate_user, create_user, get_user_by_username, get_user_by_email


Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

from fastapi.staticfiles import StaticFiles
import os

# Указываем путь к статическим файлам относительно main.py
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")




places_data = {
    "Казанский Кремль": {"categories": ["history", "culture"], "description": "Казанский Кремль — исторический центр Казани."},
    "Храм всех религий": {"categories": ["history", "culture"], "description": "Храм всех религий — архитектурное сооружение в Казани."},
    "Башня Сеюмбике": {"categories": ["history", "culture"], "description": "Башня Сеюмбике — символ Казани, одно из наиболее известных строений."},
    "Кул Шариф": {"categories": ["history", "culture"], "description": "Мечеть Кул Шариф — главная мечеть Татарстана."},
    "Казанско-Богородицкий мужской монастырь": {"categories": ["history", "culture"], "description": "Казанско-Богородицкий мужской монастырь — одно из известных религиозных сооружений."},
    "Парк Горького": {"categories": ["entertainment", "nature"], "description": "Парк Горького — популярное место для прогулок и отдыха в Казани."},
    "Аквапарк Ривьера": {"categories": ["entertainment"], "description": "Аквапарк Ривьера — один из крупнейших аквапарков в России."},
}

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
    return templates.TemplateResponse("index.html", {"request": request})

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
    return RedirectResponse(url=f"/profile/{user.username}", status_code=status.HTTP_302_FOUND)


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
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

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
