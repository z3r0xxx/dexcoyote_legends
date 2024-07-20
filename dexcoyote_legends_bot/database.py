import os
import time
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def insert_user(user_id: int, invited_by: int = None, language: str = None, is_premium = 0):
    """ Insert a new user into the users table """

    try:
        with psycopg2.connect(str(os.getenv("DATABASE_CONNECTION_STRING"))) as conn:
            with  conn.cursor() as cur:
                if language is None and invited_by is None:
                    cur.execute("INSERT INTO users(user_id, is_premium, created_at) VALUES(%s, %s, %s);", (user_id, is_premium, int(time.time()),))
                    conn.commit()
                elif language is None:
                    cur.execute("INSERT INTO users(user_id, invited_by, is_premium, created_at) VALUES(%s, %s, %s, %s);", (user_id, invited_by, is_premium, int(time.time()),))
                    conn.commit()
                elif invited_by is None:
                    cur.execute("INSERT INTO users(user_id, language, is_premium, created_at) VALUES(%s, %s, %s, %s);", (user_id, language, is_premium, int(time.time()),))
                    conn.commit()
                else:
                    cur.execute("INSERT INTO users(user_id, language, invited_by, is_premium, created_at) VALUES(%s, %s, %s, %s);", (user_id, language, invited_by, is_premium, int(time.time()),))
                    conn.commit()
                
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def check_user_exists(user_id: int) -> bool:
    """ Check if a user exists in the users table by user_id """

    try:
        with psycopg2.connect(str(os.getenv("DATABASE_CONNECTION_STRING"))) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE user_id = %s;", (user_id,))
                user = cur.fetchone()
                return user is not None
                
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False