from datetime import date
import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from pagetree.models import Hierarchy, Section, UserPageVisit
from pagetree.tests.factories import HierarchyFactory, ModuleFactory

from factories import SchoolGroupFactory
from nepi.main.models import AggregateQuizScore, PendingTeachers, Country
from nepi.main.tests.factories import StudentProfileFactory, \
    TeacherProfileFactory, ICAPProfileFactory, \
    CountryAdministratorProfileFactory, \
    SchoolFactory, InstitutionAdminProfileFactory, CountryFactory


class TestCountry(TestCase):
    def test_choices(self):
        country1 = CountryFactory(display_name="Beta")
        country2 = CountryFactory(display_name="Alpha")

        choices = Country.choices()

        self.assertEquals(len(choices), 2)
        self.assertEquals(choices[0], (country2.name, country2.display_name))
        self.assertEquals(choices[1], (country1.name, country1.display_name))


class TestGroup(TestCase):
    def test_unicode(self):
        grp = SchoolGroupFactory()
        self.assertEqual(str(grp), grp.name)

    def test_format_time(self):
        start = date(2007, 1, 5)
        end = date(2007, 12, 25)
        grp = SchoolGroupFactory(start_date=start, end_date=end)

        self.assertEquals(grp.formatted_start_date(), "01/05/2007")
        self.assertEquals(grp.formatted_end_date(), "12/25/2007")

    def test_is_active(self):
        start = date(2007, 1, 5)
        end = date(2007, 12, 25)
        grp = SchoolGroupFactory(start_date=start, end_date=end)

        self.assertFalse(grp.is_active())

        delta = datetime.timedelta(days=-90)
        grp.end_date = datetime.date.today() + delta
        self.assertTrue(grp.is_active())

        delta = datetime.timedelta(days=90)
        grp.end_date = datetime.date.today() + delta
        self.assertTrue(grp.is_active())

    def test_students(self):
        grp = SchoolGroupFactory()

        icap = ICAPProfileFactory()
        country = CountryAdministratorProfileFactory()
        dean = InstitutionAdminProfileFactory()
        teacher = TeacherProfileFactory()
        student = StudentProfileFactory()

        icap.group.add(grp)
        country.group.add(grp)
        dean.group.add(grp)
        teacher.group.add(grp)
        student.group.add(grp)

        self.assertEquals(grp.students().count(), 1)


class TestUserProfile(TestCase):
    def setUp(self):
        self.student = StudentProfileFactory().user
        self.teacher = TeacherProfileFactory().user
        self.school_admin = InstitutionAdminProfileFactory().user
        self.country_admin = CountryAdministratorProfileFactory().user
        self.icap = ICAPProfileFactory().user
        ModuleFactory("main", "/")
        self.hierarchy = Hierarchy.objects.get(name='main')

    def test_user_profile_unis(self):
        self.assertEquals(unicode(self.student), self.student.username)

    def test_display_name(self):
        self.assertEquals(self.student.profile.display_name(),
                          self.student.username)

    def test_user_profile_roles(self):
        self.assertTrue(self.student.profile.is_student())
        self.assertFalse(self.teacher.profile.is_student())
        self.assertFalse(self.school_admin.profile.is_student())
        self.assertFalse(self.country_admin.profile.is_student())
        self.assertFalse(self.icap.profile.is_student())

        self.assertFalse(self.student.profile.is_teacher())
        self.assertTrue(self.teacher.profile.is_teacher())
        self.assertFalse(self.school_admin.profile.is_teacher())
        self.assertFalse(self.country_admin.profile.is_teacher())
        self.assertFalse(self.icap.profile.is_teacher())

        self.assertFalse(self.student.profile.is_institution_administrator())
        self.assertFalse(self.teacher.profile.is_institution_administrator())
        self.assertTrue(
            self.school_admin.profile.is_institution_administrator())
        self.assertFalse(
            self.country_admin.profile.is_institution_administrator())
        self.assertFalse(self.icap.profile.is_institution_administrator())

        self.assertFalse(self.student.profile.is_country_administrator())
        self.assertFalse(self.teacher.profile.is_country_administrator())
        self.assertFalse(self.school_admin.profile.is_country_administrator())
        self.assertTrue(self.country_admin.profile.is_country_administrator())
        self.assertFalse(self.icap.profile.is_country_administrator())

        self.assertFalse(self.student.profile.is_icap())
        self.assertFalse(self.teacher.profile.is_icap())
        self.assertFalse(self.school_admin.profile.is_icap())
        self.assertFalse(self.country_admin.profile.is_icap())
        self.assertTrue(self.icap.profile.is_icap())

        self.assertEquals(self.student.profile.role(), 'student')
        self.assertEquals(self.teacher.profile.role(), 'faculty')
        self.assertEquals(self.country_admin.profile.role(), 'country')
        self.assertEquals(self.icap.profile.role(), 'icap')

    def test_last_location(self):
        self.assertEquals(self.student.profile.last_location(self.hierarchy),
                          self.hierarchy.get_root())

        section = Section.objects.get(slug='two')
        UserPageVisit.objects.create(user=self.student, section=section)
        self.assertEquals(self.student.profile.last_location(self.hierarchy),
                          section)

    def test_percent_complete(self):
        root = self.hierarchy.get_root()
        self.assertEquals(self.student.profile.percent_complete(root), 0)

        # visit section one & child one
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')
        UserPageVisit.objects.create(user=self.student, section=section_one)
        UserPageVisit.objects.create(user=self.student, section=child_one)
        self.assertEquals(self.student.profile.percent_complete(root), 50)

    def test_percent_complete_session(self):
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')

        pct = self.student.profile.percent_complete(section_one)
        self.assertEquals(pct, 0)

        UserPageVisit.objects.create(user=self.student, section=section_one)
        pct = self.student.profile.percent_complete(section_one)
        self.assertEquals(pct, 0)

        UserPageVisit.objects.create(user=self.student, section=child_one)
        pct = self.student.profile.percent_complete(section_one)
        self.assertEquals(pct, 100)

    def test_sessions_completed(self):
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')

        self.assertEquals(self.student.profile.sessions_completed(
            self.hierarchy), 2)

        UserPageVisit.objects.create(user=self.student, section=section_one)
        UserPageVisit.objects.create(user=self.student, section=child_one)
        self.assertEquals(
            self.student.profile.sessions_completed(self.hierarchy), 3)

    def test_joined_groups(self):
        group = SchoolGroupFactory()

        self.assertEquals(self.student.profile.joined_groups().count(), 0)

        self.student.profile.group.add(group)
        self.assertEquals(self.student.profile.joined_groups().count(), 1)

        group.archived = True
        group.save()
        self.assertEquals(self.student.profile.joined_groups().count(), 0)

    def test_managed_groups(self):
        teacher = TeacherProfileFactory().user
        teacher_grp = SchoolGroupFactory(creator=teacher)

        alt_teacher = TeacherProfileFactory().user  # test noise
        alt_teacher_grp = SchoolGroupFactory(creator=alt_teacher,
                                             school=teacher_grp.school)

        school = InstitutionAdminProfileFactory(
            country=teacher_grp.school.country, school=teacher_grp.school).user
        school_grp = SchoolGroupFactory(creator=school,
                                        school=teacher_grp.school)

        country = CountryAdministratorProfileFactory(
            country=teacher_grp.school.country).user
        country_school = SchoolFactory(country=teacher_grp.school.country)
        country_grp = SchoolGroupFactory(creator=country,
                                         school=country_school)

        icap = ICAPProfileFactory().user
        icap_grp = SchoolGroupFactory()

        groups = self.student.profile.get_managed_groups()
        self.assertEquals(groups.count(), 0)

        groups = teacher.profile.get_managed_groups()
        self.assertEquals(groups[0], teacher_grp)

        groups = school.profile.get_managed_groups()
        self.assertEquals(groups.count(), 3)
        self.assertTrue(alt_teacher_grp in groups)
        self.assertTrue(teacher_grp in groups)
        self.assertTrue(school_grp in groups)

        groups = country.profile.get_managed_groups()
        self.assertEquals(groups.count(), 4)
        self.assertTrue(alt_teacher_grp in groups)
        self.assertTrue(teacher_grp in groups)
        self.assertTrue(school_grp in groups)
        self.assertTrue(country_grp in groups)

        groups = icap.profile.get_managed_groups()
        self.assertEquals(groups.count(), 5)
        self.assertTrue(alt_teacher_grp in groups)
        self.assertTrue(teacher_grp in groups)
        self.assertTrue(school_grp in groups)
        self.assertTrue(country_grp in groups)
        self.assertTrue(icap_grp in groups)


class TestPendingTeachers(TestCase):
    def test_unicode(self):
        school = SchoolFactory()
        student = StudentProfileFactory()
        teacher = PendingTeachers.objects.create(user_profile=student,
                                                 school=school)

        label = "%s - %s" % (student, school)
        self.assertEquals(label, teacher.__unicode__())


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

    def test_basics(self):
        aqs = AggregateQuizScore(quiz_class='foo')
        self.assertFalse(aqs.needs_submit())
        self.assertTrue(aqs.unlocked(self.user))
