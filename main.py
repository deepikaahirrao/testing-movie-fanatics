import os
import yaml

from flask import Flask
from routes import add_routes
import create_movie_db


def create_app(config_file_name, create_db=False):
    app = Flask(__name__, instance_relative_config=True)
    config = load_config(config_file_name)
    app.config.update(config)
    #_init_db_client(app)
    add_routes(app)
    return app


#def _init_db_client(app):
#    app.movies = MovieClient(app)


def load_config(config_file_name):
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, config_file_name)
    with open(config_file) as f:
        return yaml.load(f.read())


def _create_db(db_name):
    create_movie_db.main()


app = create_app('config.yaml', create_db=True)
_create_db(app.config['db_name'])
app.run(host='0.0.0.0', port=20000)
