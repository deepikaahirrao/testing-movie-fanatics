import sqlite3

from flask import g
from flask.cli import with_appcontext


def get_db(db_name):
    db = sqlite3.connect(
        db_name,
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = dict_factory
    return db


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

