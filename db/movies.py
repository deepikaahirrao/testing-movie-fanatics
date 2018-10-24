import attr
import json
import logging
from attr.validators import instance_of, optional
from cattr import unstructure, structure
from typing import Dict, List
from . import get_db


LOG = logging.getLogger(__name__)
VALID_COLUNMS = ["name", "director", "popularity", "genre", "imdb_score"]


def validate_score_and_popularity(instance, attribute, value):
    if not (isinstance(value, float) or isinstance(value, int)):
        raise ValueError("{value} should be of type float or int"
            .format(value=value)
        )

    upper_bound = 0
    if "popularity" == attribute:
        upper_bound = 100

    if "imdb_score" == attribute:
        upper_bound = 10

    if value < 0 and value > upper_bound:
        raise ValueError("{value} should be between valid range for {attribute} attribute"
            .format(value=value, attribute=attribute)
        )


@attr.s
class MovieInt:
    name = attr.ib(type=str, default="")
    director = attr.ib(type=str, default="")    
    popularity = attr.ib(type=float, validator=validate_score_and_popularity, default=0)
    genre = attr.ib(type=List[str], validator=instance_of(list), default=attr.Factory(list))
    imdb_score = attr.ib(type=float, validator=validate_score_and_popularity, default=0)

    def __getitem__(self, item):
        return getattr(self, item)

    def serialize(self):
        result = unstructure(self)
        keys = []
        values = []
        for k, v in result.items():
            keys.append(k)
            if isinstance(v, list):
                values.append(json.dumps(v))
            else:
                values.append(v)
        return (keys, values)

    @classmethod
    def deserialize(cls, doc):
        doc.pop("id")
        for k, v in doc.items():
            if 'genre' == k:    
                data = eval(doc['genre'])
                doc[k] = data
        return MovieInt(**doc)


class MovieClient:

    def __init__(self, app):
        self._db = get_db(app.config['db_name'])
        self._table = 'movies'

    def find(self, name) -> List[MovieInt]:
        query = '''SELECT * FROM {table} 
                WHERE name=?'''.format(table=self._table)
        try:
            cur = self._db.cursor()
            cur.execute(query, (name,))
            rows = cur.fetchall()
        except sqlite3.Error as e:
            LOG.error("Error occurred while fetching record for: {}".format(name))
            raise Exception("Operation failed with error: {}".format(e.message))
        result = []
        for row in rows:
            result.append(attr.asdict(MovieInt.deserialize(row)))
        return result

    def save(self, movie_data: MovieInt) -> bool:
        (keys, values) = movie_data.serialize()
        query = '''INSERT INTO "{table}"{keys}
                values
                (?, ?, ?, ?, ?)'''.format(table=self._table, keys=tuple(keys))
        try:
            self._db.cursor().execute(query, tuple(values))
            self._db.commit()
        except sqlite3.Error as e:
            LOG.error("Error occurred while saving record for: {}".format(values))
            raise Exception("Operation failed with error: {}".format(e.message))
        return True


    def save_many(self, doc_list: List[MovieInt]) -> bool:
        movie_list = []
        for movie in doc_list:
            (keys, values) = movie.serialize()
            movie_list.append(tuple(values))
        query = '''INSERT INTO {table}"{keys}
                    values
                    (?, ?, ?, ?, ?)'''.format(table=self._table, keys=tuple(keys))
        try:
            self._db.cursor().executemany(query, tuple(movie_list))
            self._db.commit()
        except sqlite3.Error as e:
            LOG.error("Error occurred while saving multiple records")
            raise Exception("Operation failed with error: {}".format(e.message))
            return False
        return True

    def delete_by_name(self, name: str) -> bool:
        query = '''DELETE FROM {table} WHERE name=?'''.format(table=self._table)
        try:
            res = self._db.cursor().execute(query, (name,))
            self._db.commit()
        except sqlite3.Error as e:
            LOG.error("Error occurred while deleting record for: {}".format(name))
            raise Exception("Operation failed with error: {}".format(e.message))
        return True

    def edit_by_name(self, name: str, doc: Dict) -> bool:
        update_query = _construct_update_query(doc)
        query = '''UPDATE {table}
                  SET {update_query}
              WHERE name=?'''.format(table=self._table, update_query=update_query)
        try:
            self._db.cursor().execute(query, (name,))
            self._db.commit()
        except sqlite3.Error as e:
            LOG.error("Error occurred while updating record for: {}".format(name))
            raise Exception("Operation failed with error: {}".format(e.message))
        return True

    def fetch_all(self):
        #TO DO: implement this
        pass

    def fetch_multiple(self):
        #TO DO: implement this
        pass


def _construct_update_query(doc):
    query = ""
    for col in VALID_COLUNMS:
        if col in doc:
            query += '{} = "{}" ,'.format(col, doc[col])
    return query.rstrip(' ,')

