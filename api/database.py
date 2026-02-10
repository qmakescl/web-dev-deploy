import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings

class Database:
    def __init__(self):
        self.conn_url = settings.DATABASE_URL
    
    def get_connection(self):
        try:
            return psycopg2.connect(self.conn_url, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"\n[!] 데이터베이스 연결 실패: {e}")
            print("[!] .env 파일의 DATABASE_URL이 올바른지 확인해주세요.\n")
            raise e


    def execute_ddl(self):
        ddl_queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                img_url VARCHAR(500),
                content TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                comment TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS likes (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(post_id, user_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (post_id, tag_id)
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);",
            "CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id);"
        ]
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                for query in ddl_queries:
                    cur.execute(query)
            conn.commit()
            print("Database tables and indexes created successfully.")
        except Exception as e:
            conn.rollback()
            print(f"Error creating database tables: {e}")
            raise e
        finally:
            conn.close()

db = Database()
