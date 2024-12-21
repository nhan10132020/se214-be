from typing import Union
from supabase import create_client, Client
from fastapi import FastAPI,Depends, HTTPException, status
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()

# config cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1420

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=120))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer()

class UserCreate(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_user_by_username(username: str):
    response = supabase.from_("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None

def create_user(user: UserCreate, hashed_password: str):
    try:
        response = supabase.table("users").insert({
            "username": user.username,
            "hashed_password": hashed_password,
            "email": user.email,
            "role_id": 1,
        }).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error when create user: {e}")

@app.post("/users/register", response_model=Token)
async def register_user(user: UserCreate):
    if len(user.username) < 5 or len(user.username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 5 and 20 characters")
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Password and confirm password do not match")
    # check email is valid type
    if not "@" in user.email:
        raise HTTPException(status_code=400, detail="Invalid email")
    hashed_password = get_password_hash(user.password)
    create_user(user, hashed_password)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/users/login", response_model=Token)
async def login_for_access_token(user_login: UserLogin):
    user = get_user_by_username(user_login.username)
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


def get_user_role(user_id: int):
    response = supabase.from_("roles").select("name").eq("role_id", user_id).execute()
    return response.data[0]["name"] if response.data else None

def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_by_username(username)
        if user is None:
            raise credentials_exception
        return user
    except jwt.PyJWTError as e:
        raise credentials_exception


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ----------------- Authenticate JWT user ----------------- #

# Get all movies 
from fastapi import Request
@app.get("/movies")
def get_movies(page: int = 1):
    response = supabase.table("movies").select("*").range((page-1)*10, (page*10)-1).execute()
    return response.data

# Get movie detail by movie id
@app.get("/movies/{movie_id}/detail")
def get_movie_detail_by_movie_id(movie_id: int):
    response = supabase.table("movie_details").select("*").eq("movie_detail_id", movie_id).execute()
    return response.data

# Get all genres by movie id
@app.get("/movies/{movie_id}/genres")
def get_all_genres_by_movie_id(movie_id: int):
    response = supabase.table("movie_has_genred").select(
        "genres(*)"
    ).eq("movie_id", movie_id).execute()
    
    return response.data

# Get all actors by movie id
@app.get("/movies/{movie_id}/actors")
def get_all_actors_by_movie_id(movie_id: int):
    response = supabase.table("movie_has_actor").select(
        "character, actors(*)"
    ).eq("movie_id", movie_id).execute()
    
    return response.data

# Get all comments for movie id
@app.get("movies/{movie_id}/comments")
def get_all_comments_by_movie_id(movie_id: int):
    response = supabase.table("comments").select(
        "users(*), content"
    ).eq("movie_id", movie_id).execute()
    
    return response.data

# Get all actors
@app.get("/actors")
def get_all_actors(page: int = 1):
    response = supabase.table("actors").select("*").range((page-1)*10, (page*10)-1).execute()
    return response.data

# Get all movies for that actor
@app.get("/actors/{actor_id}/movies")
def get_all_movies_by_actor_id(actor_id: int, page: int = 1):
    response = supabase.table("movie_has_actor").select(
      "character, movies(*)"  
    ).eq("actor_id", actor_id).range((page-1)*10, (page*10)-1).execute()
    
    return response.data

# Get all genres
@app.get("/genres")
def get_all_genres():
    response = supabase.table("genres").select("*").execute()
    return response.data

# Get movies by genre
@app.get("/genres/{genre_id}/movies")
def get_all_movies_by_genre_id(genre_id: int, page: int = 1):
    response = supabase.table("movie_has_genred").select(
        "movies(*)"
    ).eq("genre_id", genre_id).range((page-1)*10, (page*10)-1).execute()
    
    return response.data


# Add to favorite
@app.post("/users/movies/{movie_id}/favorite")
def add_to_favorite(movie_id: int, current_user: dict = Depends(get_current_user)):
    response = supabase.table("favourite_list").insert({
        "user_id": current_user["user_id"],
        "movie_id": movie_id
    }).execute()
    return response.data

# Delete from favorite
@app.delete("/users/movies/{movie_id}/favorite")
def delete_from_favorite(movie_id: int, current_user: dict = Depends(get_current_user)):
    response = supabase.table("favourite_list").delete().eq("user_id", current_user["user_id"]).eq("movie_id", movie_id).execute()
    return response.data

# Get all favorite movies of the user
@app.get("/users/movies/favorite")
def get_all_favorite_movies(current_user: dict = Depends(get_current_user)):
    response = supabase.table("favourite_list").select(
        "movies(*)"
    ).eq("user_id", current_user["user_id"]).execute()
    
    return response.data

# User Comment for movie
@app.post("/users/movies/{movie_id}/comment")
def user_comment_for_movie(movie_id: int, comment: str, current_user: dict = Depends(get_current_user)):
    response = supabase.table("comments").insert({
        "user_id": current_user["user_id"],
        "movie_id": movie_id,
        "content": comment
    }).execute()
    return response.data

# User Updated their comment for movie
@app.patch("/users/movies/{movie_id}/comment")
def user_update_comment_for_movie(movie_id: int, comment: str, current_user: dict = Depends(get_current_user)):
    response = supabase.table("comments").update({
        "content": comment,
        'updated_at': datetime.now()
    }).eq("user_id", current_user["user_id"]).eq("movie_id", movie_id).execute()
    return response.data

# Update User watch history
@app.post("/users/movies/{movie_id}/history/watch")
def update_user_watch_history(movie_id: int, current_user: dict = Depends(get_current_user)):
    response = supabase.table("watch_histories").insert({
        "user_id": current_user["user_id"],
        "movie_id": movie_id
    }).execute()
    return response.data

# Get all user watch history
@app.get("/users/movies/history/watch")
def get_user_watch_history(current_user: dict = Depends(get_current_user)):
    response = supabase.table("watch_histories").select(
        "movies(*)"
    ).eq("user_id", current_user["user_id"]).execute()
    
    return response.data