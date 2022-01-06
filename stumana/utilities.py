from stumana import db, config
from sqlalchemy import text, func, update, null
from stumana.models import User, Student, Mark, Subject, XVMark, XXXXVMark, ClassRoom, Course, Teacher


# Dang nhap
def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


# Thay doi tuoi quy dinh
def change_chk_age(min=None, max=None):
    try:
        min = int(min)
        _min_age = str(min - 1)
        drop_min = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age1');"
        add_min = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age1'," \
                  " '(YEAR(join_date) - YEAR(bday)) > " + _min_age + "');"
        db.engine.execute(text(drop_min))
        db.engine.execute(text(add_min))
        config.min_age = min
        max = int(max)
        _max_age = str(max + 1)
        drop_max = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age2');"
        add_max = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age2'," \
                  " '(YEAR(join_date) - YEAR(bday)) < " + _max_age + "');"
        db.engine.execute(text(drop_max))
        db.engine.execute(text(add_max))
        config.max_age = max
    except Exception as e:
        return str(e)


# thay doi si so toi da
def change_max_size(max=None):
    try:
        if max:
            max = int(max)
            _max_size = str(max)

            # tao cau lenh sql
            drop_trigger = "drop trigger if exists before_enter_class;"
            create_trigger = " create trigger before_enter_class after update on class_room for each row" \
                             " begin declare new_size int; set new_size = (select total from class_room" \
                             " where new.id = id); if new_size >= (" + _max_size + " + 1) then" \
                                                                                   " signal sqlstate '45001' set message_text = 'Vuot qua so luong toi da'; end if; end;"

            db.engine.execute(text(drop_trigger))
            db.engine.execute(text(create_trigger))
            config.max_size = max
    except Exception as e:
        return str(e)


# Cho: lay bang diem cua cac hoc sinh trong 1 lop theo hoc ky, nam, mon
def get_students_mark(class_id=None, semester=None, year=None, subject_id=None):
    marks = db.session.query(Subject, Student, Mark.semester, Mark.year, XVMark, XXXXVMark, Mark.FinalMark, Mark.avg) \
        .join(Mark, Mark.subject_id.__eq__(Subject.id)) \
        .join(Student, Student.id.__eq__(Mark.student_id)) \
        .join(XVMark, XVMark.id.__eq__(Mark.XV_mark_id), isouter=True) \
        .join(XXXXVMark, XXXXVMark.id.__eq__(Mark.XXXXV_mark_id), isouter=True)

    if class_id:
        marks = marks.filter(Student.class_id.__eq__(class_id))
    if semester:
        marks = marks.filter(Mark.semester.__eq__(semester))
    if year:
        marks = marks.filter(Mark.year.__eq__(year))
    if subject_id:
        marks = marks.filter(Mark.subject_id.__eq__(subject_id))

    return marks


# Cho: tinh trung binh bo qua None.
def average_ignore_none(numbers):
    total = []
    for n in numbers:
        if n:
            total.append(n)
    if len(total) == 0:
        return 0
    avg = sum(total) / len(total)
    return avg


# Cho: lay danh sach hoc sinh theo khoi, ten lop.
def get_student_by_class(grade, class_name):
    return db.session.query(Student) \
        .join(ClassRoom, ClassRoom.id.__eq__(Student.class_id)) \
        .filter(ClassRoom.name.__eq__(class_name)) \
        .filter(ClassRoom.grade.__eq__(grade)).all()


# Cho: lay ra tong so hoc sinh trong lop cua 1 lop theo khoi, ten lop.
def get_total(grade, class_name):
    return db.session.query(ClassRoom.total) \
        .filter(ClassRoom.name.__eq__(class_name)) \
        .filter(ClassRoom.grade.__eq__(grade)).first()


# Cho: Cap nhat diem trung binh vao db.
def cal_avg_mark(subject_id, semester, year):
    marks = get_students_mark(subject_id=subject_id, semester=semester, year=year)

    for s in marks:
        if s.XVMark:
            mark15 = average_ignore_none([s.XVMark.col1, s.XVMark.col2, s.XVMark.col3, s.XVMark.col4, s.XVMark.col5])
        else:
            mark15 = 0
        if s.XXXXVMark:
            mark45 = average_ignore_none([s.XXXXVMark.col1, s.XXXXVMark.col2, s.XXXXVMark.col3])
        else:
            mark45 = 0
        if s.FinalMark:
            avg = (mark15 + mark45 * 2 + s.FinalMark * 3) / 6
        else:
            avg = (mark15 + mark45 * 2) / 6
        db.session.query(Mark).filter(Mark.subject_id.__eq__(subject_id),
                                      Mark.student_id.__eq__(s.Student.id),
                                      Mark.semester.__eq__(semester),
                                      Mark.year.__eq__(year)).update({Mark.avg: avg},
                                                                     synchronize_session=False)
    db.session.commit()


# Cho: lay ra danh sach lop hoc hanh chinh.
def get_classes():
    return db.session.query(ClassRoom).all()


# Cho: lay ra danh sach hoc sinh qua mon theo lop.
def total_qualified_by_class(class_id, semester, year, subject_id):
    cal_avg_mark(subject_id=subject_id, semester=semester, year=year)
    count = db.session.query(func.count(Mark.avg)). \
        join(Student, Student.id.__eq__(Mark.student_id)). \
        join(ClassRoom, ClassRoom.id.__eq__(Student.class_id)). \
        filter(ClassRoom.id.__eq__(class_id),
               Mark.subject_id.__eq__(subject_id),
               Mark.semester.__eq__(semester),
               Mark.year.__eq__(year),
               Mark.avg.__ge__(5)).first()
    return count[0]


# Cho: lay ra danh sach mon hoc.
def get_subjects():
    return db.session.query(Subject.name)


# Cho: lay ra thong tin thong ke theo lop, mon hoc, nam, hoc ky.
def get_stats(semester=None, year=None, subject_name=None):
    classes = get_classes()
    stats = []
    subject_id = db.session.query(Subject.id).filter(Subject.name.__eq__(subject_name)).first()
    for c in classes:
        total_qualified = total_qualified_by_class(c.id, semester=semester, year=year, subject_id=subject_id[0])
        total = c.total if c.total else 0
        stats.append({
            'class_id': c.id,
            'class_name': c.grade + c.name,
            'total': total,
            'total_qualified': total_qualified,
            'ratio': "{0:.2f}".format((float(total_qualified) / total * 100) if total != 0 else 0)
        })

    return stats


# Cho: lay ra teacher_id theo current_user.id
def get_teacher_id(user_id):
    return db.session.query(Teacher.id).filter(Teacher.user_id.__eq__(user_id))


# Cho: lay ra nhung lop hoc dc phu trach cua 1 giao vien.
def get_classes_of_teacher(user_id):
    teacher_id = get_teacher_id(user_id=user_id)

    return db.session.query(Subject.name, ClassRoom.grade, ClassRoom.name, Course.id) \
        .join(Course, Course.subject_id.__eq__(Subject.id)) \
        .join(ClassRoom, ClassRoom.id.__eq__(Course.class_id)) \
        .filter(Course.teacher_id.__eq__(teacher_id)).all()


# Cho: lay ra thong tin cua 1 lop hoc duoc day boi 1 giao vien.
def get_course_info(course_id):
    return db.session.query(ClassRoom.grade, ClassRoom.name, Subject.name, Course.year) \
        .join(ClassRoom, ClassRoom.id.__eq__(Course.class_id)) \
        .join(Subject, Subject.id.__eq__(Course.subject_id)).filter(Course.id.__eq__(course_id)).first()


# Cho: lay bang diem cua cac hoc sinh trong 1 lop hoc duoc day boi 1 giao vien trong 1 hoc ky.
def get_mark_by_course_id(course_id, semester=None):
    course = Course.query.get(course_id)
    if not semester:
        semester = 1
    students = get_students_mark(subject_id=course.subject_id,
                                 class_id=course.class_id,
                                 year=course.year,
                                 semester=semester).order_by(Student.last_name)

    cal_avg_mark(subject_id=course.subject_id,
                 semester=semester,
                 year=course.year)

    marks = []
    for s in students:
        marks.append({
            'student_name': s.Student.last_name + " " + s.Student.first_name,
            'mark15': [s.XVMark.col1, s.XVMark.col2, s.XVMark.col3, s.XVMark.col4, s.XVMark.col5],
            'mark45': [s.XXXXVMark.col1, s.XXXXVMark.col2, s.XXXXVMark.col3],
            'final_mark': s.FinalMark,
            'avg_mark': s.avg,
            'student_id': s.Student.id,
            'subject_id': s.Subject.id
        })

    return marks


# Cho: lay bang diem cua 1 hoc sinh hien thi ra view chinh sua diem.
def get_marks_of_student(subject_id, student_id, year, semester=None):
    records = db.session.query(Subject, Student,
                               Mark.semester, XVMark, XXXXVMark, Mark.FinalMark) \
        .join(Subject, Subject.id.__eq__(Mark.subject_id)) \
        .join(Student, Student.id.__eq__(Mark.student_id)) \
        .join(XVMark, XVMark.id.__eq__(Mark.XV_mark_id), isouter=True) \
        .join(XXXXVMark, XXXXVMark.id.__eq__(Mark.XXXXV_mark_id), isouter=True) \
        .filter(Mark.subject_id.__eq__(subject_id),
                Mark.year.__eq__(year),
                Mark.student_id.__eq__(student_id))

    if semester:
        records = records.filter(Mark.semester.__eq__(semester))

    marks = []
    for r in records.all():
        marks.append({
            'subject': {
                'id': r.Subject.id,
                'name': r.Subject.name,
            },
            'student': {
                'id': r.Student.id,
                'name': r.Student.first_name + " " + r.Student.last_name,
            },
            'semester': r.semester,
            'mark15': [r.XVMark.col1, r.XVMark.col2, r.XVMark.col3, r.XVMark.col4, r.XVMark.col5],
            'mark45': [r.XXXXVMark.col1, r.XXXXVMark.col2, r.XXXXVMark.col3],
            'final_mark': r.FinalMark,
        })

    return marks


# Cho: chinh sua diem cho 1 hoc sinh.
def update_marks(subject_id, student_id, year, mark15=None, mark45=None, final_mark=None):
    record = db.session.query(Mark.XV_mark_id, Mark.XXXXV_mark_id) \
        .filter(Mark.subject_id.__eq__(subject_id),
                Mark.student_id.__eq__(student_id),
                Mark.year.__eq__(year))  # Query lay ra 2 khoa ngoai xvmark, xxxxvmark
    final_marks = db.session.query(Mark).filter(Mark.subject_id.__eq__(subject_id),
                                                Mark.student_id.__eq__(student_id),
                                                Mark.year.__eq__(year))  # Query lay ra diem de cap nhat

    if mark15['1'] or mark45['1'] or final_mark['1']:
        record_put = record.filter(Mark.semester.__eq__(1)).first()  # xvmark_id, xxxxvmark_id cuar hoc ky 1
        # Lay ra 2 id cua xvmark voi xxxxvmark trong Mark vi tri [0] la id cua xvmark, [1] la id cua xxxxvmark

        db.session.query(XVMark).filter(XVMark.id.__eq__(record_put[0])) \
            .update({XVMark.col1: mark15['1'][0] if mark15['1'][0] != '' else null(),
                     XVMark.col2: mark15['1'][1] if mark15['1'][1] != '' else null(),
                     XVMark.col3: mark15['1'][2] if mark15['1'][2] != '' else null(),
                     XVMark.col4: mark15['1'][3] if mark15['1'][3] != '' else null(),
                     XVMark.col5: mark15['1'][4] if mark15['1'][4] != '' else null()},
                    synchronize_session=False)  # Neu khong nhap diem thi diem = null

        db.session.query(XXXXVMark).filter(XXXXVMark.id.__eq__(record_put[1])) \
            .update({XXXXVMark.col1: mark45['1'][0] if mark45['1'][0] != '' else null(),
                     XXXXVMark.col2: mark45['1'][1] if mark45['1'][1] != '' else null(),
                     XXXXVMark.col3: mark45['1'][2] if mark45['1'][2] != '' else null()},
                    synchronize_session=False)  # Neu khong nhap diem thi diem = null

        final_marks.filter(Mark.semester.__eq__(1)) \
            .update({Mark.FinalMark: final_mark['1'] if final_mark['1'] != '' else null()},
                    synchronize_session=False)  # Neu khong nhap diem thi diem = null

    if mark15['2'] or mark45['2'] or final_mark['2']:
        record_put = record.filter(Mark.semester.__eq__(2)).first()  # xvmark_id, xxxxvmark_id cuar hoc ky 2
        # Lay ra 2 id cua xvmark voi xxxxvmark trong Mark vi tri [0] la id cua xvmark, [1] la id cua xxxxvmark

        db.session.query(XVMark).filter(XVMark.id.__eq__(record_put[0])) \
            .update({XVMark.col1: mark15['2'][0] if mark15['2'][0] != '' else null(),
                     XVMark.col2: mark15['2'][1] if mark15['2'][1] != '' else null(),
                     XVMark.col3: mark15['2'][2] if mark15['2'][2] != '' else null(),
                     XVMark.col4: mark15['2'][3] if mark15['2'][3] != '' else null(),
                     XVMark.col5: mark15['2'][4] if mark15['2'][4] != '' else null()},
                    synchronize_session=False)  # Neu khong nhap diem thi diem = null

        db.session.query(XXXXVMark).filter(XXXXVMark.id.__eq__(record_put[1])) \
            .update({XXXXVMark.col1: mark45['2'][0] if mark45['2'][0] != '' else null(),
                     XXXXVMark.col2: mark45['2'][1] if mark45['2'][1] != '' else null(),
                     XXXXVMark.col3: mark45['2'][2] if mark45['2'][2] != '' else null()},
                    synchronize_session=False)  # Neu khong nhap diem thi diem = null

        final_marks.filter(Mark.semester.__eq__(2)) \
            .update({Mark.FinalMark: final_mark['2'] if final_mark['2'] != '' else null()},
                    synchronize_session=False)  # Neu khong nhap diem thi diem = null

    db.session.commit()


def create_all_mark_records(course_id=None):
    course = Course.query.get(course_id)
    students_already_have = db.session.query(Mark.student_id).filter(Mark.subject_id.__eq__(course.subject_id),
                                                                     Mark.year.__eq__(course.year)).distinct()
    students_have_no_record = db.session.query(Student.id) \
        .filter(Student.class_id.__eq__(course.class_id),
                Student.id.not_in(students_already_have))

    for s in students_have_no_record:
        mark15_1 = XVMark()
        mark15_2 = XVMark()
        mark45_1 = XXXXVMark()
        mark45_2 = XXXXVMark()

        db.session.add(mark15_1)
        db.session.add(mark15_2)
        db.session.add(mark45_1)
        db.session.add(mark45_2)

        mark1 = Mark(subject_id=course.subject_id,
                     student_id=s[0],
                     semester=1,
                     year=course.year,
                     xvmark=mark15_1,
                     xxxxvmark=mark45_1)
        db.session.add(mark1)

        mark2 = Mark(subject_id=course.subject_id,
                     student_id=s[0],
                     semester=2,
                     year=course.year,
                     xvmark=mark15_2,
                     xxxxvmark=mark45_2)
        db.session.add(mark2)

    db.session.commit()


# lay thong tin hoc sinh
def info_student():
    return db.session.query(Student).all()


def total_year():
    return db.session.query(Mark.year, Student.first_name, Student.last_name, ClassRoom.grade, ClassRoom.name, Mark.semester, Mark.FinalMark)\
                            .join(Mark, Mark.student_id.__eq__(Student.id), isouter=True)\
                            .join(Student, Student.class_id.__eq__(ClassRoom.id))\
                            .group_by(Student.id)


if __name__ =="__main__":
     print(info_student())
     # print(total_year())


# Tu day tro xuong la de test = console
# a = get_mark_by_course_id(1)
# cal_avg_mark(subject_id=1, year=2021, semester=1)
# a = get_students_mark(class_id=2, semester=1, year=2021, subject_id=1)
# a = get_students_mark(class_id=2, year=2021, subject_id=1)
# a = create_all_mark_records(1)
# print(a)
