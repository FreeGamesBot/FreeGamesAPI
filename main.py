import flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify, make_response, request
import pymongo
import threading

connection = pymongo.MongoClient("")
db = connection[""]
collection = db[""]
freegameslist = []

app = flask.Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["60 per hour"])


def pull_newgames():
    threading.Timer(1200.0, pull_newgames).start()
    freegameslist.clear()
    for game in collection.find({}, {"_id": 0}):  # Pulls all games from the database
        freegameslist.append(game)

pull_newgames()


@app.route('/', methods=['GET'])
@limiter.limit("1 per minute")
def home():
    return jsonify({"message": "Welcome to free games bot api! For more info, visit https://docs.freegamesbot.xyz"})


@app.route('/ping', methods=['GET'])
@limiter.limit("1 per minute")
def ping():
    return jsonify({"status": "API is alive"})


@app.route('/freegames', methods=['GET'])
@limiter.limit("1 per minute")
def freegames():
    type = request.args.get('type')
    lst = []
    if type == "all":
        for i in freegameslist:
            lst.append(i)
    elif type == "epicgames":
        for i in freegameslist:
            if i["Platform"] == "Epic Games":
                lst.append(i)
    elif type == "gog":
        for i in freegameslist:
            if i["Platform"] == "GOG":
                lst.append(i)
    elif type is (None or ""):
        for i in freegameslist:
            lst.append(i)
    return jsonify({'result' : lst}, 200)


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
            jsonify(error=f"ratelimit exceeded {e.description}")
            , 429
    )


if __name__ == '__main__':
    app.run(debug=True)
