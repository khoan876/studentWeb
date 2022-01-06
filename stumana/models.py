from stumana import db
from sqlalchemy import Column, String, Integer, DATETIME, ForeignKey, Enum, Boolean, Float, CheckConstraint
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from enum import Enum as UserEnum
from flask_login import UserMixin


class UserRole(UserEnum):
    ADMIN = 0
    STAFF = 1
    TEACHER = 2
    STUDENT = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, autoincrement=True, primary_key=True)


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    user_role = Column(Enum(UserRole), nullable=False)
    student = relationship('Student', backref='user', lazy=True)
    teacher = relationship('Teacher', backref='user', lazy=True)
    staff = relationship('Staff', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Ethnic(BaseModel):
    name = Column(String(20), nullable=False)


class Person(BaseModel):
    __abstract__ = True

    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    bday = Column(DATETIME, nullable=False)
    sex = Column(Boolean, default=True)
    address = Column(String(100))
    phone = Column(String(15))
    email = Column(String(50))
    join_date = Column(DATETIME, default=datetime.now())
    active = Column(Boolean, default=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class ClassRoom(BaseModel):
    grade = Column(String(5), nullable=False)
    name = Column(String(10), nullable=False)
    total = Column(Integer, default=0)
    students = relationship('Student', backref='classroom', lazy=False)
    # teachers = relationship('Teacher', secondary='course', lazy='subquery',
    #                         backref=backref('classroom', lazy=True))

    def __str__(self):
        return self.name


class Student(Person):
    __table_args__ = (
        CheckConstraint('(year(join_date) - year(bday)) > 14', name='chk_age1'),
        CheckConstraint('(year(join_date) - year(bday)) < 21', name='chk_age2')
    )

    ethnic_id = Column(Integer, ForeignKey(Ethnic.id))
    user_id = Column(Integer, ForeignKey(User.id), unique=True)
    class_id = Column(Integer, ForeignKey(ClassRoom.id))


class Teacher(Person):
    ethnic_id = Column(Integer, ForeignKey(Ethnic.id))
    user_id = Column(Integer, ForeignKey(User.id), unique=True)
    classes = relationship('ClassRoom', secondary='course', lazy='subquery',
                           backref=backref('teacher', lazy=True))


class Staff(Person):
    ethnic_id = Column(Integer, ForeignKey(Ethnic.id))
    user_id = Column(Integer, ForeignKey(User.id), unique=True)


# mon hoc
class Subject(BaseModel):
    name = Column(String(20), nullable=False)

    def __str__(self):
        return self.name


# Lop hoc theo bo mon
class Course(BaseModel):
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    class_id = Column(Integer, ForeignKey(ClassRoom.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    year = Column(Integer, default=datetime.now().year)


# diem 15p
class XVMark(BaseModel):
    col1 = Column(Float)
    col2 = Column(Float)
    col3 = Column(Float)
    col4 = Column(Float)
    col5 = Column(Float)
    mark = relationship('Mark', backref='xvmark', lazy=True)


# diem 45p
class XXXXVMark(BaseModel):
    col1 = Column(Float)
    col2 = Column(Float)
    col3 = Column(Float)
    mark = relationship('Mark', backref='xxxxvmark', lazy=True)


# bang diem cua 1 hoc sinh trong mot hoc ky cua 1 nam
class Mark(db.Model):
    subject_id = Column(Integer, ForeignKey(Subject.id), primary_key=True, nullable=False)
    student_id = Column(Integer, ForeignKey(Student.id), primary_key=True, nullable=False)
    semester = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    XV_mark_id = Column(Integer, ForeignKey(XVMark.id), unique=True)
    XXXXV_mark_id = Column(Integer, ForeignKey(XXXXVMark.id), unique=True)
    FinalMark = Column(Float)
    avg = Column(Float)


if __name__ == '__main__':
    # db.drop_all()

    db.create_all()

    # tao Trigger tu dong tinh toan si so lop hoc
    db.engine.execute("drop trigger if exists change_class_size;")
    db.engine.execute("create trigger change_class_size before update on student for each row begin"
                      " declare old_size int; declare new_size int; set old_size = (select count(s.id)"
                      " from student s, class_room c where s.class_id = c.id and c.id = old.class_id);"
                      " set new_size = (select count(s.id) from student s, class_room c"
                      " where s.class_id = c.id and c.id = new.class_id);"
                      " update class_room set total = new_size + 1 where id = new.class_id;"
                      " update class_room set total = old_size - 1 where id = old.class_id;"
                      "end;")
