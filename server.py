from flask import Flask, render_template, jsonify
from pymongo import MongoClient, ASCENDING

app  = Flask(__name__)

mongo_client = MongoClient()
db = mongo_client['witchdoctor']

@app.route("/")
def index():
    record = db['playlist'].find().sort([("requested_at", ASCENDING)]).limit(1).next()
    return  render_template('index.html')

@app.route("/next")
def next():
    record = db['playlist'].find().sort([("requested_at", ASCENDING)]).limit(1).next()
    db['playlist'].delete_many({"_id": record["_id"]})
    return jsonify(request_string=record["request_string"])

if __name__ == "__main__":
    app.run(host='0.0.0.0')
