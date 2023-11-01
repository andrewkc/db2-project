from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from BD2P2.prueba import InvertIndex
from os import getenv
import psycopg2
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints

@app.post('/')
async def root():
    return "Hello from FastAPI"


@app.post('/data_from_postgres')
async def top_k_postgres(data :dict):
    try:
        query = data.get('query')
        k = int(data.get('k')) if data.get('k') != '' else 5

        conn = psycopg2.connect(
            host=getenv("HOST"),
            port=getenv("PORT"),
            dbname=getenv("DBNAME"),
            user=getenv("USER"),
            password=getenv("PASSWORD")
        )

        cursor = conn.cursor()

        sentence = f"""
                EXPLAIN ANALYZE
                SELECT id, name, content, ts_rank(indexed, query) rank
                FROM product, plainto_tsquery('english', '{query}') query
                ORDER BY rank DESC LIMIT {k};
                """
        cursor.execute(sentence)
        response = cursor.fetchall()
        execution_time = response[-1][0].split('Execution Time: ')[1]
        
        sentence = f"""
                SELECT id, name, content, ts_rank(indexed, query) rank
                FROM product, plainto_tsquery('english', '{query}') query
                ORDER BY rank DESC LIMIT {k};
                """
        cursor.execute(sentence)
        response = cursor.fetchall()

        conn.close()
        cursor.close()

        return {'content': response, 'execution_time': execution_time, 'status_code':200}
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)


@app.post('/data_from_invidx')
async def top_k_invidx(data: dict):
    try:
        query = data.get('query')
        k = int(data.get('k')) if data.get('k') != '' else 5

        index = InvertIndex(index_file="spimi.txt")
        matching_indices, scores = index.retrieve_k_nearest(query, k)
        df = index.loadData()
        rows = df.iloc[matching_indices].iloc[:, 2:-2].values.tolist()
        content = list(map(lambda row: ' '.join(map(str, row)), rows))
        df = df.iloc[matching_indices].iloc[:, [1, -2]]
        df['content'] = content
        df['scores'] = scores
        df['id'] = df['id'].astype(int)
        result = df.values.tolist()

        return {'content': result, 'status_code':200}
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)


@app.post('/create_index')
async def create_index():
    try:   
        global index 
        index = InvertIndex(index_file="spimi.txt")
        index.prueba()
        return {'response': 200}
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
