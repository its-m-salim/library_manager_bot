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



# async def borrow(user_id, book_id, due_date):
#     try:
#         conn = await connection_db()
#         await conn.execute("""
#         insert into borrows(user_id, book_id, borrowed_at, due_date) values
#             ($1, $2, $3)
# """, user_id, book_id, due_date)
#         return True
#     except Exception as error:
#         print(f"{type(error)}: {error} sb.py")     
#     finally:
#         await conn.close()   


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



async def is_active(b_id):
    try:
        conn = await connection_db()
        book = await conn.fetchrow("""
        select * from books 
        where id = $1
""", int(b_id))

        return book
    except Exception as error:
        print(f"{type(error)}: {error} con.py")     
    finally:
        await conn.close()   




async def borrow_book(b_id, tg_id):

    try:
        conn = await connection_db()
        status = await conn.execute("""
        update books 
        set is_available = False
        where id = $1 and is_available = True;

""", int(b_id))
        
        if status == "UPDATE 1":
            await conn.execute("""
        insert into borrows(user_id, book_id) values
            ($1, $2)
""", str(tg_id), int(b_id))
            return True
        else:
            return False
    except Exception as error:
        print(f"{type(error)}: {error} sbb.py")     
    finally:
        await conn.close()   






async def return_book(b_id, tg_id):

    try:
        conn = await connection_db()
        status = await conn.execute("""
        update books 
        set is_available = true
        where id = $1 and is_available = false;

""", int(b_id))
        
        if status == "UPDATE 1":
            await conn.execute("""
            update borrows
            set returned_at = now()
            where user_id = $1 and book_id = $2
""", str(tg_id), int(b_id))
            return True
        else:
            return False
    except Exception as error:
        print(f"{type(error)}: {error} srb.py")     
    finally:
        await conn.close()   









async def my_books(tg_id):
    try:
        conn = await connection_db()
        books = await conn.fetch("""
select books.title as title, books.author as author, borrows.borrowed_at as bat from borrows
join books on books.id = borrows.book_id
where borrows.user_id = $1 and returned_at is null
""", str(tg_id))
        return books
    except Exception as error:
        print(f"{type(error)}: {error} smb.py")     
    finally:
        await conn.close()   