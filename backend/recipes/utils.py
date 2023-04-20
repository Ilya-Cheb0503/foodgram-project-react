from contextlib import closing
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
import json

PROJECT_BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(os.path.join(PROJECT_BASE_DIR / 'infra', '.env'))

DB_NAME = str(os.getenv('DB_NAME'))
POSTGRES_USER = str(os.getenv('POSTGRES_USER'))
POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD'))
DB_HOST = str(os.getenv('DB_HOST'))
DB_PORT = str(os.getenv('DB_PORT'))


def script_db():

    try:
        with closing(psycopg2.connect(
            dbname=DB_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )) as conn:
            with conn.cursor() as cursor:
                with open(
                    '../data/ingredients.json',
                    mode='r',
                    encoding='utf8',
                ) as json_file:
                    data = json.load(json_file)
                    for line in data:
                        title = line.get('name')
                        measurement_unit = line.get('measurement_unit')
                        cursor.execute(
                            f"INSERT INTO recipes_ingredient("
                            f"name, measurement_unit"
                            f") VALUES ('{title}', '{measurement_unit}');")
                        conn.commit()
        print('все найс')
    except Exception as error:
        print(error)


if __name__ == '__main__':
    script_db()
