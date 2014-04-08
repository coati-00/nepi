'''Creating test just for registration since it is prone to changing'''
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from nepi.main.models import Country, School
from nepi.main.models import Course
from nepi.main.views import ContactView, CreateSchoolView
from nepi.main.views import CreateCourseView, UpdateCourseView
from datetime import datetime


class TestFormViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.country = Country(name='LS', region='Region 1')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.course = Course(school=self.school,
                             semester="Fall 2018", name="Course",
                             start_date=datetime.now(),
                             end_date=datetime.now())
        self.student = User(first_name="student", last_name="student",
                            username="student", email="student@email.com",
                            password="student")
        self.student.save()
        self.teacher = User(first_name="teacher", last_name="teacher",
                            username="teacher", email="teacher@email.com",
                            password="teacher")
        self.teacher.save()

    def test_create_school(self):
        '''CreateSchoolView'''
        request = self.factory.post(
            '/add_school/',
            {"name": "School Needs Name",
             "country": self.country})
        response = CreateSchoolView.as_view()(request)
#        self.assertEqual(response.status_code, 302)
#        self.assertTrue(School.objects.count() > 0)

# need to pass it saved school object
# check templates and urls?
#    def test_update_school(self):
#        '''UpdateSchoolView'''
#        request = self.factory.post(
#            '/edit_school/',
#            {"name": "School Needs Name",
#             "country": "ET"})
#        response = UpdateSchoolView.as_view()(request)
#        self.assertEqual(response.status_code, 302)
#        self.assertTrue(School.objects.count() > 0)


    def test_create_course(self):
        '''CreateSchoolView'''
        request = self.factory.post(
            '/add_course/',
            {"name": "Course Needs Name",
             "country": self.country,
             "school": self.school})
        response = CreateCourseView.as_view()(request)
#        self.assertEqual(response.status_code, 302)
#        self.assertTrue(Course.objects.count() > 0)

#    def test_teacher_registration_and_login(self):
#        '''when teachers register they should
#        be added to the pending teachers table'''
#        request = self.factory.post(
#            '/add_course/',
#            {"name": "Course Needs Name",
#             "country": "ET"})
#        response = RegistrationView.as_view()(request)
#        self.assertEqual(response.status_code, 302)
#        self.assertTrue(PendingTeachers.objects.count() > 0)