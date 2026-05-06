from unittest.mock import patch, Mock
from app import db
import pytest


# שליפת כל התלמידים

@patch("app.db._get_connection")
def test_get_students_positive(mock_get_connection: Mock):
    # Arrange
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "John Doe", "age": 20},
        {"id": 2, "name": "Jane Smith", "age": 22}
    ]

    # Act
    result = db.get_students()

    # Assert
    assert result == [
        {"id": 1, "name": "John Doe", "age": 20},
        {"id": 2, "name": "Jane Smith", "age": 22}
    ]

    # Validation
    mock_cursor.execute.assert_called_with("select * from students")
    mock_cursor.fetchall.assert_called_once()
    mock_con.close.assert_called_once()


# שליפת תלמיד לפי ID

@patch("app.db._get_connection")
def test_get_student_positive(mock_get_connection: Mock):
    # Arrange
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = {
        "id": 1,
        "name": "John Doe",
        "age": 20
    }

    # Act
    result = db.get_student(1)

    # Assert
    assert result == {
        "id": 1,
        "name": "John Doe",
        "age": 20
    }

    # Validation
    mock_cursor.execute.assert_called_once_with(
        "select * from students where id = %s",
        (1,)
    )
    mock_cursor.fetchone.assert_called_once()
    mock_con.close.assert_called_once()


  # קבלת סטודנט - מקרה קצה (דאטהבייס ריק)

@patch("app.db._get_connection")
def test_get_students_empty_list(mock_get_connection: Mock):
    # Arrange
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    # Act
    result = db.get_students()
    # Assert
    assert result == []
    # Validation
    mock_cursor.fetchall.assert_called_once()
    mock_con.close.assert_called_once()


# הוספת תלמיד

@patch("app.db._get_connection")
def test_add_student_positive(mock_get_connection: Mock):
    # Arrange
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor

    mock_cursor.lastrowid = 1
    student = {"name": "John Doe", "age": 20}

    # Act
    result = db.add_student(student)

    # Assert
    assert result == {"name": "John Doe", "age": 20, "id": 1}

    # Validation
    mock_cursor.execute.assert_called_once_with(
        "insert into students (name, age) values (%s, %s)",
        ("John Doe", 20)
    )
    mock_con.commit.assert_called_once()
    mock_con.close.assert_called_once()


# עדכון תלמיד

@patch("app.db.get_student")
@patch("app.db._get_connection")
def test_update_student_positive(mock_get_connection: Mock, mock_get_student: Mock):
    # Arrange
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1

    student = {"id": 1, "name": "John Doe", "age": 25}
    mock_get_student.return_value = {"id": 1, "name": "John Doe", "age": 25}

    # Act
    result = db.update_student(student)

    # Assert
    assert result == {"id": 1, "name": "John Doe", "age": 25}

    # Validation
    mock_cursor.execute.assert_called_with(
        "update students set name=%s, age=%s where id=%s",
        ("John Doe", 25, 1)
    )
    mock_con.commit.assert_called_once()
    mock_get_student.assert_called_with(1)
    mock_con.close.assert_called_once()


# מחיקת תלמיד

@patch("app.db.get_student")
@patch("app.db._get_connection")
def test_delete_student_positive(mock_get_connection: Mock, mock_get_student: Mock):
    # Arrange
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor

    mock_get_student.return_value = {"id": 1, "name": "John Doe", "age": 20}

    # Act
    result = db.delete_student(1)

    # Assert
    assert result == {"id": 1, "name": "John Doe", "age": 20}

    # Validation
    mock_get_student.assert_called_with(1)
    mock_cursor.execute.assert_called_with(
        "delete from students where id = %s", (1,)
    )
    mock_con.commit.assert_called_once()
    mock_con.close.assert_called_once()


 # מחיקת תלמיד שלא קיים

@patch("app.db.get_student")
@patch("app.db._get_connection")
def test_delete_student_not_found(mock_get_connection: Mock, mock_get_student: Mock):
    # Arrange
    mock_get_student.side_effect = KeyError("student not found: 999")

    # Act + Assert
    with pytest.raises(KeyError):
        db.delete_student(999)

    # Validate
    mock_get_student.assert_called_once_with(999)
    mock_get_connection.assert_called_once()



# בדיקה של שליפת תלמיד שלא קיים במערכת

@patch("app.db._get_connection")
def test_get_student_not_found(mock_get_connection: Mock):
    mock_con = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_con
    mock_con.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    try:
        db.get_student(999)
        assert False
    except KeyError:
        pass

    mock_con.close.assert_called_once()