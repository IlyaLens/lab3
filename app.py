# app.py — To-Do List веб-приложение (Flask + TDD)

from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# База данных в памяти
tasks = []
next_id = 1


def findTask(task_id):
    return next((t for t in tasks if t["id"] == task_id), None)


# ── Итерация 1: GET / — проверка работоспособности ──────────────────────────
@app.route("/")
def index():
    return jsonify({"message": "Todo App is running"}), 200


# ── Итерация 2-5: GET /tasks — список задач ──────────────────────────────────
@app.route("/tasks", methods=["GET"])
def getTasks():
    status = request.args.get("status")

    # Итерация 11: фильтр по невыполненным
    if status == "active":
        return jsonify([t for t in tasks if not t["completed"]]), 200

    # Итерация 12: фильтр по выполненным
    if status == "completed":
        return jsonify([t for t in tasks if t["completed"]]), 200

    return jsonify(tasks), 200


# ── Итерация 3-5: POST /tasks — добавить задачу ──────────────────────────────
@app.route("/tasks", methods=["POST"])
def addTask():
    global next_id
    data = request.get_json()

    # Итерация 14: проверка пустого названия
    if not data or not data.get("title") or not data["title"].strip():
        return jsonify({"error": "Title cannot be empty"}), 400

    task = {
        "id": next_id,
        "title": data["title"].strip(),
        "completed": False,
        "created_at": datetime.utcnow().isoformat(),  # Итерация 10
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


# ── Итерация 6-7: GET /tasks/<id> — получить задачу по id ───────────────────
@app.route("/tasks/<int:task_id>", methods=["GET"])
def getTask(task_id):
    task = findTask(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404  # Итерация 7
    return jsonify(task), 200


# ── Итерация 8: PATCH /tasks/<id>/complete — отметить выполненной ────────────
@app.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
def completeTask(task_id):
    task = findTask(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    task["completed"] = True
    return jsonify(task), 200


# ── Итерация 9: DELETE /tasks/<id> — удалить задачу ─────────────────────────
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def deleteTask(task_id):
    task = findTask(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    tasks.remove(task)
    return jsonify({"message": "Task deleted"}), 200


# ── Итерация 13: PUT /tasks/<id> — обновить название ─────────────────────────
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def updateTask(task_id):
    task = findTask(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json()
    if not data or not data.get("title") or not data["title"].strip():
        return jsonify({"error": "Title cannot be empty"}), 400
    task["title"] = data["title"].strip()
    return jsonify(task), 200


# ── Итерация 15: GET /tasks/count — количество задач ─────────────────────────
@app.route("/tasks/count", methods=["GET"])
def getTasksCount():
    return jsonify({
        "total": len(tasks),
        "active": len([t for t in tasks if not t["completed"]]),
        "completed": len([t for t in tasks if t["completed"]]),
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
