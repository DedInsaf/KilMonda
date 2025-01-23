from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

import secrets

from database import engine, Base, get_db
from auth import authenticate_user, create_user, get_user_by_username, get_user_by_email

from fastapi.staticfiles import StaticFiles
import os

from starlette.middleware.sessions import SessionMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex())

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
    "Театр оперы и балета имени Мусы Джалиля": { "categories": ["culture", "entertainment"], "description": "Театр оперы и балета — одно из главных культурных мест Казани."},
    "Озеро Лебяжье": {"categories": ["nature"],"description": "Озеро Лебяжье — живописное место для отдыха на природе."},
    "Кукольный театр Экият": {
        "categories": ["culture", "entertainment"],
        "description": "Кукольный театр Экият — популярное место для семейного отдыха.",
    },
    "Парк Тысячелетия": {
        "categories": ["nature", "entertainment"],
        "description": "Парк Тысячелетия — современное место для прогулок в Казани.",
    },
    "Мечеть Аль-Марджани": {
        "categories": ["history", "culture"],
        "description": "Мечеть Аль-Марджани — одна из старейших мечетей Казани.",
    },
    "Татарский государственный Академический театр имени Галиасгара Камала": {
        "categories": ["culture"],
        "description": "Театр Камала — крупнейший татарский драматический театр.",
    },
    "Центр семьи Казан": {
        "categories": ["culture", "entertainment"],
        "description": "Центр семьи Казан — известное архитектурное сооружение и ЗАГС.",
    },
    "Сквер Габдуллы Тукая": {
        "categories": ["nature", "culture"],
        "description": "Сквер Габдуллы Тукая — место для прогулок, посвящённое татарскому поэту.",
    },
    "Площадь Свободы": {
        "categories": ["culture", "history"],
        "description": "Площадь Свободы — значимое место для мероприятий в Казани.",
    },
    "ТЦ «Кольцо»": {
        "categories": ["shopping", "entertainment"],
        "description": "Торговый центр «Кольцо» — популярное место для шопинга и развлечений.",
    },
    "Национальный музей Республики Татарстан": {
        "categories": ["culture", "history"],
        "description": "Национальный музей Татарстана — главный музей региона.",
    },
    "Парк Урицкого": {
        "categories": ["nature"],
        "description": "Парк Урицкого — зелёная зона для прогулок и отдыха.",
    },
    "Нижний Кабан": {
        "categories": ["nature"],
        "description": "Нижний Кабан — озеро, популярное место для прогулок и фотосессий.",
    },
    "Музей чак-чака": {
        "categories": ["culture", "food"],
        "description": "Музей чак-чака — уникальное место, посвящённое татарскому десерту.",
    },
    "Речной порт": {
        "categories": ["history", "entertainment"],
        "description": "Речной порт Казани — историческое место и транспортный узел.",
    },
    "Музей советских игровых автоматов": {
        "categories": ["entertainment", "culture"],
        "description": "Музей советских игровых автоматов — уникальное место с ретро-играми.",
    },
    "Дворец земледельцев": {
        "categories": ["culture", "architecture"],
        "description": "Дворец земледельцев — архитектурное достояние Казани.",
    },
    "Музей-заповедник «Остров-град Свияжск»": {
        "categories": ["history", "culture"],
        "description": "Свияжск — исторический остров-град с уникальными памятниками.",
    },
    "Казанская набережная": {
        "categories": ["nature", "entertainment"],
        "description": "Казанская набережная — место для прогулок и мероприятий.",
    },
    "Музей естественной истории Татарстана": {
        "categories": ["culture", "education"],
        "description": "Музей естественной истории — интересное место для изучения науки.",
    },
    "Музей А.М. Горького и Ф.И. Шаляпина": {
        "categories": ["culture", "history"],
        "description": "Музей, посвящённый А.М. Горькому и Ф.И. Шаляпину.",
    },
    "Парк Победы": {
        "categories": ["nature", "history"],
        "description": "Парк Победы — мемориальный комплекс и зелёная зона.",
    },
    "Планетарий Казанского федерального университета": {
        "categories": ["education", "entertainment"],
        "description": "Планетарий КФУ — интересное место для любителей астрономии.",
    },
    "Литературный музей имени Габдуллы Тукая": {
        "categories": ["culture", "history"],
        "description": "Музей, посвящённый жизни и творчеству Габдуллы Тукая.",
    },
    "Казанский цирк": {
        "categories": ["entertainment"],
        "description": "Казанский цирк — популярное место для семейного отдыха.",
    },
    "Казанская ярмарка": {
        "categories": ["shopping", "entertainment"],
        "description": "Казанская ярмарка — место для ярмарочных мероприятий и выставок.",
    },
    "Чёрное озеро": {
        "categories": ["nature"],
        "description": "Чёрное озеро — живописное место для отдыха и прогулок.",
    },
}

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
