from fastapi import FastAPI, Request, Form, Depends, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from database import create_db_and_tables, get_db
from starlette.middleware.sessions import SessionMiddleware
from hashlib import md5
from os import system

from typing import Optional, Annotated

import sqlite3

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="??????")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.on_event("shutdown")
def on_shutdown():
    pass
    # connection_close()


app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/fonts", StaticFiles(directory="tr1/fonts"), name="fonts")
app.mount("/js", StaticFiles(directory="tr1/js"), name="js")
app.mount("/images", StaticFiles(directory="tr1/images"), name="images")

templates = Jinja2Templates(directory="tr1/")


class User(BaseModel):
    username: str
    password: str


@app.get("/", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": id})


def make_list(choco_info):
    result = []
    for row in choco_info:
        row_dict = {"id": row[0], "name": row[1], "available": row[2], "image": row[3]}
        result.append(row_dict)
    return result


@app.get("/image")
def get_image(filename: str):
    file = "tr1/" + filename
    return FileResponse(file)


@app.get("/item", response_class=HTMLResponse)
def item_page(request: Request, id, conn: sqlite3.Connection = Depends(get_db)):  # remove id: int
    vuln_chocolate_info = conn.execute("Select id, name, available, image from chocolate where id = \'{}\'".format(id),
                                       ).fetchone()
    # chocolate_info = conn.execute("Select id, name, available, image from chocolate where id = (?)",
    #   (id,)).fetchone()
    return templates.TemplateResponse("items.html", {"request": request, "info": vuln_chocolate_info})


@app.get("/chocolate", response_class=HTMLResponse)
def about(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    chocolate_info = conn.execute("Select id, name, available, image from chocolate").fetchall()
    return templates.TemplateResponse("chocolate.html", {"request": request, "chocolate": chocolate_info})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request, message: Optional[str] = None):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})


def check_user(user_login, conn):
    check = "SELECT EXISTS(SELECT 1 FROM users WHERE name=(?));"
    vuln_check = 'SELECT EXISTS(SELECT 1 FROM users WHERE name=\'{}\')'.format(user_login)
    # return conn.execute(check, (user_login,)).fetchone()[0]
    return conn.execute(vuln_check).fetchone()[0]


def get_password(password) -> str:
    hash_func = md5()
    hash_func.update(bytes(password, "utf-8"))
    return hash_func.hexdigest()


@app.post("/login")
def login(request: Request, user: str = Form(...), password: str = Form(...),
          conn: sqlite3.Connection = Depends(get_db)):
    # 1) fetch user by username
    if not check_user(user, conn):
        return RedirectResponse("/login?message=no+such+user", status_code=303)
    # 2) compare password hashes
    stored_password = conn.execute("select password from users where name is (?)", (user,)).fetchone()[0]
    if get_password(password) != stored_password:
        return RedirectResponse("/login?message=wrong+password", status_code=303)
    # 3) if match - set session to username
    else:
        request.session["username"] = "1234"
    username = conn.execute("SELECT name FROM users WHERE name = (?)", [user]).fetchone()[0]
    return RedirectResponse("/users/" + username, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signup(user: str = Form(...), password: str = Form(...), conn: sqlite3.Connection = Depends(get_db)):
    # 1) check whether user with this login already exists
    insert = "INSERT INTO users (name, password) VALUES(?, ?);"
    if check_user(user, conn):
        return RedirectResponse("/login?message=user+already+exists", status_code=303)
    else:
        password_hash = get_password(password)
        conn.execute(insert, [user, password_hash])
        conn.commit()
    return RedirectResponse("/login?message=new+user+is+created", status_code=303)


@app.get("/users/admin", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.post("/check_host")
def check_host(request: Request, host=Form(...)):
    os_command = True if system("ping -c 1 " + host) == 0 else False
    answer = "Host is up" if os_command else "Host is down"
    return answer


@app.post("/users/{name}")
async def user():
    return "ok"


@app.get("/users/{name}")
def user(request: Request, name):
    return templates.TemplateResponse("user.html", {"request": request, "name": name})


@app.get("/search", response_class=HTMLResponse)
def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
def search(request: Request, conn: sqlite3.Connection = Depends(get_db), product_name=Form()):
    vuln_search = "select id, name, available, image from chocolate where name=\"{}\"".format(product_name)
    chocolate_info = conn.execute(vuln_search).fetchone()
    return templates.TemplateResponse("items.html", {"request": request, "info": chocolate_info})


@app.get("/change_passwd", response_class=HTMLResponse)
def change(request: Request):
    return templates.TemplateResponse("change_passwd.html", {"request": request})


""""" @app.post("/change_passwd", response_class=HTMLResponse)
def change(request: Request, message: Optional[str] = None, old_passwd: str = Form(...), new_passwd: str = Form(...),
           conn: sqlite3.Connection = Depends(get_db)):
    request.session.
    return templates.TemplateResponse("change_passwd.html", {"request": request, "message": message}) """
