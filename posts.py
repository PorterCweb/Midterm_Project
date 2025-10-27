from psycopg_pool import AsyncConnectionPool #使用connection pool


async def getList(conn):
	async with conn.cursor() as cur:
		sql="select * from posts order by id desc;"
		await cur.execute(sql)
		rows = await cur.fetchall()
		return rows

async def getPostFromID(conn, id):
	async with conn.cursor() as cur:
		sql="select * from posts where id = %s;"
		await cur.execute(sql,(id,))
		row = await cur.fetchone()
		return row

async def getProposals(conn):
	async with conn.cursor() as cur:
		sql = "SELECT * FROM proposals"
		await cur.execute(sql)
		rows = await cur.fetchall()
		return rows
	
async def getProposalFromID(conn, id):
	async with conn.cursor() as cur:
		sql="select * from proposals where id = %s;"
		await cur.execute(sql,(id,))
		rows = await cur.fetchall()
		return rows

async def deletePost(conn, id):
	async with conn.cursor() as cur:
		sql="delete from posts where id = %s;"
		await cur.execute(sql,(id,))
		return True
	
async def modifyPost(conn, title, content, expectedquotation, id):
	async with conn.cursor() as cur:
		sql = "UPDATE posts SET title = %s, content = %s, expectedquotation = %s WHERE id = %s"
		await cur.execute(sql,(title, content, expectedquotation, id,))
		return True

async def acceptProposal(conn, id, proposer, quote, status):
	async with conn.cursor() as cur:
		sql = "UPDATE posts SET status = %s, contractor = %s, finalquotation = %s WHERE id = %s"
		await cur.execute(sql,(status, proposer, quote, id,))
		return True

async def addPost(conn, title, content, expectedquotation, status, client):
	async with conn.cursor() as cur:
		sql = "insert into posts (title, content, expectedquotation, status, client) values (%s,%s,%s,%s,%s);"
		await cur.execute(sql,(title,content,expectedquotation,status,client))
		return True

async def setUploadFile(conn, id, filename, status):
	async with conn.cursor() as cur:
		sql="update posts set filename=%s, status=%s where id=%s;"
		await cur.execute(sql,(filename, status, id,))
		return True
	
async def register(conn, username, account, password, role):
	async with conn.cursor() as cur:
		sql = "insert into users (username, account, password, role) values (%s,%s,%s,%s);"
		await cur.execute(sql,(username, account, password, role,))
		return True

async def getUsers(conn, account):
	async with conn.cursor() as cur:
		sql = "SELECT * FROM users Where account = %s"
		await cur.execute(sql,(account,))
		row = await cur.fetchone()
		return row
	
async def submitProposal(conn, id, proposer, quote, message):
	async with conn.cursor() as cur:
		sql = "insert into proposals (id, proposer, quote, message) values (%s,%s,%s,%s)"
		await cur.execute(sql,(id,proposer,quote,message,))
		return True
async def acceptSubmission(conn, id, status):
	async with conn.cursor() as cur:
		sql = "UPDATE posts SET status = %s WHERE id = %s"
		await cur.execute(sql,(status,id,))
		return True