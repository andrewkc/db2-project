from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from os import getenv
import psycopg2
import uvicorn

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


@app.post('get_data_from_postgres')
async def get_top_k_postgres(data):
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
                SELECT id, content, ts_rank(indexed, query) rank
                FROM product, plainto_tsquery('english', '{query}') query
                ORDER BY rank DESC LIMIT {k};
                """
        cursor.execute(sentence)
        response = cursor.fetchall()

        conn.close()
        cursor.close()

        return {'content': response, 'status_code':200}
    except Exception as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


@app.post('get_data_from_invidx')
async def get_top_k_invidx():
    try:
        response = None
        return {'content': response, 'status_code':200}
    except Exception as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', reload=True)