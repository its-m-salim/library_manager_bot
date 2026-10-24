from connection import*



async def create_user(username, full_name, tg_id):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into users(username, full_name, telegram_id) values
            ($1, $2, $3)
""", username, full_name, str(tg_id))
        return True
    except Exception as error:
        print(f"{type(error)}: {error} su.py")     
    finally:
        await conn.close()   



async def borrow(user_id, book_id, due_date):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into borrows(user_id, book_id, borrowed_at, due_date) values
            ($1, $2, $3)
""", user_id, book_id, due_date)
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sb.py")     
    finally:
        await conn.close()   


async def profile(tg_id):
    try:
        conn = await connection_db()
        user = await conn.fetchrow("""
        select * from users where telegram_id = $1
""", str(tg_id))
        return user
    except Exception as error:
        print(f"{type(error)}: {error} sp.py")    
        return False 
    finally:
        await conn.close()   


async def add_books(title, author):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into books(title, author) values
                ($1, $2)
    """, title, author )
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sab.py")    
        return False 
    finally:
        await conn.close()   


async def active_books():
    try:
        conn = await connection_db()
        books = await conn.fetch("""
        select * from books 
        where is_available = true
""")
        return books
    except Exception as error:
        print(f"{type(error)}: {error} s_acb.py")     
    finally:
        await conn.close()   