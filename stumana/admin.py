from stumana import app, db, utilities
from flask_admin.contrib.sqla import ModelView
from stumana.models import User, Student, ClassRoom, Subject, Teacher, Staff, UserRole
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_login import current_user, logout_user
from flask import redirect, request
import config
from datetime import datetime


class AuthenticatedBaseView(BaseView):
    def __index__(self):
        return current_user.is_authenticated


class AuthenticatedModelView(ModelView):
    create_modal = True
    edit_modal = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class StaffBaseView(AuthenticatedBaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.STAFF or current_user.user_role == UserRole.ADMIN


class AdminBaseView(AuthenticatedBaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


class StudentModalView(AuthenticatedModelView):
    column_labels = {
        'first_name': 'Họ',
        'last_name': 'Tên',
        'bday': 'Ngày sinh',
        'sex': 'Giới tính',
        'address': 'Địa chỉ',
        'phone': 'SĐT',
        'email': 'Email',
        'join_date': 'Ngày gia nhập',
        'active': 'Active',
        'user': 'Tên tài khoản',
        'classroom': 'Lớp',
        'class_name': 'Tên lớp',
        'name': 'Tên người dùng',
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'avatar': 'Ảnh đại diện',
        'user_role': 'Chức vụ'
    }


class ClassModalView(AuthenticatedModelView):
    column_labels = {
        'grade': 'Khối',
        'name': 'Tên lớp',
        'total': 'Sỉ số',
    }


class SubjectModelView(StudentModalView):
    column_searchable_list = ['name']
    column_filters = ['name']
    column_labels = {
        'id': 'Mã môn học',
        'name': 'Tên môn học'
    }


class CustomPersonForm(StudentModalView):
    form_excluded_columns = ['user', 'classroom', 'classes']


class CustomUserForm(StudentModalView):
    form_excluded_columns = ['student', 'teacher', 'staff']


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("admin/index.html")


class ChangeRule(AdminBaseView):
    @expose("/")
    def __index__(self):
        return self.render("admin/change-rule.html",
                           min_age=config.min_age,
                           max_age=config.max_age,
                           max_size=config.max_size)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


class UserAllocation(AdminBaseView):    # de lam sau
    @expose("/")
    def __index__(self):
        return self.render("admin/index.html")

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


# class Student(ModalModelView):
#     def is_accessible(self):
#         if current_user.is_authenticated:
#             return current_user.user_role == UserRole.STAFF

# in hoc sinh
class PrintStudentView(AdminBaseView):
    @expose('/')
    def __index__(self):
        info_student = utilities.info_student()
        return self.render("print/print_student.html", info_student=info_student)


# in diem ca nam
# class PrintTotalMarkView(AdminBaseView):
#     @expose('/')
#     def __index__(self):
#         total_year = utilities.total_year()
#         return self.render("print/print_totalmark.html", total_year=total_year)


class StatsView(StaffBaseView):
    @expose('/')
    def __index__(self):
        subject_name = request.args.get("subject", "Toán 11")
        semester = request.args.get("semester", "1")
        year = request.args.get("year", datetime.now().year)
        stats = utilities.get_stats(subject_name=subject_name,
                                    semester=semester,
                                    year=year)

        return self.render("admin/stats.html",
                           stats=stats,
                           subjects=utilities.get_subjects())


class SetUpClass(StaffBaseView):    # de lam sau
    @expose("/")
    def __index__(self):
        err_msg = None
        students = None
        grade = request.args.get('grade')
        class_name = request.args.get('class')

        if grade and class_name:
            students = utilities.get_student_by_class(grade=grade,
                                                      class_name=class_name)
        else:
            return self.render("admin/set-up.html",
                               classes=utilities.get_classes(),
                               total=utilities.get_total(grade=grade,
                                                         class_name=class_name),
                               err_msg=err_msg)

        if students:
            return self.render("admin/set-up.html",
                               classes=utilities.get_classes(),
                               students=students,
                               total=utilities.get_total(grade=grade,
                                                         class_name=class_name))
        else:
            err_msg = "Lớp không tồn tại hoặc không có học sinh nào!!!"

        return self.render("admin/set-up.html",
                           classes=utilities.get_classes(),
                           total=utilities.get_total(grade=grade,
                                                     class_name=class_name),
                           err_msg=err_msg)


class LogoutView(BaseView):
    @expose('/')
    def __index__(self):
        logout_user()
        return redirect("/")

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app=app, name='Quản trị Trường THPT',
              template_mode='bootstrap4',
              index_view=MyAdminIndexView())
admin.add_view(CustomUserForm(User, db.session,
                              name='Quản lý tài khoản',
                              category="Tài khoản",
                              menu_icon_type='fa',
                              menu_icon_value='fa-users'))
admin.add_view(UserAllocation(name="Cấp tài khoản",
                              category="Tài khoản",
                              menu_icon_type='fa',
                              menu_icon_value='fa-id-card'))
# Staff
admin.add_view(CustomPersonForm(Student, db.session,
                                name='Học sinh',
                                category="Cá nhân",
                                menu_icon_type='fa',
                                menu_icon_value='fa-graduation-cap'))
# Staff
# admin.add_view(Change_class(Student, db.session,
#                             name='Điều chỉnh lớp học',
#                             category="Lớp học"))
# Admin
admin.add_view(CustomPersonForm(Teacher, db.session,
                                name='Giáo viên',
                                category="Cá nhân",
                                menu_icon_type='fa',
                                menu_icon_value='fa-podcast'))
# Admin
admin.add_view(CustomPersonForm(Staff, db.session,
                                name='Nhân viên',
                                category="Cá nhân",
                                menu_icon_type='fa',
                                menu_icon_value='fa-briefcase'))
# Admin
admin.add_view(ClassModalView(ClassRoom, db.session,
                                name='Quản lý lớp học',
                                menu_icon_type='fa',
                                menu_icon_value='fa-columns',
                                category="Lớp học"))
# Staff
# admin.add_view(Change_class(Student, db.session,
#                             menu_icon_type='fa',
#                             menu_icon_value='fa-graduation-cap',
#                             category="Lớp học"))
# Staff
admin.add_view(SetUpClass(name="Lập danh sách lớp",
                          menu_icon_type='fa',
                          menu_icon_value='fa-reorder',
                          category="Lớp học"))
# Admin
admin.add_view(SubjectModelView(Subject, db.session,
                                name='Môn học',
                                menu_icon_type='fa',
                                menu_icon_value='fa-book'))
# Admin
admin.add_view(ChangeRule(name="Thay đổi quy định",
                          menu_icon_type='fa',
                          menu_icon_value='fa-gear'))
# Admin
admin.add_view(StatsView(name='Thống kê báo cáo',
                         menu_icon_type='fa',
                         menu_icon_value='fa-line-chart'))

# bieu mau hoc sinh
admin.add_view(PrintStudentView(name='In học sinh',
                                category='Biểu mẫu',
                                menu_icon_type='fa'))

# bieu mau diem hoc ki
# admin.add_view(PrintMarkView(name='In điểm học kì',
#                              category='Biểu mẫu',
#                              menu_icon_type='fa'))

# bieu mau diem ca nam
# admin.add_view(PrintTotalMarkView(name='In điểm cả năm',
#                              category='Biểu mẫu',
#                              menu_icon_type='fa'))


admin.add_view(LogoutView(name="Đăng xuất",
                          menu_icon_type='fa',
                          menu_icon_value='fa-sign-out'))
