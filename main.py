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
    user = await posts.getUsers(conn,account)
    # 驗證使用者
    if user["account"] == account and user["password"] == password:
        # 登入成功，將使用者資訊存入 Session
        request.session["user"] = user["username"]
        request.session["account"] = user["account"]
        request.session["role"] = user["role"]
        # 判別使用者身分及導入至不同介面
        if request.session["role"] == "client":
            postLists = await posts.getList(conn)
            return templates.TemplateResponse("clientForm.html", {"request": request, "user": user, "postLists": postLists})
        else:
            postLists = await posts.getList(conn)
            return templates.TemplateResponse("contractorForm.html", {"request": request, "user": user, "postLists": postLists})
    else:
        # 登入失敗
        return HTMLResponse(
			"帳號或密碼錯誤 <a href='/loginForm.html'> 重新登入</a>", 
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
    return RedirectResponse(url="/loginForm.html")

@app.get("/file/{p:path}")
async def getPath(p: str):
    return {"yourPath": p}

@app.get("/url/")
async def getParam(a: int, b: int=5, c: str | None=None):
    return {"Aa": a, "Bb": b, "Cc": c}

@app.get("/jump")
def redirect():
    return RedirectResponse(url="/", status_code=302)

@app.get("/postDetail/{id}")
async def readPost(request: Request, id: int, conn=Depends(getDB)):
    postDetail = await posts.getPostFromID(conn, id)
    proposals = await posts.getProposals(conn)
    user = {
        "username": request.session.get("user"),
        "account": request.session.get("account"),
        "role": request.session.get("role")
    }
    return templates.TemplateResponse("postDetail.html", {"request": request, "user": user, "postdetail": postDetail, "proposals": proposals})

@app.get("/delete/{id}")
async def delPost(request: Request, id: int, conn=Depends(getDB)):
    await posts.deletePost(conn, id)
    return RedirectResponse(url="/homepage", status_code=302)

@app.get("/modifyPost/{id}.html")
async def modify_get_form(request: Request, id: int, conn=Depends(getDB)):
    postDetail = await posts.getPostFromID(conn, id)
    return templates.TemplateResponse("modifyPost.html", {
        "request": request,
        "postdetail": postDetail,
    })

@app.post("/modifyPost/{id}")
async def modify_Post(
    request: Request,
    id: int,
    title: str=Form(...),
    content: str=Form(...),
    expectedquotation: str=Form(...),
    conn=Depends(getDB)
):
    await posts.modifyPost(conn, title, content, expectedquotation, id)
    return RedirectResponse(url="/homepage", status_code=302)

@app.get("/proposalForm/{id}.html")
async def postStat(request: Request, id: int, conn=Depends(getDB)):
    proposal = await posts.getProposalFromID(conn, id)
    postdetail = await posts.getPostFromID(conn,id)
    user = {
        "username": request.session.get("user"),
        "account": request.session.get("account"),
        "role": request.session.get("role")
    }
    return templates.TemplateResponse("proposalForm.html", {
        "request": request, 
        "proposal": proposal,
        "postdetail": postdetail,
        "user": user
    })

@app.get("/acceptProposal/{id}/{proposer}/{quote}")
async def acceptprops(request: Request, id: int, proposer: str, quote: int, conn=Depends(getDB)):
    status = 'assigned'
    await posts.acceptProposal(conn, id, proposer, quote, status)
    return RedirectResponse(url="/homepage", status_code=302)

@app.post("/addPost")
async def addPost(
    request: Request,
    title: str=Form(...),
    content: str=Form(...),
    expectedquotation: str=Form(...),
    conn=Depends(getDB)
):
    status = "open"
    client = request.session.get("user")
    await posts.addPost(conn, title, content, expectedquotation, status, client)
    return RedirectResponse(url="/homepage", status_code=302)

@app.get("/homepage")
async def acceptprop(request: Request, conn=Depends(getDB)):
    user = {
            "username": request.session.get("user"),
            "account": request.session.get("account"),
            "role": request.session.get("role")
        }
    if user["role"] == "client":
        postLists = await posts.getList(conn)
        return templates.TemplateResponse("clientForm.html", {"request": request, "user": user, "postLists": postLists})
    else:
        postLists = await posts.getList(conn)
        return templates.TemplateResponse("contractorForm.html", {"request": request, "user": user, "postLists": postLists})

@app.post("/submitProposal/{id}")
async def submitprop(
    request:Request, 
    id: int, 
    quote: int = Form(...),  # 由於沒有 Form(...) 標記，FastAPI 預設會從 URL 的 query string 中尋找這些參數，而不是從表單數據中。
    message: str = Form(...),  # 由於沒有 Form(...) 標記，FastAPI 預設會從 URL 的 query string 中尋找這些參數，而不是從表單數據中。
    conn =Depends(getDB)
):
    proposer = request.session.get("user")
    await posts.submitProposal(conn, id, proposer, quote, message)
    return RedirectResponse(url=f"/postDetail/{id}", status_code=302)

@app.get("/acceptSubmission/{id}")
async def acceptsubmit(request:Request, id: int, conn=Depends(getDB)):
    status = 'completed'
    await posts.acceptSubmission(conn,id,status)
    return RedirectResponse(url=f"/postDetail/{id}", status_code=302)

@app.get("/rejectSubmission/{id}")
async def rejectSubmit(request:Request, id:int, conn=Depends(getDB)):
    status = 'rejected'
    await posts.rejectSubmission(conn, id, status)
    return RedirectResponse(url=f"/postDetail/{id}", status_code=302)

@app.get("/myProposals")
async def myProposals(request: Request, conn=Depends(getDB)):
    user = {
        "username": request.session.get("user"),
        "account": request.session.get("account"),
        "role": request.session.get("role")
    }
    # 獲取歷史專案
    historyProjects = await posts.getHistoryProjects(conn, user["username"], user["role"])
    return templates.TemplateResponse("historyProjects.html", {
        "request": request, 
        "user": user, 
        "historyProjects": historyProjects
    })


app.mount("/", StaticFiles(directory="www"))