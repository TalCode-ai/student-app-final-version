
import pytest
from unittest.mock import patch, Mock
import app.service as service

from app.service import ServiceError


# שליפת תלמיד לפי ID

@patch("app.service.db.get_student")
def test_get_student_positive(mock_get_student: Mock):
    # Arrange
    mock_get_student.return_value = {"id": 1, "name": "John Doe", "age": 20}
    # Act
    result = service.get_student(1)
    # Assert
    assert result == {"id": 1, "name": "John Doe", "age": 20}
    # Validation
    mock_get_student.assert_called_with(1)


# שליפת כל התלמידים

@patch("app.service.db.get_students")
def test_get_students(mock_get_students: Mock):
    # Arrange
    mock_get_students.return_value = [
        {"id": 1, "name": "John Doe", "age": 20},
        {"id": 2, "name": "Jane Smith", "age": 22}
    ]
    # Act
    result = service.get_students()
    # Assert
    assert  result == [
        {"id": 1, "name": "John Doe", "age": 20},
        {"id": 2, "name": "Jane Smith", "age": 22}
    ]
    # Validation
    mock_get_students.assert_called_once()


# הוספת תלמיד חדש (תרחיש חיובי)

@patch("app.service.db.add_student")
def test_add_student_positive(mock_add_student: Mock):
    # Arrange
    new_student = {"name": "Amir", "age": 40}
    added_student = {"id": 3, "name": "Amir", "age": 40}
    mock_add_student.return_value = added_student

    # Act
    result = service.add_student(new_student)

    # Assert
    assert result == added_student

    # Validation
    mock_add_student.assert_called_with(new_student)


# ניסיון להוסיף תלמיד עם גיל לא חוקי

@patch("app.service.db.add_student")
def test_add_student_negative(mock_add_student: Mock):
    # Arrange
    student = {"name": "Amir", "age": 17}

    # Act + Assert
    with pytest.raises(ServiceError) as exc_info:
        service.add_student(student)

    assert "invalid age" in str(exc_info.value)

    # Validation
    mock_add_student.assert_not_called()


# הוספת תלמיד עם נתונים לא תקינים

@pytest.mark.parametrize(
    "student",
    [
        {"name": "Amir", "age": 17},   # צעיר מדי
        {"name": "Amir", "age": 121},  # מבוגר מדי
        {"name": "", "age": 25},       # שם ריק
        {"name": "A", "age": 25},      # שם קצר מדי
    ],
    ids=[
        "too young",
        "too old",
        "empty name",
        "name too short"
    ]
)
@patch("app.service.db.add_student")
def test_add_student_invalid_data(mock_add_student: Mock, student):
    # Act + Assert
    with pytest.raises(ServiceError):
        service.add_student(student)

    # Validation
    mock_add_student.assert_not_called()


# עדכון תלמיד קיים (תרחיש חיובי)

@patch("app.service.db.update_student")
def test_update_student_positive(mock_update_student: Mock):
    # Arrange
    updated_data = {"id": 1, "name": "Amir", "age": 25}  # New Data
    db_response = {"id": 1, "name": "Amir", "age": 25}

    mock_update_student.return_value = db_response

    # Act
    result = service.update_student(updated_data)

    # Assert
    assert result["age"] == 25

    # Validation
    mock_update_student.assert_called_with(updated_data)



# ניסיון לעדכן תלמיד עם גיל לא חוקי

@patch("app.service.db.update_student")
def test_update_student_invalid_age(mock_update_student: Mock):
    student = {"id": 1, "name": "Amir", "age": 17}

    with pytest.raises(ServiceError):
        service.update_student(student)

    mock_update_student.assert_not_called()




# מחיקת תלמיד קיים (תרחיש חיובי)

@patch("app.service.db.delete_student")
def test_delete_student_positive(mock_delete_student: Mock):
    # Arrange
    student_id = 1
    mock_delete_student.return_value = None

    # Act
    result = service.delete_student(student_id)

    # Assert
    assert result is None

    # Validation
    mock_delete_student.assert_called_with(student_id)


# בדיקות גבול לגיל חוקי בעת הוספת תלמיד
# הערכים המותרים: 18 ו־120

@pytest.mark.parametrize("age", [18, 120])
@patch("app.service.db.add_student")
def test_add_student_valid_age_boundaries(mock_add_student: Mock, age):
    student = {"name": "Amir", "age": age}
    mock_add_student.return_value = {"id": 1, **student}

    result = service.add_student(student)

    assert result["age"] == age
    mock_add_student.assert_called_once_with(student)




# ניסיון למחוק תלמיד שלא קיים במערכת

@patch("app.service.db.delete_student")
def test_delete_student_not_found(mock_delete_student: Mock):
    # Arrange
    student_id = 999
    mock_delete_student.return_value = None

    # Act
    result = service.delete_student(student_id)

    # Assert
    assert result is None

    # Validation
    mock_delete_student.assert_called_once_with(student_id)

# עדכון סטודנט חדש

@pytest.mark.jira_key("SAFV-4")
@patch("app.service.db.update_student")
def test_update_student_positive(mock_update_student: Mock):
    # Arrange
    updated_data = {"id": 1, "name": "Amir", "age": 25}  # New Data
    db_response = {"id": 1, "name": "Amir", "age": 25}

    mock_update_student.return_value = db_response

    # Act
    result = service.update_student(updated_data)

    # Assert
    assert result["age"] == 25

    # Validation
    mock_update_student.assert_called_with(updated_data)


 # בדיקת מקרי קצה של עדכון סטודנט חדש

@pytest.mark.parametrize(
    "student",
    [
        {"id": "", "name": "Amir", "age": 25},
        {"id": -1, "name": "Amir", "age": 25},
        {"id": "abc", "name": "Amir", "age": 25},
        {"id": 1, "name": "", "age": 25},
        {"id": 1, "name": "A", "age": 25},
        {"id": 1, "name": "Amir", "age": 17},
        {"id": 1, "name": "Amir", "age": 121},
        {"id": 1, "name": "Amir", "age": "abc"},
    ],
    ids=[
        "empty id",
        "negative id",
        "text id",
        "empty name",
        "short name",
        "too young",
        "too old",
        "text age",
    ]
)
@patch("app.service.db.update_student")
def test_update_student_negative(mock_update_student, student):
    with pytest.raises(ServiceError):
        service.update_student(student)

    mock_update_student.assert_not_called()


# מחיקת סטודנט קיים

@patch("app.service.db.delete_student")
def test_delete_student_positive(mock_delete_student: Mock):
    # Arrange
    student_id = 1
    mock_delete_student.return_value = None

    # Act
    result = service.delete_student(student_id)

    # Assert
    assert result is None

    # Validation
    mock_delete_student.assert_called_with(student_id)

# מחיקת סטודנט לא קיים
#########################

# בדיקות קצה שליליות למחיקת סטודנט (סרוויס לא עושה Validtion ID)

@pytest.mark.xfail(reason="Known bug: delete_student does not validate invalid student_id")
@pytest.mark.parametrize(
    "student_id",
    [
        "",  # ערך ריק
        -1,  # ערך לא חוקי (מינוס)
        "abc",  # ערך לא חוקי (טקסט)
    ],
    ids=[
        "empty id",
        "negative id",
        "text id",
    ]
)
@patch("app.service.db.delete_student")
def test_delete_student_negative(mock_delete_student, student_id):
    with pytest.raises(ServiceError):
        service.delete_student(student_id)

    mock_delete_student.assert_not_called()