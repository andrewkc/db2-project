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


@app.post('/get_data_from_postgres')
async def get_top_k_postgres(data :dict):
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
        return JSONResponse(content=e.response["Error"], status_code=500)


@app.post('/get_data_from_invidx')
async def get_top_k_invidx(data):
    try:
        inverted_index = InvertIndex(
            index_file="./BD2P2/your_index_file.txt", 
            abstracts_por_bloque=10000, 
            dataFile="./BD2P2/definitivo.csv")

        query = data.get('query')
        k = int(data.get('k')) if data.get('k') != '' else 5

        matching_indices = inverted_index.retrieve_k_nearest(query, k)
        return {'content': matching_indices, 'status_code':200}
    except Exception as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


@app.post('/create_index')
async def create_index():
    try:
        inverted_index = InvertIndex(
            index_file="./BD2P2/your_index_file.txt", 
            abstracts_por_bloque=10000, 
            dataFile="./BD2P2/definitivo.csv")
        
        inverted_index.SPIMIConstruction()
        index = inverted_index.index_blocks()
        inverted_index.write_index_tf_idf(index, len(index))
        return {'response': 200}
    except Exception as e:
        return JSONResponse(content=e.response["Error"], status_code=500)
