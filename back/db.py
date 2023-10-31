import psycopg2
import pandas as pd
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def insert_product(id, name, content, tablename = 'product'):
    return f"INSERT INTO {tablename}(id, name, content) VALUES ({id}, '{name}' '{content}');"

def create_table(tablename):
    conn = psycopg2.connect(
        host=getenv("HOST"),
        port=getenv("PORT"),
        database=getenv("DBNAME"),
        user=getenv("USER"),
        password=getenv("PASSWORD")
    )

    cursor = conn.cursor()
    sentence = f"""CREATE TABLE IF NOT EXISTS {tablename}(
                   id INT, 
                   name TEXT,
                   content TEXT
                );"""
    cursor.execute(sentence)

    conn.commit()
    cursor.close()
    conn.close()

def insert_products(tablename = 'product'):
    conn = psycopg2.connect(
        host=getenv("HOST"),
        port=getenv("PORT"),
        dbname=getenv("DBNAME"),
        user=getenv("USER"),
        password=getenv("PASSWORD")
    )

    cursor = conn.cursor()

    # N = 44425
    df = pd.read_csv('./BD2P2/definitivo.csv')
    for _, row in df.iterrows():
        id = row[1]
        name = str(row[-2]).lower()
        content = ' '.join(map(lambda x: str(x).lower(), list(row[2:-2])))
        insert = insert_product(id, name, content, tablename)
        cursor.execute(insert)

    conn.commit()
    cursor.close()
    conn.close()

def create_index(tablename='product'):
    conn = psycopg2.connect(
        host=getenv("HOST"),
        port=getenv("PORT"),
        dbname=getenv("DBNAME"),
        user=getenv("USER"),
        password=getenv("PASSWORD")
    )

    cursor = conn.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

    cursor.execute(f"ALTER TABLE {tablename} ADD COLUMN indexed tsvector;")
    cursor.execute(f"""UPDATE {tablename} SET indexed = T.indexed FROM (
                    SELECT id, setweight(to_tsvector('english', name), 'A') || setweight(to_tsvector('english', content), 'B') AS indexed FROM {tablename}
                   ) AS T WHERE {tablename}.id = T.id;""")
    cursor.execute('CREATE INDEX IF NOT EXISTS content_idx_gin ON product USING gin (indexed);')

    conn.commit()
    cursor.close()
    conn.close()

create_table('product')
insert_products('product')
create_index('product')