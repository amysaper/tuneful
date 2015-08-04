# JSON Schema describing the structure of a song
post_schema = {
    "properties": {
        "file" : {
            "id": {"type": "int"}
            }
    },
    "required": ["file", "id"]
}


import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError


import models
import decorators
from tuneful import app
from database import session
from utils import upload_path

#Gets all songs
@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """

    songs = session.query(models.Song)

    # Convert the songs to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")

#Gets a single song
@app.route("/api/songs/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def song_get(id):
    """ Single song endpoint """
    # Get the post from the database
    song = session.query(models.Song).get(id)

    # Check whether the post exists
    # If not return a 404 with a helpful message
    if not song:
        message = "Could not find song with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Return the song as JSON
    data = json.dumps(song.as_dictionary())
    return Response(data, 200, mimetype="application/json")

#post a song
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    """ Add a new song """
    data = request.json

    # Check that the JSON supplied is valid, and fits the scheme for the song (including an id)
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Add the Song to the database
    song = models.Song(file=data["file"], id=data["id"])
    session.add(song)
    session.commit()

    # Return a 201 Created, containing the song as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("song_get", id=song.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")
