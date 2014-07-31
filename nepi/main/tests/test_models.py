from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from factories import GroupFactory
from nepi.main.models import Group, UserProfile, Country, School, \
    AggregateQuizScore
from nepi.main.tests.factories import HierarchyFactory


class TestGroup(TestCase):
    def test_unicode(self):
        c = GroupFactory()
        self.assertEqual(str(c), "A Group")


class TestUserProfile(TestCase):
    def setUp(self):
        self.student = User(first_name="student", last_name="student",
                            username="student", email="student@email.com",
                            password="student")
        self.student.save()
        self.teacher = User(first_name="teacher", last_name="teacher",
                            username="teacher", email="teacher@email.com",
                            password="teacher")
        self.teacher.save()
        self.icap = User(first_name="icapp", last_name="icapp",
                         username="icapp", email="icapp@email.com",
                         password="icapp")
        self.icap.save()
        self.country1 = Country(name='LS')
        self.country1.save()
        self.country2 = Country(name='GM')
        self.country1.save()
        self.country3 = Country(name='TG')
        self.country1.save()
        self.school = School(country=self.country1, name='School 1')
        self.school.save()
        self.group = Group(school=self.school,
                           name="Group",
                           start_date=datetime.now(),
                           end_date=datetime.now())
        self.group.save()
        self.student_profile = UserProfile(
            user=self.student, profile_type='ST', country=self.country1,
            school=self.school)
        self.student_profile.save()
        self.teacher_profile = UserProfile(
            user=self.teacher, profile_type='TE', country=self.country1,
            school=self.school)
        self.teacher_profile.save()
        self.icap_profile = UserProfile(
            user=self.icap, profile_type='IC',
            country=self.country1, school=self.school)
        self.icap_profile.save()

    def test_user_profile_unis(self):
        self.assertEquals(unicode(self.student), "student")
        self.assertEquals(unicode(self.teacher), "teacher")
        self.assertEquals(unicode(self.icap), "icapp")


class TestAggregateQuizScore(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

        hierarchy = HierarchyFactory()

        hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page One',
            'slug': 'page-one',
            'pageblocks': [{
                'label': 'pretest page one',
                'css_extra': 'foo',
                'block_type': 'Quiz',
                'rhetorical': False,
                'description': 'the first quiz',
                'questions': []},
            ],
            'children': [],
        })
        hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page Two',
            'slug': 'page-two',
            'pageblocks': [{
                'label': 'pretest page two',
                'css_extra': 'foo',
                'block_type': 'Quiz',
                'rhetorical': False,
                'description': 'the second quiz',
                'questions': []},
            ],
            'children': [],
        })
        hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page Three',
            'slug': 'page-three',
            'pageblocks': [{
                'label': 'pretest page three',
                'css_extra': 'bar',
                'block_type': 'Quiz',
                'rhetorical': False,
                'description': 'the third quiz',
                'questions': []},
            ],
            'children': [],
        })

    def test_quizzes(self):
        quizzes = AggregateQuizScore(quiz_class='foo').quizzes().order_by(
            'description')
        self.assertEquals(quizzes.count(), 2)

        self.assertEquals(quizzes[0].description, 'the first quiz')
        self.assertEquals(quizzes[1].description, 'the second quiz')
