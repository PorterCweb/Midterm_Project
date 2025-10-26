from psycopg_pool import AsyncConnectionPool #使用connection pool


async def getList(conn):
	async with conn.cursor() as cur:
		sql="select * from posts order by id desc;"
		await cur.execute(sql)
		rows = await cur.fetchall()
		return rows

async def getPost(conn, id):
	async with conn.cursor() as cur:
		sql="select id ,title, content, price, filename, status from posts where id=%s;"
		await cur.execute(sql,(id,))
		row = await cur.fetchone()
		return row
	
async def GetProposalFromID(conn, id):
	async with conn.cursor() as cur:
		sql="select id, proposer, quote, question from proposals where id=%s;"
		await cur.execute(sql,(id,))
		rows = await cur.fetchall()
		return rows

async def deletePost(conn, id):
	async with conn.cursor() as cur:
		sql="delete from posts where id=%s;"
		await cur.execute(sql,(id,))
		return True
	
async def modifyPost(conn, title, content, price, id):
	async with conn.cursor() as cur:
		sql = "UPDATE posts SET title = %s, content = %s, price = %s WHERE id = %s"
		await cur.execute(sql,(title, content, price, id))
		return True

async def acceptproposal(conn, id):
	async with conn.cursor() as cur:
		sql = "UPDATE posts SET status = '已有人報價' WHERE id = %s"
		await cur.execute(sql,(id,))
		return True

async def addPost(conn, title, content, price, status,client):
	async with conn.cursor() as cur:
		sql="insert into posts (title, content, price, status, client) values (%s,%s,%s,%s,%s);"
		await cur.execute(sql,(title,content,price,status,client))
		return True

async def setUploadFile(conn, id, filename):
	async with conn.cursor() as cur:
		sql="update posts set filename=%s where id=%s;"
		await cur.execute(sql,(filename,id,))
		return True
	
async def register(conn, username, account, password, role):
	async with conn.cursor() as cur:
		sql = "insert into users (username, account, password, role) values (%s,%s,%s,%s);"
		await cur.execute(sql,(username, account, password, role))
		return True

async def getUsers(conn, account):
	async with conn.cursor() as cur:
		sql = "SELECT * FROM users Where account = %s"
		await cur.execute(sql,(account,))
		row = await cur.fetchone()
		return row
	

		





