from fastapi import FastAPI, Form, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Todo:
    def __init__(self, item: str, owner: str):
        self.item = item
        self.owner = owner

todos: List[Todo] = []

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    username = request.cookies.get("username")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "todos": todos,
        "username": username
    })

@app.post("/login")
def login(response: Response, username: str = Form(...)):
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="username", value=username)
    return response

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(key="username")
    return response

@app.post("/create-todo")
def create_todo(request: Request, item: str = Form(...)):
    username = request.cookies.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todos.append(Todo(item=item, owner=username))
    return RedirectResponse("/", status_code=303)

@app.post("/delete-todo/{idx}")
def delete_todo(idx: int, request: Request):
    username = request.cookies.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if idx < 0 or idx >= len(todos):
        raise HTTPException(status_code=404, detail="Todo not found")
    if todos[idx].owner != username:
        raise HTTPException(status_code=403, detail="Permission denied: not owner")
    del todos[idx]
    return RedirectResponse("/", status_code=303)
