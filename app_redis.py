# flask library
from flask import Flask, request, jsonify

# redis library
import redis
import json

# celery library
from celery.result import AsyncResult
from celery_app import celery

# celery module
from tasks import slow_add

        
# Init Redis & Flask
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
app = Flask(__name__)


# API 1: /add
@app.route("/add", methods=["POST"])
def add():
    data = request.get_json() 

    a = data.get("a")
    b = data.get("b")

    task = slow_add.delay(a, b)

    return jsonify({
        "task_id": task.id,
        "status": "submitted"
    }) 


# API 2: /status/<task_id>
@app.route("/status/<task_id>")
def status(task_id):
    res = AsyncResult(task_id, app=celery)

    return jsonify({
        "task_id": task_id,
        "status": res.status
    })


# API 3: /result/<task_id>
@app.route("/result/<task_id>")
def result(task_id):
    res = AsyncResult(task_id, app=celery)

    if res.status != "SUCCESS":
        return jsonify({
            "task_id": task_id,
            "status": res.status,
            "result": None,
            "message": "not ready yet"
            }), 202

    return jsonify({
        "task_id": task_id,
        "status": res.status,
        "result": res.result
    })


# Main Setting
if __name__ == "__main__":
    app.run(debug=True)

