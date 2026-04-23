import mysql.connector
import os
from urllib.parse import parse_qs, urlparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MONGO_DB_NAME = os.getenv("MONGODB_INITDB_DATABASE", "blog_db")

mysql_conn = None


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variable d'environnement manquante: {name}")
    return value


def get_mysql_connection():
    global mysql_conn
    if mysql_conn is None or not mysql_conn.is_connected():
        mysql_conn = mysql.connector.connect(
            database=get_required_env("MYSQL_DATABASE"),
            user=get_required_env("MYSQL_USER"),
            password=get_required_env("MYSQL_PASSWORD"),
            port=MYSQL_PORT,
            host=get_required_env("MYSQL_HOST")
        )
    return mysql_conn


def ensure_mongo_auth_source(url: str) -> str:
    """Ajoute authSource=admin si des identifiants sont présents et qu'il manque."""
    parsed = urlparse(url)
    if not parsed.username:
        return url

    query_params = parse_qs(parsed.query)
    if "authSource" in query_params:
        return url

    separator = "&" if parsed.query else "?"
    return f"{url}{separator}authSource=admin"


mongo_url = ensure_mongo_auth_source(
    get_required_env("MONGO_URL")
)
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client.get_database(MONGO_DB_NAME)
posts_collection = mongo_db.posts


def fetch_posts():
    posts = list(posts_collection.find({}, {"_id": 1, "titre": 1, "auteur": 1, "vues": 1}))
    for post in posts:
        post["_id"] = str(post["_id"])
    return posts


def fetch_users():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, pseudo, email FROM utilisateurs")
        return cursor.fetchall()
    finally:
        cursor.close()


def count_mysql_users():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as count FROM utilisateurs")
        return cursor.fetchone()["count"]
    finally:
        cursor.close()


@app.get("/posts")
async def get_posts():
    try:
        posts = fetch_posts()
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {str(e)}")


@app.get("/users")
async def get_users():
    try:
        records = fetch_users()
        return {"utilisateurs": records, "count": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {str(e)}")


@app.get("/health")
async def health_check():
    errors = []
    count_mongo = 0
    count_mysql = 0

    try:
        count_mongo = posts_collection.count_documents({})
        if count_mongo < 1:
            errors.append(f"MongoDB: Collection posts vide ({count_mongo} documents)")
    except Exception as e:
        errors.append(f"MongoDB: {str(e)}")

    try:
        count_mysql = count_mysql_users()
        if count_mysql < 1:
            errors.append(f"MySQL: Table utilisateurs vide ({count_mysql} lignes)")
    except Exception as e:
        errors.append(f"MySQL: {str(e)}")

    if errors:
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "errors": errors})

    return {
        "status": "healthy",
        "mongodb_documents": count_mongo,
        "mysql_users": count_mysql
    }


@app.get("/")
async def root():
    return {
        "message": "Hybrid Stack API",
        "routes": {
            "/posts": "GET - MongoDB articles",
            "/users": "GET - MySQL utilisateurs",
            "/health": "GET - Health check"
        }
    }