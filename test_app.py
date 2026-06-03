# test_app.py — 15 итераций TDD для To-Do List приложения
# Методология: RED → GREEN → REFACTOR

import pytest
from app import app, tasks


@pytest.fixture(autouse=True)
def clearTasks():
    """Очищает список задач перед каждым тестом."""
    tasks.clear()
    import app as appModule
    appModule.next_id = 1
    yield
    tasks.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 1 — Приложение запускается и отвечает 200
# RED:    тест падает — маршрут / не существует
# GREEN:  добавляем маршрут / в app.py
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_01_app_is_running(client):
    """Приложение запускается и возвращает статус 200."""
    response = client.get("/")
    assert response.status_code == 200


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 2 — Получить пустой список задач
# RED:    тест падает — маршрут /tasks не существует
# GREEN:  добавляем GET /tasks, возвращаем []
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_02_get_empty_tasks(client):
    """GET /tasks возвращает пустой список если задач нет."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 3 — Добавить задачу
# RED:    тест падает — POST /tasks не существует
# GREEN:  добавляем POST /tasks, сохраняем задачу
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_03_add_task(client):
    """POST /tasks создаёт новую задачу и возвращает 201."""
    response = client.post("/tasks", json={"title": "Купить молоко"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Купить молоко"


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 4 — Задача имеет поле title
# RED:    тест падает — поле title отсутствует в ответе
# GREEN:  добавляем title в объект задачи
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_04_task_has_title(client):
    """Созданная задача содержит поле title."""
    client.post("/tasks", json={"title": "Сделать зарядку"})
    response = client.get("/tasks")
    tasks_list = response.get_json()
    assert len(tasks_list) == 1
    assert tasks_list[0]["title"] == "Сделать зарядку"


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 5 — Задача имеет уникальный id
# RED:    тест падает — поле id отсутствует
# GREEN:  добавляем автоинкремент id
# REFACTOR: вынести логику в переменную next_id
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_05_task_has_id(client):
    """Каждая задача имеет уникальный числовой id."""
    client.post("/tasks", json={"title": "Задача 1"})
    client.post("/tasks", json={"title": "Задача 2"})
    response = client.get("/tasks")
    tasks_list = response.get_json()
    assert tasks_list[0]["id"] == 1
    assert tasks_list[1]["id"] == 2


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 6 — Получить задачу по id
# RED:    тест падает — GET /tasks/<id> не существует
# GREEN:  добавляем маршрут GET /tasks/<id>
# REFACTOR: вынести поиск в функцию findTask()
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_06_get_task_by_id(client):
    """GET /tasks/1 возвращает конкретную задачу по id."""
    client.post("/tasks", json={"title": "Прочитать книгу"})
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Прочитать книгу"


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 7 — Задача не найдена → 404
# RED:    тест падает — сервер возвращает 500 вместо 404
# GREEN:  добавляем проверку на None и возврат 404
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_07_task_not_found(client):
    """GET /tasks/999 возвращает 404 если задача не существует."""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 8 — Отметить задачу выполненной
# RED:    тест падает — PATCH /tasks/<id>/complete не существует
# GREEN:  добавляем маршрут и меняем completed = True
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_08_complete_task(client):
    """PATCH /tasks/1/complete отмечает задачу как выполненную."""
    client.post("/tasks", json={"title": "Написать отчёт"})
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    assert response.get_json()["completed"] is True


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 9 — Удалить задачу
# RED:    тест падает — DELETE /tasks/<id> не существует
# GREEN:  добавляем маршрут и удаляем задачу из списка
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_09_delete_task(client):
    """DELETE /tasks/1 удаляет задачу и возвращает 200."""
    client.post("/tasks", json={"title": "Задача для удаления"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    response = client.get("/tasks")
    assert response.get_json() == []


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 10 — Задача имеет дату создания
# RED:    тест падает — поле created_at отсутствует
# GREEN:  добавляем created_at = datetime.utcnow().isoformat()
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_10_task_has_created_at(client):
    """Задача содержит поле created_at с датой создания."""
    response = client.post("/tasks", json={"title": "Задача с датой"})
    data = response.get_json()
    assert "created_at" in data
    assert data["created_at"] is not None


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 11 — Получить только невыполненные задачи
# RED:    тест падает — фильтрация не реализована
# GREEN:  добавляем параметр ?status=active
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_11_get_active_tasks(client):
    """GET /tasks?status=active возвращает только невыполненные задачи."""
    client.post("/tasks", json={"title": "Активная задача"})
    client.post("/tasks", json={"title": "Выполненная задача"})
    client.patch("/tasks/2/complete")
    response = client.get("/tasks?status=active")
    tasks_list = response.get_json()
    assert len(tasks_list) == 1
    assert tasks_list[0]["title"] == "Активная задача"


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 12 — Получить только выполненные задачи
# RED:    тест падает — фильтр по completed не реализован
# GREEN:  добавляем параметр ?status=completed
# REFACTOR: объединить фильтры в одном месте
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_12_get_completed_tasks(client):
    """GET /tasks?status=completed возвращает только выполненные задачи."""
    client.post("/tasks", json={"title": "Активная задача"})
    client.post("/tasks", json={"title": "Выполненная задача"})
    client.patch("/tasks/2/complete")
    response = client.get("/tasks?status=completed")
    tasks_list = response.get_json()
    assert len(tasks_list) == 1
    assert tasks_list[0]["title"] == "Выполненная задача"


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 13 — Обновить название задачи
# RED:    тест падает — PUT /tasks/<id> не существует
# GREEN:  добавляем маршрут и обновляем title
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_13_update_task(client):
    """PUT /tasks/1 обновляет название задачи."""
    client.post("/tasks", json={"title": "Старое название"})
    response = client.put("/tasks/1", json={"title": "Новое название"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "Новое название"


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 14 — Пустое название → ошибка 400
# RED:    тест падает — пустой title принимается
# GREEN:  добавляем валидацию title в POST и PUT
# REFACTOR: вынести валидацию в отдельную проверку
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_14_empty_title_returns_400(client):
    """POST с пустым title возвращает 400."""
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_iteration_14b_whitespace_title_returns_400(client):
    """POST с title из пробелов возвращает 400."""
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400


# ════════════════════════════════════════════════════════════════════════════
# ИТЕРАЦИЯ 15 — Получить количество задач
# RED:    тест падает — GET /tasks/count не существует
# GREEN:  добавляем маршрут с подсчётом total/active/completed
# REFACTOR: —
# ════════════════════════════════════════════════════════════════════════════

def test_iteration_15_get_tasks_count(client):
    """GET /tasks/count возвращает количество задач по категориям."""
    client.post("/tasks", json={"title": "Задача 1"})
    client.post("/tasks", json={"title": "Задача 2"})
    client.post("/tasks", json={"title": "Задача 3"})
    client.patch("/tasks/1/complete")
    response = client.get("/tasks/count")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 3
    assert data["active"] == 2
    assert data["completed"] == 1
