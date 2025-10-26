# main.py
from fastapi import FastAPI, Depends, Request, Form, HTTPException
from db import getDB
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# 加入 Session 中介軟體
from starlette.middleware.sessions import SessionMiddleware

templates = Jinja2Templates(directory="templates")

from routes.upload import router as upload_router
from routes.dbQuery import router as db_router
import posts

# Include the router
app = FastAPI()

# ===== 新增：加入 Session 中介軟體 =====
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production-please",  # 記得改成更安全的密鑰
    max_age=None,  # Session 不過期
    same_site="lax",
    https_only=False,  # 正式環境改為 True
)

# prefix will be prepended before the route
app.include_router(upload_router, prefix="/api") 
app.include_router(db_router, prefix="/api")

# ===== 新增：登入檢查函數 =====
def get_current_user(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

# ===== 新增：登入路由 =====
@app.post("/login")
async def login(
    request: Request,
    account: str = Form(...),
    password: str = Form(...),
    conn = Depends(getDB)
):
    # 從資料庫查詢使用者
    async with conn.cursor() as cur:
        sql = "SELECT username, account, password, role FROM users WHERE account = %s"
        await cur.execute(sql, (account,))
        user = await cur.fetchone()
    
    # 驗證使用者
    if user and user["password"] == password:
        # 登入成功，將使用者資訊存入 Session
        request.session["user"] = user["username"]
        request.session["account"] = user["account"]
        request.session["role"] = user["role"]
        return RedirectResponse(url="/", status_code=302)
    
    # 登入失敗
    return HTMLResponse(
        "帳號或密碼錯誤 <a href='/loginForm.html'>重新登入</a>", 
        status_code=401
    )

# ===== 新增：註冊路由 =====
@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    account: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    conn = Depends(getDB)
):
    await posts.register(conn, username, account, password, role)
    return RedirectResponse(url="/loginForm.html", status_code=302)

# ===== 新增：登出路由 =====
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/loginForm.html")

# ===== 原有路由（可選擇性加入登入驗證） =====
@app.get("/")
async def root(request: Request, conn=Depends(getDB)):
    # 可選：加入登入驗證 user: str = Depends(get_current_user)
    myList = await posts.getList(conn)
    return templates.TemplateResponse("postList.html", {"request": request, "items": myList})

@app.get("/file/{p:path}")
async def getPath(p: str):
    return {"yourPath": p}

@app.get("/url/")
async def getParam(a: int, b: int=5, c: str | None=None):
    return {"Aa": a, "Bb": b, "Cc": c}

@app.get("/jump")
def redirect():
    return RedirectResponse(url="/", status_code=302)

@app.get("/read/{id}")
async def readPost(request: Request, id: int, conn=Depends(getDB)):
    postDetail = await posts.getPost(conn, id)
    return templates.TemplateResponse("postDetail.html", {"request": request, "post": postDetail})

@app.get("/readProposer/{id}")
async def readProposer(request: Request, id: int, conn=Depends(getDB)):
    postDetail = await posts.GetProposalFromID(conn, id)
    return templates.TemplateResponse("proposallist.html", {"request": request, "post": postDetail})

@app.get("/delete/{id}")
async def delPost(request: Request, id: int, conn=Depends(getDB)):
    postDetail = await posts.deletePost(conn, id)
    return RedirectResponse(url="/", status_code=302)

@app.get("/modifyPost/{id}.html")
async def modify_get_form(request: Request, id: int, conn=Depends(getDB)):
    post = await posts.getPost(conn, id)
    return templates.TemplateResponse("modifyPost.html", {
        "request": request,
        "post": post,
    })

@app.post("/modifyPost/{id}")
async def modify_Post(
    request: Request,
    id: int,
    title: str=Form(...),
    content: str=Form(...),
    price: str=Form(...),
    conn=Depends(getDB)
):
    postDetail = await posts.modifyPost(conn, title, content, price, id)
    return RedirectResponse(url="/", status_code=302)

@app.get("/proposallist/{id}.html")
async def postStat(request: Request, id: int, conn=Depends(getDB)):
    proposal = await posts.GetProposalFromID(conn, id)
    status = await posts.postStatus(conn, id)
    return templates.TemplateResponse("proposallist.html", {
        "request": request,
        "proposal": proposal,
        "status": status
    })

@app.get("/acceptproposal/{id}")
async def acceptprops(request: Request, id: int, conn=Depends(getDB)):
    await posts.acceptproposal(conn, id)
    return RedirectResponse(url="/", status_code=302)

@app.post("/addPost")
async def addPost(
    request: Request,
    title: str=Form(...),
    content: str=Form(...),
    price: str=Form(...),
    conn=Depends(getDB)
):
    postDetail = await posts.addPost(conn, title, content, price)
    return RedirectResponse(url="/", status_code=302)

app.mount("/", StaticFiles(directory="www"))