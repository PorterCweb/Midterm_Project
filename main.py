# main.py
from fastapi import FastAPI, Depends, Request, Form
from db import getDB
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,RedirectResponse


from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

from routes.upload import router as upload_router
from routes.dbQuery import router as db_router
import posts

# Include the router
app = FastAPI()
#prefix will be prepended before the route
app.include_router(upload_router, prefix="/api") 
app.include_router(db_router, prefix="/api")

@app.get("/")
async def root(request:Request,conn=Depends(getDB)):
	#產生回應內容的程式
	myList= await posts.getList(conn)
	return templates.TemplateResponse("postList.html", {"request":request,"items": myList})

	#return myList
	#return HTMLResponse(content="Hello World", status_code=200)

@app.get("/file/{p:path}")  #http://localhost/file/a/b/c/123.jpg
async def getPath(p: str):  #p  “a/b/c/123.jpg”
	return {"yourPath": p}

@app.get("/url/")  #http://localhost/url/?a=2&d=999
async def getParam(a: int, b:int=5, c:str | None=None): #注意有預設值與沒有的差異
	#a:必須要提供(不然報錯)
	#b:網址參數沒提供時，以預設值0帶入
	#c:可有可無，未提供時  None/null
	#d:忽略
	return {"Aa": a, "Bb":b , "Cc":c }

@app.get("/jump")
def redirect():
		return RedirectResponse(url="/", status_code=302)

@app.get("/read/{id}")
async def readPost(request:Request, id:int,conn=Depends(getDB)):
	postDetail = await posts.getPost(conn,id)
	return templates.TemplateResponse("postDetail.html", {"request":request,"post": postDetail})


# 報價人
@app.get("/readProposer/{id}")
async def readProposer(request:Request, id:int,conn=Depends(getDB)):
	postDetail = await posts.GetProposalFromID(conn,id)
	return templates.TemplateResponse("proposallist.html", {"request":request,"post": postDetail})

@app.get("/delete/{id}")
async def delPost(request:Request, id:int,conn=Depends(getDB)):
	postDetail = await posts.deletePost(conn,id)
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
	request:Request,
	id:int,
	title: str=Form(...),
	content:str=Form(...),
	price: str=Form(...),
	conn=Depends(getDB)
	):
	postDetail = await posts.modifyPost(conn,title,content,price,id)
	return RedirectResponse(url="/", status_code=302)

@app.get("/proposallist/{id}.html")
async def propsform(request: Request, id: int, conn=Depends(getDB)):
	proposal = await posts.GetProposalFromID(conn, id)
	specificpost = await posts.getSpecificPost(conn,id)
	return templates.TemplateResponse("proposallist.html", {
        "request": request,
		"proposal": proposal,
        "specificpost": specificpost
		})


@app.get("/acceptproposal/{id}")
async def acceptprops(request:Request, id:int, conn=Depends(getDB)):
	await posts.acceptproposal(conn, id)
	return RedirectResponse(url="/", status_code=302)

@app.post("/addPost")
async def addPost(
	request:Request,
	title: str=Form(...),
	content:str=Form(...),
	price: str=Form(...),
	conn=Depends(getDB)
):
	postDetail = await posts.addPost(conn,title,content,price)
	return RedirectResponse(url="/", status_code=302)




app.mount("/", StaticFiles(directory="www"))