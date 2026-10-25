from dotenv import load_dotenv
import asyncpg
import os
load_dotenv()
p_db = os.getenv("PASSWORD_DB")


async def connection_db():
    try:
        conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="salim",
        database="library",
        password=p_db
)
        return conn
    except Exception as error:
        print(f"{type(error)}: {error} conn.py")


async def create_tables():
    try:
        conn = await connection_db()
        await conn.execute("""
        create table if not exists books(
            id serial primary key,
            title varchar(100),
            author varchar(200),
            added_at timestamp default now(),
            borrows_count int default 0,
            read_url text,
            is_available bool default true,
            is_active bool default true
        );

        create table if not exists users(
            id serial primary key,
            username varchar(200),
            full_name varchar(200),
            telegram_id varchar(200) unique,
            total_books int default 0,
            created_at timestamp default now(),
            is_active bool default true
        );
        
        create table if not exists borrows(
            id serial primary key,
            user_id varchar(200) references users(telegram_id),
            book_id int references books(id),
            borrowed_at timestamp default now(),
            due_date timestamp default now() + interval'14 days',
            returned_at timestamp ,
            is_active bool default true

        )
""")
        print("Tables created successfuly!")
    except Exception as error:
        print(f"{type(error)}: {error} con.py")     
    finally:
        await conn.close()   

