from flask import Flask, request, jsonify
import uuid


# redis library
import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

app = Flask(__name__)


# API 1: /add
@app.route("/add", methods=["POST"])
def add():
    data = request.get_json() # How to operate?
    a = data.get("a")
    b = data.get("b")

    task_id = str(uuid.uuid4()) 
    
    # 기존과 다르게 redis에 저장하므로..
    task_data = {
            "status": "processing",
            "result": None
    }
    
    # redis에 task 저장
    r.set(task_id, json.dumps(task_data))

    result = a + b 

    task_data["status"] = "done"
    task_data["result"] = result

    r.set(task_id, json.dumps(task_data))

    return jsonify({"task_id": task_id}) 


# API 2: /status/<task_id>
@app.route("/status/<task_id>")
def status(task_id):
    task_json = r.get(task_id)
    if not task_json:
        return jsonify({"error": "not found"}), 404 # return format..?
    
    task = json.loads(task_json)
    return jsonify({"status": task["status"]}) 


# API 3: /result/<task_id>
@app.route("/result/<task_id>")
def result(task_id):
    task_json = r.get(task_id)
    if not task_json:
        return jsonify({"error": "not found"}), 404 # Exception 1
    
    task = json.loads(task_json)

    if task["status"] != "done":
        return jsonify({"error": "not ready"}), 400 # Exception 2

    return jsonify({"result": task["result"]})


# Main Setting
if __name__ == "__main__":
    app.run(debug=True)

# 이제 redis에서 json을 저장하니 flask가 꺼져도.. 문제가 없다..!
# redis의 역할
#   1. cache
#   2. session 저장소
#   3. 작업 상태/큐

"""
| 튜플 요소 | Flask의 해석    |
| ----- | ------------ |
| 첫 번째  | HTTP 응답 Body |
| 두 번째  | HTTP 상태 코드   |

flask는 view함수(route에 따른 데코레이터 함수들)의 튜플 반환값을 자동으로 이렇게 처리
"""

