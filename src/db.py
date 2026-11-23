import os 
import psycopg 

def get_db():
    return psycopg.connect(os.environ["DATABASE_URL"])