# Flask: Flask app 객체를 만드는 Class && Request: HTTP Request를 담고 있는 객체 && jsonify: Python 딕셔너리를 JSON으로 바꿔주는 함수
from flask import Flask, request, jsonify
# 고유id를 만드는 파이썬 라이브러리로 task_id 만들 때 사용
import uuid


# Flask 클래스 객체인 app 생성 (__name__: 현재 파일 이름을 객체에 알려줌)
app = Flask(__name__)


# 작업 상태를 저장하는 메모리 공간인 딕셔너리 (나중에 Redis로 바뀜)
tasks = {}


# 데코레이터 문법
# /add url에 따른 add() 함수 수행
# 참고로 Flask는 url에서 path 부분만을 보기에.. /를 통해 구분하기
# 즉, Flask는 특정 path에 따른 함수를 수행해주는 라이브러리!
# 첫번째 API: "/add"
@app.route("/add", methods=["POST"])
def add():
    data = request.get_json() # 클라이언트의 http request를 json으로 변환
    a = data.get("a")
    b = data.get("b")

    # 랜덤 task_id 생성
    # http는 client를 기억하지 않기 때문에 api_서버 측에서 task_id를 저장해줄 필요가 있다..!
    task_id = str(uuid.uuid4()) 

    # 일단 바로 계산하지만, '진행중'처럼 흉내냄
    # 딕셔너리 중첩
    tasks[task_id] = {
        "status": "processing",
        "result": None
    }

    # 계산 (나중에 celery가 담당할 예정)
    result = a + b 

    tasks[task_id]["status"] = "done"
    tasks[task_id]["result"] = result

    # task_id를 json으로 클라이언트에게 알려줌 (나중에 이를 기반으로 조회하라고!)
    return jsonify({"task_id": task_id}) 


# 두번째 API: /status/<task_id>
@app.route("/status/<task_id>")
def status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "not found"}), 404 # task_id 조회 안되면 404 Not Found!

    return jsonify({"status": task["status"]}) # task_id의 상태 알랴줌!


# 세번째 API: /result/<task_id>
@app.route("/result/<task_id>")
def result(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "not found"}), 404 # Exception 1

    if task["status"] != "done":
        return jsonify({"error": "not ready"}), 400 # Exception 2

    return jsonify({"result": task["result"]})


if __name__ == "__main__":
    app.run(debug=True)
