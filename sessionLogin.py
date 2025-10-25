from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import HTTPException, status
from fastapi.staticfiles import StaticFiles
from db import getDB  # 引入資料庫連接
import posts
app = FastAPI()

from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production",
    max_age=None,
    same_site="lax",
    https_only=False,
)

# 登入檢查函數
def get_current_user(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

@app.get("/")
async def home(request: Request, user: str = Depends(get_current_user)):
    return {"message": f"Welcome back, {user}!"}

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/loginForm.html")

# 修改後的登入路由 - 使用資料庫驗證
@app.post("/login")
async def login(
    request: Request,
    account: str = Form(...),
    password: str = Form(...),
    conn = Depends(getDB)  # 注入資料庫連接
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

@app.post("/register")
async def register(
	request:Request,
	username:str=Form(...),
	account:str=Form(...),
	password:str=Form(...),
	role:str=Form(...),
	conn=Depends(getDB)
):
		await posts.register(conn, username, account, password, role)
		return RedirectResponse(url="./loginForm.html", status_code=302)

app.mount("/", StaticFiles(directory="www"))