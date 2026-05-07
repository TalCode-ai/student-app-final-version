import pytest
import requests


@pytest.fixture
def base_url():
    return "http://127.0.0.1:5000/students"

#שליפת רשימת תלמידים

def test_get_students(base_url):
    res = requests.get(base_url)

    assert res.status_code == 200
    assert res.reason == "OK"
    assert isinstance(res.json(), list)

#בדיקה שלילית - שליפת סטודנט שלא נמצא

def test_get_student_not_found(base_url):
    res = requests.get(f"{base_url}/99999")
    data = res.json()

    assert res.status_code == 404
    assert isinstance(data, dict)
    assert "message" in data

#בדיקה להוספת סטודנט חדש

def test_add_student(base_url):
    student = {
        "name": "John Doe",
        "age": 20
    }

    res = requests.post(base_url, json=student)

    assert res.status_code in [200, 201]

    data = res.json()
    assert data["name"] == "John Doe"
    assert data["age"] == 20
    assert "id" in data

#קבלת סטודנט לפי ID

def test_get_student_by_id(base_url):
    # Arrange
    student = {"name": "Jane Doe", "age": 22}
    create_res = requests.post(base_url, json=student)
    student_id = create_res.json()["id"]

    # Act
    res = requests.get(f"{base_url}/{student_id}")

    # Assert
    assert res.status_code == 200

    data = res.json()
    assert data["id"] == student_id
    assert data["name"] == "Jane Doe"
    assert data["age"] == 22

#בדיקה לעדכון סטודנט
def test_update_student(base_url):
    # Arrange - create student first
    student = {
        "name": "Before Update",
        "age": 30
    }

    create_res = requests.post(base_url, json=student)
    student_id = create_res.json()["id"]

    updated_student = {
        "id": student_id,
        "name": "After Update",
        "age": 31
    }

    # Act
    res = requests.put(base_url, json=updated_student)

    # Assert
    assert res.status_code == 200

    data = res.json()
    assert data["id"] == student_id
    assert data["name"] == "After Update"
    assert data["age"] == 31

#בדיקה למחיקת סטודנט
def test_delete_student(base_url):
    # Arrange - create student first
    student = {
        "name": "Delete Me",
        "age": 40
    }

    create_res = requests.post(base_url, json=student)
    student_id = create_res.json()["id"]

    # Act
    delete_res = requests.delete(f"{base_url}/{student_id}")

    # Assert
    assert delete_res.status_code == 200

    # Verify deleted
    get_res = requests.get(f"{base_url}/{student_id}")
    assert get_res.status_code == 404

    # מחיקת סטודנט שלא קיים
def test_delete_student_not_found(base_url):
    res = requests.delete(f"{base_url}/99999")

    assert res.status_code == 404

#בדיקות מקרי קצה של הוספת סטודנט
@pytest.mark.parametrize(
    "student",
    [
        {"age": 20},                         # שם חסר
        {"name": "No Age"},                  # גיל חסר
        {"name": "", "age": 25},             # שם ריק
        {"name": "A", "age": 25},            # שם קצר
        {"name": "Too Young", "age": 17},    # צעיר מידי
        {"name": "Too Old", "age": 121},     # מבוגר מידי
    ],
    ids=[
        "missing name",
        "missing age",
        "empty name",
        "short name",
        "too young",
        "too old",
    ]
)
def test_add_student_negative(base_url, student):
    res = requests.post(base_url, json=student)

    assert res.status_code == 400

#עדכון סטודנט שלא קיים במערכת
def test_update_student_not_found(base_url):
    # Arrange
    updated_student = {
        "id": 9999,
        "name": "Does not Exist",
        "age": 30
    }
    # Act
    res = requests.put(base_url, json=updated_student)
    data = res.json()
    # Assert
    assert res.status_code == 404
    assert isinstance(data, dict)
    assert "message" in data

# -מקרה של הוספת סטודנט כאשר הגיל הוא טקסט ולא מספר
# באג מוכר: API מחזיר הודעת שגיאה 500 במקום 400)
def test_add_student_text_age_bug(base_url):
    student = {"name": "Bad Age", "age": "abc"}

    res = requests.post(base_url, json=student)

    assert res.status_code == 400

#  בדיקת מקרי קצה של עדכון סטודנט - באג: API מחזיר שגיאה לא נכונה
@pytest.mark.xfail(reason="Known bug: API returns 500 instead of 400 for invalid update input")
@pytest.mark.parametrize(
    "updated_student",
    [
        {"id": 1, "name": "Invalid Update", "age": 15},
        {"id": 1, "name": "Invalid Update", "age": "abc"},
        {"id": 1, "name": "", "age": 25},
        {"id": "", "name": "Invalid Update", "age": 25},
    ],
    ids=[
        "too young",
        "text age",
        "empty name",
        "empty id",
    ]
)
def test_update_student_negative(base_url, updated_student):
    res = requests.put(base_url, json=updated_student)

    assert res.status_code == 400
