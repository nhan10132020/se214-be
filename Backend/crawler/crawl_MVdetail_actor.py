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

response = supabase.table("movies").select("movie_id").is_("movie_detail_id",None).execute()

count = 1

for movie in response.data:
    movie_id = movie["movie_id"]
    
    print(f"Movie: {count}")
    count+=1
        
    # Call tmdb details endpoint
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=videos%2Ccredits&language=en-US'
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmOTI3YTY1YzBhMjZmODQ0MDUwOTgyYjhhZDY2NDViYSIsIm5iZiI6MTczMTU2ODYzMi4xODc4NDgzLCJzdWIiOiI2NzM0MDAyZDljMWEyMzhkOGE5ZDJhMmIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.Y1hCi9KkCfidLu2n25c8Y_SSiyQePG4vQEI3x_28bKw',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            # Insert movie details
            try:
                supabase.table("movie_details").insert({
                "movie_detail_id": data["id"],
                "homepage": data["homepage"],
                "budget": data["budget"],
                "tagline": data["tagline"],
                "revenue": data["revenue"],
                "runtime": data["runtime"],
                "spoken_language": [language["english_name"] for language in data["spoken_languages"]],
                "status": data["status"],
                "production_countries": [country["name"] for country in data["production_countries"]],
                "production_companies": [company["name"] for company in data["production_companies"]],
                "video_url": data["videos"]["results"][0]["key"] if data["videos"]["results"] else None
                }).execute()
            except Exception as e:
                print("The movie details has been inserted, But do not updated in movies table")
                
            # Update FK movie_detail_id in movies table
            supabase.table("movies").update({
                "movie_detail_id": data["id"]
            }).eq("movie_id", movie_id).execute()
            
            # Insert actors: max 5 actors in 1 movie, if don't have actor in DB
            for actor in data["credits"]["cast"][:5]:
                actor_id = actor["id"]
                actor_response = supabase.table("actors").select("actor_id").eq("actor_id", actor_id).execute()
                if not actor_response.data:
                    supabase.table("actors").insert({
                        "actor_id": actor["id"],
                        "known_for_department": actor["known_for_department"],
                        "name": actor["name"],
                        "original_name": actor["original_name"],
                        "popularity": actor["popularity"],
                        "profile_path": actor["profile_path"],
                        "gender": actor["gender"]
                    }).execute()

                # Link movie_id and actor_id in movie_has_actor table
                supabase.table("movie_has_actor").insert({
                    "movie_id": movie_id,
                    "actor_id": actor_id,
                    "character": actor["character"]
                }).execute()
        except Exception as e:
            print(e)
            print(f"Fix forgot to insert video_url for movie_id: {movie_id}")
            supabase.table("movie_details").update({
                "video_url": data["videos"]["results"][0]["key"] if data["videos"]["results"] else None
            }).eq("movie_detail_id", movie_id).execute()
        
    else:
        print(f"Request failed with status code: {response.status_code}")
    

print("Done !!!")