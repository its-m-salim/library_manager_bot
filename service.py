from connection import*
from datetime import datetime, date


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


async def add_books(title, author, read_url=None):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into books(title, author, read_url) values
                ($1, $2, $3)
    """, title, author, read_url)
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sab.py")    
        return False 
    finally:
        await conn.close()   


async def active_books():
    try:
        conn = await connection_db()
        unvailable = await conn.fetchrow("select count(*) as count from books where is_available = false")
        books = await conn.fetch("""
        select * from books 
        where is_available = true
        order by id
""")
        return unvailable, books
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






async def get_borrowed(b_id, tg_id):
    try:
        conn = await connection_db()
        br = await conn.fetchrow("""
        select * from borrows
        where book_id = $1
        and returned_at is null
""", int(b_id))
        if not br:
            return "free"
        elif br["user_id"] != str(tg_id):
            return "other_user"
        return "ok"
    except Exception as error:
        print(f"{type(error)}: {error} sgb.py")     
    finally:
        await conn.close()   










async def borrow_book(b_id, tg_id):

    try:

        conn = await connection_db()
        await conn.fetchrow("""
        insert into borrows(user_id, book_id) values
            ($1, $2)
        """, str(tg_id), int(b_id))

        
        status = await conn.fetchrow("""
        update books 
        set is_available = False
        where id = $1 and is_available = True
        returning id

""", int(b_id))
        if not status:
            return False
                
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sbb.py") 
        return False    
    finally:
        await conn.close()   




async def bestsellers():
    try:
        conn = await connection_db()
        best  = await conn.fetchrow("""
        select id from books
        where borrows_count > 3
        order by borrows_count desc,
        is_available asc, id asc
        limit 1
""")
        return best
    except Exception as error:
        print(f"{type(error)}: {error} sbest.py")     
    finally:
        await conn.close()   










async def return_book(b_id, tg_id):
    try:
        conn = await connection_db()
        status = await conn.fetchrow("""
        update borrows
        set returned_at = now()
        where user_id = $1 and book_id = $2
        and returned_at is null
        returning id
        """, str(tg_id), int(b_id))

        if not status:
            return False
        await conn.execute("""
        update users
        set total_books = total_books + 1
        where telegram_id = $1
""", str(tg_id))
        await conn.execute("""
        update books 
        set is_available = true,
        borrows_count = borrows_count + 1
        where id = $1 and is_available = false""", int(b_id))

        return True
    except Exception as error:
        print(f"{type(error)}: {error} srb.py")    
        return False 
    finally:
        await conn.close()   




async def overdue(tg_id):
    try:
        conn = await connection_db()
        invalid_books = await conn.fetch("""
        select books.id as id,  books.title as title, books.author as author, borrows.borrowed_at as bat from borrows
        join books on books.id = borrows.book_id
        where borrows.user_id = $1 and returned_at is null
        and borrows.borrowed_at < now() - interval'14 days'
""", str(tg_id))
        return invalid_books
    except Exception as error:
        print(f"{type(error)}: {error} sov.py") 
        return False    
    finally:
        await conn.close()   




async def my_books(tg_id):
    try:
        conn = await connection_db()
        books = await conn.fetch("""
select books.id as id,  books.title as title, books.author as author, borrows.borrowed_at as bat, books.read_url from borrows
join books on books.id = borrows.book_id
where borrows.user_id = $1 and returned_at is null
""", str(tg_id))
        return books
    except Exception as error:
        print(f"{type(error)}: {error} smb.py")     
        return False
    finally:
        await conn.close()   




def format_date(created_at):
    today = date.today()

    if created_at.date() == today:
        return created_at.strftime("Сегодня в %H:%M")

    elif (today - created_at.date()).days == 1:
        return created_at.strftime("Вчера в %H:%M")

    return created_at.strftime("%d.%m.%Y в %H:%M")