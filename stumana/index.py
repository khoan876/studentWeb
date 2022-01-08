from stumana import login
from flask import render_template, url_for, jsonify
from admin import *
from flask_login import login_user, logout_user, login_required


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/user_login', methods=['get', 'post'])
def user_login():
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method.__eq__('POST'):
        try:
            username = request.form['username']
            password = request.form['password']

            user = utilities.check_login(username=username, password=password)
            if user:
                login_user(user=user)
                if current_user.user_role == UserRole.ADMIN:
                    return redirect('/admin')
                next = request.args.get('next', '/')
                return redirect(next)
            else:
                error_msg = "Sai tài khoản hoặc mật khẩu !!!"

        except Exception as ex:
            error_msg = str(ex)

    return render_template('login.html', error_msg=error_msg)


@app.route("/user_logout")
def user_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/api/change-rule", methods=['PUT'])
def change_rule():
    data = request.json
    min_age = data.get('min_age')
    max_age = data.get('max_age')
    max_size = data.get('max_size')

    result1 = utilities.change_chk_age(min=min_age, max=max_age)
    result2 = utilities.change_max_size(max=max_size)
    if result1 or result2:
        return jsonify({'status': 404})

    return jsonify({'status': 200})


# @app.route('/report/<int:classroom_id>')
# def report_student(classroom_id):
#     subject = request.args.get("subject")
#     classroom = utilities.get_class_by_id(classroom_id=classroom_id)
#     students = utilities.get_student_by_class(class_id=classroom_id)
#     avg = utilities.get_student_avg(class_id=classroom_id, subject=subject)
#
#     return render_template('report-student.html',
#                            classroom=classroom,
#                            students=students,
#                            avg=avg)


# STAFF them hoc sinh
@app.route("/add-newstudents",  methods=['get', 'post'])
@login_required
def list_students():
    if current_user.user_role == UserRole.STAFF:
        list_student = utilities.info_student()

        return render_template("staff/list-students.html", list_student=list_student)
    else:
        return redirect("/")


@app.route('/add-newstudents/add', methods=['GET', 'POST'])
@login_required
def add_students():
    if current_user.user_role == UserRole.STAFF:

        return render_template("layout/list-students.html")


# @admin.route('/add-newstudents/edit/<int:student_id>', methods=['GET', 'POST'])
# @login_required
# def edit_student(student_id):








# in danh sach hoc sinh moi
@app.route("/print/newstudent")
@login_required
def print_student():
    if current_user.user_role == UserRole.STAFF:
        info_student = utilities.info_student()
        return render_template("print/print_student.html", info_student=info_student)
    else:
        return redirect("/")


@app.route("/students-marks")
@login_required
def students_marks():
    if current_user.user_role == UserRole.TEACHER:
        classes = utilities.get_classes_of_teacher(current_user.id)
        course_id = request.args.get('course_id')

        if course_id:
            course = utilities.get_course_info(course_id)
            utilities.create_all_mark_records(course_id=course_id)
            marks = utilities.get_mark_by_course_id(course_id=course_id)

            return render_template("students-marks.html",
                                   marks=marks,
                                   course=course,
                                   classes=classes)
        return render_template("students-marks.html", classes=classes)
    else:
        return redirect("/")


@app.route("/students-marks/edit/<int:student_id>")
@login_required
def edit_marks(student_id):
    if current_user.user_role == UserRole.TEACHER:
        year = request.args.get('year')
        subject_id = request.args.get('subject_id')
        classes = utilities.get_classes_of_teacher(current_user.id)

        marks = utilities.get_marks_of_student(student_id=student_id,
                                               subject_id=subject_id,
                                               year=year)

        return render_template("student_marks.html", marks=marks, classes=classes)
    else:
        return redirect("/")


# in diem hoc ky
@app.route("/students-marks/print/<int:student_id>")
@login_required
def print_mark(student_id):
    if current_user.user_role == UserRole.TEACHER:
        course = utilities.info_course()
        year = request.args.get('year')
        subject_id = request.args.get('subject_id')
        classes = utilities.get_classes_of_teacher(current_user.id)
        marks = utilities.get_marks_of_student(student_id=student_id,
                                               subject_id=subject_id,
                                               year=year)
        return render_template("print/print_mark.html", marks=marks, classes=classes, course=course)
    else:
        return redirect("/")


# in diem ca nam
@app.route("/students-marks/print")
@login_required
def print_totalmark():
    if current_user.user_role == UserRole.TEACHER:
        classes = utilities.get_classes_of_teacher(current_user.id)
        course_id = request.args.get('course_id')
        course = utilities.get_course_info(course_id)
        marks = utilities.get_mark_by_course_id(course_id=course_id)
        return render_template("print/print_totalmark.html",
                               marks=marks,
                               course=course,
                               classes=classes)

    else:
        return redirect("/")


@app.route("/api/update-mark", methods=['PUT'])
@login_required
def update_marks():
    data = request.json
    subject_id = data.get('subject_id')
    student_id = data.get('student_id')
    year = data.get('year')
    mark15 = {
        '1': data.get('mark15_1'),
        '2': data.get('mark15_2')
    }
    mark45 = {
        '1': data.get('mark45_1'),
        '2': data.get('mark45_2')
    }
    final_mark = {
        '1': data.get('final_mark1'),
        '2': data.get('final_mark2')
    }

    try:
        result = utilities.update_marks(subject_id=subject_id,
                                        student_id=student_id,
                                        year=year,
                                        mark15=mark15,
                                        mark45=mark45,
                                        final_mark=final_mark)
    except Exception as e:
        return jsonify({'status': 404,
                        'err_msg': e})

    return jsonify({'status': 200})


@app.route("/api/load-marks", methods=['POST'])
def load_marks():
    data = request.json
    try:
        marks = utilities.get_mark_by_course_id(course_id=data.get('course_id'), semester=data.get('semester'))
        return jsonify({'status': 200,
                        'marks': marks})
    except:
        return jsonify({'status': 404})


# @app.route("/api/cal-avg", methods=['POST'])
# def cal_avg():
#     data = request.json
#
#     try:
#         utilities.cal_avg_mark(subject_id=data.get('subject_id'),
#                                semester=data.get('semester'),
#                                year=data.get('year'))
#     except:
#         return jsonify({'status': 404})
#
#     return jsonify({'status': 200,
#                     'avg_mark': })


@login.user_loader
def user_load(user_id):
    return utilities.get_user_by_id(user_id=user_id)


@app.context_processor
def common_response():
    return {
        'UserRole': UserRole,
        'year': datetime.now().year
    }


if __name__ == '__main__':
    app.run(debug=True)
