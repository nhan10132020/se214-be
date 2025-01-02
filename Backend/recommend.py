from pydantic import BaseModel
from fastapi import FastAPI
import pandas as pd
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from dotenv import load_dotenv
import uvicorn
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# application
app = FastAPI()

# Get data from Supabase
genres = supabase.table('genres').select("*").execute()
movies = supabase.table('movies').select("*,movie_has_genred(genre_id)").execute()


# Convert to DataFrame
genres = pd.DataFrame(genres.data)
genres = genres.rename(columns={'genre_id': 'id'})

movies = pd.DataFrame(movies.data)
movies["movie_has_genred"] = movies["movie_has_genred"].apply(lambda x: [i["genre_id"] for i in x])
movies = movies.rename(columns={'movie_has_genred': 'genre_ids'})

md = movies.drop_duplicates(subset="movie_id").reset_index(drop=True) # processing data
df = movies.drop_duplicates(subset="movie_id").reset_index(drop=True) # original data

# Processing data
md['overview'] = md['overview'].fillna('')
md['overview'] = md['overview'].apply(lambda x: x.split(" "))
genre_dict = dict(zip(genres['id'], genres['name']))
md['genres'] = md['genre_ids'].apply(lambda x: [genre_dict[i] for i in x])
md['soup'] =  md["genres"]*5 + md["overview"] 
md['soup'] = md['soup'].apply(lambda x: ' '.join(x))

# Vectorizer data
count = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=1, stop_words='english')
count_matrix = count.fit_transform(md['soup'])

# Calculate Cosine Similarity
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# Indexing
indices = pd.Series(md.index, index=md['movie_id'])

def filter_movie_ids(movie_ids):
    acpt = [val for val in movie_ids if val in indices]
    if len(acpt) == 0:
        return [indices.sample(n=1).index[0]]
    else:
        return acpt


# Recommendation based on user's favorite movies
def get_recommendations(movie_ids):
    movie_ids = filter_movie_ids(movie_ids)
    recommendations = {}
    row_numbers = [indices.index.get_loc(id) for id in movie_ids]
    for id in movie_ids:
        idx = indices[id] 
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:100]
        sim_scores = [(m, score) for m, score in sim_scores if m not in row_numbers]
        for i in range(30):
            if sim_scores[i][0] in recommendations:
                recommendations[sim_scores[i][0]] += sim_scores[i][1]
            else:
                recommendations[sim_scores[i][0]] = sim_scores[i][1]
        
    recommendations = {k: v for k, v in sorted(recommendations.items(), key=lambda x: x[1],reverse=True)}
    movie_indices = [i for i in recommendations]
    return df.iloc[movie_indices].head(30)
