# application logic
from app import db


class ServiceError(Exception): pass

# תוקן בלוגיקה-באג שמחזיר שגיאה לא נכונה
def add_student(student):
    name = student.get("name")
    age = student.get("age")

    if not isinstance(name, str) or len(name.strip()) < 2:
        raise ServiceError("invalid name")

    if not isinstance(age, int):
        raise ServiceError("invalid age")

    if age < 18 or age > 120:
        raise ServiceError("invalid age")

    return db.add_student(student)


def get_students():
    return db.get_students()


def get_student(student_id):
    return db.get_student(student_id)


# תוקן בלוגיקה
def update_student(student):
    student_id = student.get("id")
    name = student.get("name")
    age = student.get("age")

    if not isinstance(student_id, int) or student_id <= 0:
        raise ServiceError("invalid student id")

    if not isinstance(name, str) or len(name.strip()) < 2:
        raise ServiceError("invalid name")

    if not isinstance(age, int):
        raise ServiceError("invalid age")

    if age < 18 or age > 120:
        raise ServiceError("invalid age")

    return db.update_student(student)


def delete_student(student_id):
    return db.delete_student(student_id)

if __name__=="__main__":
    result = get_student(1)
    print(result)