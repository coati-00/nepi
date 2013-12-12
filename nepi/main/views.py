from annoying.decorators import render_to
from django import forms
from django.contrib.auth import authenticate, login, logout
from nepi.main.models import Course, UserProfile, School
from nepi.main.models import Country, PendingRegister
from nepi.main.forms import LoginForm, CreateAccountForm
from nepi.main.forms import AddSchoolForm, CreateCourseForm, ContactForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
# from django.template import Context, Template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import RequestContext
from pagetree.helpers import get_section_from_path, get_module
# import json
from pagetree.models import Section
# from captcha.fields import CaptchaField
# from django.utils import simplejson
# from django.views.generic.edit import CreateView
# from captcha.models import CaptchaStore
# from captcha.helpers import captcha_image_url
# from django.http import HttpResponse
# import json

UNLOCKED = ['resources']  # special cases


class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if isinstance(items, type({})):
                ctx = RequestContext(request)
                return render_to_response(self.template_name,
                                          items,
                                          context_instance=ctx)
            else:
                return items

        return rendered_func


def _edit_response(request, section, path):
    first_leaf = section.hierarchy.get_first_leaf(section)

    return dict(section=section,
                module=get_module(section),
                root=section.hierarchy.get_root(),
                leftnav=_get_left_parent(first_leaf),
                prev=_get_previous_leaf(first_leaf),
                next=first_leaf.get_next())


@user_passes_test(lambda u: u.is_superuser)
@rendered_with('main/edit_page.html')
def edit_page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _edit_response(request, section, path)


def edit_resources(request, path):
    section = get_section_from_path(path, "resources")
    return _edit_response(request, section, path)


def resources(request, path):
    section = get_section_from_path(path, "resources")
    return _response(request, section, path)


@login_required
@rendered_with('main/page.html')
def page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _response(request, section, path)


def _get_left_parent(first_leaf):
    leftnav = first_leaf
    if first_leaf.depth == 4:
        leftnav = first_leaf.get_parent()
    elif first_leaf.depth == 5:
        leftnav = first_leaf.get_parent().get_parent()
    return leftnav


def _response(request, section, path):
    h = section.hierarchy
    if request.method == "POST":
        # user has submitted a form. deal with it
        proceed = True
        for p in section.pageblock_set.all():
            if hasattr(p.block(), 'needs_submit'):
                if p.block().needs_submit():
                    prefix = "pageblock-%d-" % p.id
                    data = dict()
                    for k in request.POST.keys():
                        if k.startswith(prefix):
                            data[k[len(prefix):]] = request.POST[k]
                    p.block().submit(request.user, data)
                    if hasattr(p.block(), 'redirect_to_self_on_submit'):
                        proceed = not p.block().redirect_to_self_on_submit()

        if request.is_ajax():
            json = simplejson.dumps({'submitted': 'True'})
            return HttpResponse(json, 'application/json')
        elif proceed:
            return HttpResponseRedirect(section.get_next().get_absolute_url())
        else:
            # giving them feedback before they proceed
            return HttpResponseRedirect(section.get_absolute_url())
    else:
        first_leaf = h.get_first_leaf(section)
        ancestors = first_leaf.get_ancestors()
        profile = UserProfile.objects.filter(user=request.user)[0]

        # Skip to the first leaf, make sure to mark these sections as visited
        if (section != first_leaf):
            profile.set_has_visited(ancestors)
            url = "/%s%s" % ("pages", first_leaf.get_absolute_url())
            return HttpResponseRedirect(url)

        # the previous node is the last leaf, if one exists.
        prev = _get_previous_leaf(first_leaf)
        next_page = first_leaf.get_next()

        # Is this section unlocked now?
        can_access = _unlocked(first_leaf, request.user, prev, profile)
        if can_access:
            profile.set_has_visited([section])

        module = None
        if not first_leaf.is_root() and len(ancestors) > 1:
            module = ancestors[1]

        # specify the leftnav parent up here.
        leftnav = _get_left_parent(first_leaf)

        return dict(section=first_leaf,
                    accessible=can_access,
                    module=module,
                    root=ancestors[0],
                    previous=prev,
                    next=next_page,
                    depth=first_leaf.depth,
                    request=request,
                    leftnav=leftnav)


def accessible(section, user):
    try:
        previous = section.get_previous()
        return _unlocked(section, user, previous, user.get_profile())
    except AttributeError:
        return False


def is_accessible(request, section_slug):
    section = Section.objects.get(slug=section_slug)
    previous = section.get_previous()
    response = {}

    if _unlocked(section, request.user, previous, request.user.get_profile()):
        response[section_slug] = "True"

    json = simplejson.dumps(response)
    return HttpResponse(json, 'application/json')


# def test_view(request):
#     if request.POST:
#         form = CaptchaTestForm(request.POST)

#         # Validate the form: the captcha field will automatically
#         # check the input
#         if form.is_valid():
#             human = True
#     else:
#         form = CaptchaTestForm()

#     return render_to_response('template.html',locals())


# class AjaxExampleForm(CreateView):
#     template_name = ''
#     form_class = AjaxForm

#     def form_invalid(self, form):
#         if self.request.is_ajax():
#             to_json_responce = dict()
#             to_json_responce['status'] = 0
#             to_json_responce['form_errors'] = form.errors

#             to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
#             to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

#             return HttpResponse(json.dumps(to_json_responce), content_type='application/json')

#     def form_valid(self, form):
#         form.save()
#         if self.request.is_ajax():
#             to_json_responce = dict()
#             to_json_responce['status'] = 1

#             to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
#             to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

#             return HttpResponse(json.dumps(to_json_responce), content_type='application/json')


# def captchatest(request):
#     return render_to_response("main/catchatest.html")


# def clear_state(request):
#     try:
#         request.user.get_profile().delete()
#     except UserProfile.DoesNotExist:
#         pass

#     # clear quiz
#     import quizblock
#     quizblock.models.Submission.objects.filter(user=request.user).delete()

#     # clear prescription writing
#     PrescriptionWritingActivityState.objects.filter(
#     \ user=request.user).delete()

#     # clear treatment choices
#     TreatmentChoiceActivityState.objects.filter(user=request.user).delete()

#     # clear virtual patient
#     VirtualPatientActivityState.objects.filter(user=request.user).delete()

#     return HttpResponseRedirect(reverse("index"))

# def _get_previous_leaf(section):
#     depth_first_traversal = section.get_root().get_annotated_list()
#     for (i, (s, ai)) in enumerate(depth_first_traversal):
#         if s.id == section.id:
#             # first element is the root, so we don't want to return that
#             prev = None
#             while i > 1 and not prev:
#                 (node, x) = depth_first_traversal[i - 1]
#                 if node and len(node.get_children()) > 0:
#                     i -= 1
#                 else:
#                     prev = node
#             return prev
#     # made it through without finding ourselves? weird.
#     return None

# #UNLOCKED = ['welcome', 'resources']  # special cases


# def _unlocked(section, user, previous, profile):
#     """ if the user can proceed past this section """
#     if (not section or
#         section.is_root() or
#         profile.get_has_visited(section) or
#         section.slug in UNLOCKED or
#             section.hierarchy.name in UNLOCKED):
#         return True

#     if not previous or previous.is_root():
#         return True

#     for p in previous.pageblock_set.all():
#         if hasattr(p.block(), 'unlocked'):
#             if p.block().unlocked(user) is False:
#                 return False

#     if previous.slug in UNLOCKED:
#         return True

#     # Special case for virtual patient as this activity was too big to fit
#     # into a "block"
#     if (previous.label == "Virtual Patient" and
#             not VirtualPatientActivityState.is_complete(user)):
#         return False

#     return profile.get_has_visited(previous)


"""General Views"""


@render_to('main/index.html')
def index(request):
    return dict()


def logout_view(request):
    """When user logs out redirect to home page."""
    logout(request)
    return HttpResponseRedirect('/')


def contact(request):
    '''Contact someone regarding the project - WHO???'''
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['cdunlop@columbia.edu']
            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return render_to_response('thanks.html')
    else:
        form = ContactForm()  # An unbound form

    return render(request, 'main/contact.html', {
        'form': form,
    })


def thanks_course(request, course_id):
    """Returns thanks for joining course page."""
    # XXX: F821 undefined name 'form'
    return render(request, 'student/thanks_course.html', {'form': form, })


"""More General Views"""


def nepi_login(request):
    '''Allow user to login.'''
    if request.method == 'POST':  # If the form has been submitted...
        form = LoginForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/home/")
                else:
                    return HttpResponseRedirect("/")
            else:
                return HttpResponseRedirect("/")
    else:
        form = LoginForm()  # An unbound form

    return render(request, 'main/login.html', {
        'form': form,
    })


def home(request):
    '''Return homepage appropriate for user type.'''
    try:
        # user = User.objects.get(pk=request.user.pk)
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.profile_type == 'ST':
            #  modules = LearningModule.objects.all()
            courses = user_profile.course.all()
            return render(request, 'student/stindex.html',
                          {'courses': courses})

        elif user_profile.profile_type == 'TE':
            pass
        # courses = user_profile.course.all()
        # return render(request, 'teacher/teindex.html',
        #               {'courses': courses})
        elif user_profile.profile_type == 'IC':
            pending_teachers = PendingRegister.objects.filter(profile_type='TE')
            schools = School.objects.all()
            return render(request, 'icap/icindex.html',
                          {'schools': schools,
                              'pending_teachers': pending_teachers})
        #return render_to_response('main/icindex.html/')
        else:
            return HttpResponseRedirect('/')
    except User.DoesNotExist:
        return HttpResponseRedirect('/')


def register(request):
    '''This is based off of django-request - creates a new user account.'''
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            try:
                User.objects.get(username=request.POST['username'])
                raise forms.ValidationError("this username already exists")
            except User.DoesNotExist:
                if 'password1' in request.POST and 'password2' in request.POST:
                    if request.POST['password1'] != request.POST['password2']:
                        raise forms.ValidationError(
                            "passwords dont match each other")

                    if request.POST['password1'] == request.POST['password2']:
                        new_user = User.objects.create_user(
                            username=request.POST['username'],
                            email=request.POST['email'],
                            password=request.POST['password1'])
                        new_user.first_name = request.POST['first_name']
                        new_user.last_name = request.POST['last_name']
                        new_user.save()
                        new_profile = UserProfile(user=new_user)
                        try:
                            get_country = \
                                Country.objects.get(
                                    name=request.POST['country'])
                            new_profile.country = get_country
                            new_profile.save()
                        except Country.DoesNotExist:
                            get_country = \
                                Country(
                                    name=request.POST['country'])
                            get_country.save()
                            new_profile.country = get_country
                            new_profile.save()
                        new_profile.profile_type = 'ST'
                        new_profile.save()
                        is_teacher = request.POST.get('is_teacher', 'ST')
                        if is_teacher == 'TE':
                            register = PendingRegister(user=new_user,
                                                       userprofile=new_profile,
                                                       profile_type='TE')
                            register.save()
                            recipients = ['cdunlop@columbia.edu']
                            if request.POST['email']:
                                sender = request.POST['email']
                            else:
                                sender = "unknown@unknown.com"
                            subject = 'Teacher Status Requested'
                            message = str(new_user.first_name) \
                                + " " + str(new_user.last_name) \
                                + " has requested teacher status."
                            # + get_school.name + "."
                            from django.core.mail import send_mail
                            send_mail(subject, message, sender, recipients)
                            return render_to_response(
                                'main/thanks_teacher.html')
                        return HttpResponseRedirect('/thank_you_reg/')

            else:
                raise forms.ValidationError("You are missing a password.")

    else:
        form = CreateAccountForm()

    return render(request, 'registration_form.html', {
        'form': form,
    })


############
"""NEPI Peoples Views"""


def add_school(request):
    """This is intended to be for ICAP personel to register
    Schools in the program."""
    if request.method == 'POST':
        form = AddSchoolForm(request.POST)
        try:
            get_country = Country.objects.get(name=request.POST['country'])
            try:
                School.objects.get(
                    name=request.POST['name'],
                    country=get_country)
                raise forms.ValidationError("This school already exists.")
            except School.DoesNotExist:
                new_school = School(
                    name=request.POST['name'],
                    country=get_country
                )
                new_school.save()
                return HttpResponseRedirect('/thank_you_school/')
        except Country.DoesNotExist:
            new_country = Country(name=request.POST['country'])
            new_country.save()
            new_school = School(
                name=request.POST['name'],
                country=new_country
            )
            new_school.save()
            return HttpResponseRedirect('/thank_you_school/')

    else:
        form = AddSchoolForm()  # An unbound form

    return render(request, 'icap/add_school.html', {
        'form': form,
    })


def view_schools(request):
    """Return all school for viewing to ICAPP personnel."""
    schools = School.objects.all()
    return render(request, 'icap/view_schools.html', {'schools': schools})


def conf_teacher(request):
    """This is intended to be for ICAP personel to
    confirm teachers in the program."""
    conf_teach = UserProfile.objects.filter(is_teacher=True)
    return render(request,
                  'icap/show_teachers.html',
                  {'conf_teach': conf_teach})


def confirm_teacher(request, prof_id, schl_id):
    userprofile = UserProfile.object.get(pk=prof_id)
    school = School.object.get(pk=schl_id)
    userprofile.profile_type = 'TE'
    userprofile.school = school
    userprofile.save()
    return HttpResponseRedirect('/confirm/')


def deny_teacher(request, prof_id, schl_id):
    pend_reg = PendingRegister.object.get(userprofile=prof_id, school=schl_id)
    pend_reg.delete()
    return HttpResponseRedirect('/delete_teacher/')


def icapp_view_students(request):
    """Allow teacher to view progress of students within a
    course."""
    users = User.objects.all()
    # filter(user_profile.profile_type='ST')
    # find and return users with certain kind of profile
    students = []
    for u in users:
        try:
            profile = UserProfile.objects.get(user=u)
            if profile.profile_type == 'ST':
                print profile
                print u
                students.append(u)
        except UserProfile.DoesNotExist:
            pass
    # students# = UserProfile.objects.filter(profile_type='ST')
    # Profile.objects.filter(profile_type='ST')
    return render(request,
                  'icap/icapp_show_students.html',
                  {'students': students})


def view_region(request):
    """Allow ICAP personnel to view a region, will show schools,
    countries and teachers in region and their classes"""
    pass


"""Teacher Views"""


def create_course(request):
    """This is intended to allow teachers to create courses
    which use the learning modules."""
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        if form.is_valid():
            semester = request.POST['semester']
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            name = request.POST['name']
            get_school = School.objects.get(name=user_profile.school)
            #  need to associate with hierarchy
            new_course = Course(semester=semester,
                                start_date=start_date,
                                end_date=end_date,
                                school=get_school,
                                name=name)
            new_course.save()
            return HttpResponseRedirect('/thank_you/')
        else:
                raise forms.ValidationError(
                    "Please enter appropriate fields for the form.")

    else:
        form = CreateCourseForm()  # An unbound form

    return render(request, 'main/create_course.html', {
        'form': form,
    })


def edit_course(request, crs_id):
    """This is intended to allow teachers to create courses
    which use the learning modules."""
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        if form.is_valid():
            semester = request.POST['semester']
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            name = request.POST['name']
            get_country = Country.objects.get(country=user_profile.country)
            get_school = School.objects.get(name=user_profile.school)
            new_course = Course(semester=semester,
                                start_date=start_date,
                                end_date=end_date,
                                country=get_country,
                                school=get_school,
                                name=name)
            new_course.save()
            return HttpResponseRedirect('/thank_you/')
        else:
                raise forms.ValidationError(
                    "Please enter appropriate fields for the form.")

    else:
        form = CreateCourseForm()  # An unbound form

    return render(request, 'teacher/create_course.html', {
        'form': form,
    })


def course_students(request, crs_id):
    users = User.objects.all()
    course_students = []
    for u in users:
        try:
            profile = UserProfile.objects.get(user=u)
            if profile.profile_type == 'ST':
                courses = profile.course_set.all()
                for c in courses:
                    if c.crs_id == crs_id:
                        course_students.add(profile)
                        # [u][profile][c])
        except UserProfile.DoesNotExist:
            pass

    return render(request,
                  'teacher/show_students.html',
                  {'course_students': course_students})


# def courses(request):
#     courses = user_profile.course.all()
#     return render(request,
#                   'teacher/courses.html',
#                   {'courses': courses})


def remove_student(request, stud_id, cors_id):
    """Allow teacher to remove student."""
    pass


def course_results(request):
    pass


def course_created(request):
    pass


def confirm_student(request, st_id, class_id):
    """Allow teacher to confirm student is in course."""
    userprofile = UserProfile.object.get(pk=request.user.pk)
    course = Course.object.get(pk=st_id)
    userprofile.course = course
    userprofile.school = course.school
    userprofile.save()
    return HttpResponseRedirect('/confirm/')


def view_pending_students(request):
    """Allow teacher to view students claiming
     they are enrolled in a course."""
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    teachers_courses = user_profile.course_set.all()
    #for each in teachers_courses:
    #    view_pending_students =
    # PendingRegister.objects.filter(profile_type='ST', course=each)
    return render(request,
                  'main/pending_students.html',
                  {'teachers_courses': teachers_courses})


"""Student Views"""


#def find_course(request):
#    pass

def join_course(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    country = user_profile.country
    schools = School.objects.filter(country=country)
    return render(request,
                  'student/join_course.html',
                  {'schools': schools,
                   'country': country
                   }
                  )


def view_courses(request, schl_id):
    school = School.objects.get(pk=schl_id)
    courses = Course.objects.filter(school=school)
    return render(request,
                  'student/view_courses.html',
                  {'courses': courses, 'school': school})


# def join_course(request, crs_id):
#     user = request.user
#     user_profile = UserProfile.objects.get(user=user)
#     course = Course.objects.get(pk=crs_id)
#     register = PendingRegister(user=user,
#                                userprofile=user_profile,
#                                course=course)
#     register.save()
#     return render(request, 'main/thanks_course.html', {'course': course})


def _get_previous_leaf(section):
    depth_first_traversal = section.get_root().get_annotated_list()
    for (i, (s, ai)) in enumerate(depth_first_traversal):
        if s.id == section.id:
            # first element is the root, so we don't want to return that
            prev = None
            while i > 1 and not prev:
                (node, x) = depth_first_traversal[i - 1]
                if node and len(node.get_children()) > 0:
                    i -= 1
                else:
                    prev = node
            return prev
    # made it through without finding ourselves? weird.
    return None


def _unlocked(section, user, previous, profile):
    """ if the user can proceed past this section """
    if (not section or
        section.is_root() or
        profile.get_has_visited(section) or
        section.slug in UNLOCKED or
            section.hierarchy.name in UNLOCKED):
        return True
