import os
from supabase import create_client, Client
from crawler import crawler
import requests
from dotenv import load_dotenv
import time

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

count = 1

for page in range(1, 101):
    print(f"Fetching page {page}")
    url = f'https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={page}'
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmOTI3YTY1YzBhMjZmODQ0MDUwOTgyYjhhZDY2NDViYSIsIm5iZiI6MTczMTU2ODYzMi4xODc4NDgzLCJzdWIiOiI2NzM0MDAyZDljMWEyMzhkOGE5ZDJhMmIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.Y1hCi9KkCfidLu2n25c8Y_SSiyQePG4vQEI3x_28bKw',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        movies = data['results']
        for movie in movies:
            print(f"movie: {count}")
            count+=1
            try:
                supabase.table("movies").insert({
                "movie_id": movie["id"],
                "adult": movie["adult"],
                "original_language": movie["original_language"],
                "original_title": movie["original_title"],
                "overview": movie["overview"],
                "popularity": movie["popularity"],
                "backdrop_path": movie["backdrop_path"],
                "poster_path": movie["poster_path"],
                "release_date": movie["release_date"],
                "title": movie["title"],
                "vote_average": movie["vote_average"],
                "vote_count": movie["vote_count"]
                }).execute()
                
                for genre_id in movie["genre_ids"]:
                    supabase.table("movie_has_genred").insert({
                        "movie_id": movie["id"],
                        "genre_id": genre_id
                    }).execute()
            except Exception as e:
                print(f"An error occurred: {e}")
        time.sleep(1)
    else:
        print(f"Request failed with status code: {response.status_code}")


