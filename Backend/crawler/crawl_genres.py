import os
from supabase import create_client, Client
from crawler import crawler
import requests
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

url = 'https://api.themoviedb.org/3/genre/movie/list?language=en'
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmOTI3YTY1YzBhMjZmODQ0MDUwOTgyYjhhZDY2NDViYSIsIm5iZiI6MTczMTU2ODYzMi4xODc4NDgzLCJzdWIiOiI2NzM0MDAyZDljMWEyMzhkOGE5ZDJhMmIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.Y1hCi9KkCfidLu2n25c8Y_SSiyQePG4vQEI3x_28bKw',
    'accept': 'application/json'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    genres = data['genres']
    for genre in genres:
        supabase.table("genres").insert({"genre_id": genre["id"], "name": genre["name"]}).execute()
else:
    print(f"Request failed with status code: {response.status_code}")


