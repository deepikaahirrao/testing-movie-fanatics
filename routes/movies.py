import attr
import logging
from flask import Blueprint, jsonify, request, current_app as app
from db.movies import MovieInt, MovieClient


api_v1 = Blueprint('api_v1', __name__)


@api_v1.route("/movie/add/", methods=['PUT'])
def add_movie():
    '''
        I am here
    '''
    data = request.get_json()
    app.movies = MovieClient(app)
    movie_obj = MovieInt(**data)
    if app.movies.save(movie_obj):
        return jsonify({"sucsess": True, "msg": "{} is added successfully".format(name)}), 200
    return jsonify({"sucsess": False})


@api_v1.route("/movie/remove/<name>/", methods=['DELETE'])
def remove_movie(name):
    app.movies = MovieClient(app)
    if app.movies.delete_by_name(name):
        return jsonify({"sucsess": True, "msg": "{} is deleted successfully".format(name)}), 200
    return jsonify({"sucsess": False})


@api_v1.route("/movie/edit/<name>/", methods=['POST'])
def edit_movie(name):
    data = request.get_json()
    app.movies = MovieClient(app)
    if app.movies.edit_by_name(name, data):
        return jsonify({"sucsess": True, "msg": "{} is edited successfully".format(name)}), 200
    return jsonify({"sucsess": False})


@api_v1.route("/movie/get/<name>/", methods=['GET'])
def get_movie(name):
    app.movies = MovieClient(app)
    result = app.movies.find(name)
    if result:
        return jsonify({"sucsess": True, "data": result}), 200
    return jsonify({"sucsess": False})

