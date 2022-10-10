import flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify, make_response, request
import pymongo

connection = pymongo.MongoClient("")
db = connection[""]
collection = db[""]

app = flask.Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["60 per hour"])


@app.route('/ping', methods=['GET'])
@limiter.limit("1 per minute")
def ping():
    return jsonify({"status": "API is alive"})


@app.route('/freegames', methods=['GET'])
@limiter.limit("1 per minute")
def freegames():
    type = request.args.get('type')
    lst = []
    x = collection.find({}, {"_id": 0})
    if type == "all":
        for i in x:
            lst.append(i)
    elif type == "epicgames":
        for i in x:
            if i["Platform"] == "Epic Games":
                lst.append(i)
    elif type == "gog":
        for i in x:
            if i["Platform"] == "GOG":
                lst.append(i)
    elif type is None:
        return make_response(jsonify({"error": "No type specified"}), 400)
    return jsonify({'result' : lst}, 200)


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
            jsonify(error=f"ratelimit exceeded {e.description}")
            , 429
    )


if __name__ == '__main__':
    app.run(debug=True)
