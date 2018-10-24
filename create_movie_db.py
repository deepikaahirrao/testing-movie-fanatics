import json
import sqlite3
import logging


LOG = logging.getLogger(__name__)


def is_table_exist():
    query = '''SELECT name FROM sqlite_master WHERE type="table" AND name="movies"'''
    db_conn = sqlite3.connect('db_movies')

    try:
        cur = db_conn.cursor()
        cur.execute(query)
        res = cur.fetchone()
    except:
        LOG.error("error while creating database")
        raise
    if res:
        return True
    return False
    

def create_table():
    query = '''CREATE TABLE IF NOT EXISTS "movies" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" TEXT NOT NULL,
                    "director" TEXT NOT NULL,
                    "popularity" INTEGER NOT NULL,
                    "genre" TEXT NOT NULL,
                    "imdb_score" INTEGER NOT NULL
               )'''
    db_conn = sqlite3.connect('db_movies')

    try:
        db_conn.cursor().execute(query)
        db_conn.commit()
    except:
        LOG.error("error while creating database")
        raise


def add_records():
    movie_list = []
    with open('imdb.json', 'r') as fp:
        movies = json.load(fp)
        for m in movies:
            data = []
            keys = []
            for k, v in m.items():
                if '99popularity' == k:
                    keys.append('popularity')
                else:
                    keys.append(k)
                if isinstance(v, list):
                    data.append(json.dumps(v))
                else:
                    data.append(v)
            movie_list.append(tuple(data))          
    
    if movie_list:
        query = '''INSERT INTO "movies"{keys}
                    values
                    (?, ?, ?, ?, ?)'''.format(keys=tuple(keys))
        db_conn = sqlite3.connect('db_movies')
        try:
            db_conn.cursor().executemany(query, tuple(movie_list))
            db_conn.commit()
        except:
            LOG.error("error while inserting data")
            raise
        finally:
            db_conn.close()
    LOG.debug("No records are added in the tables")


def main():
    if not is_table_exist():
        create_table()
        add_records()

