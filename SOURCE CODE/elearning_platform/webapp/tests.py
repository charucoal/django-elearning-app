from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .forms import *
from .models import * 

# Create your tests here.

################# UNIT TESTS FOR DECORATORS & AUTHENTICATION #################
class DecoratorTests(TestCase):
    
    # set up 2 test users (1 student and teacher)
    def setUp(self):
        self.student_user = User.objects.create_user(username='student', password='password')
        self.student_info = UserInfo.objects.create(user=self.student_user,
                                                    user_type='student',
                                                    first_name='John',
                                                    last_name='Doe',
                                                    email='johndoe@gmail.com')

        self.teacher_user = User.objects.create_user(username='teacher', password='password')
        self.teacher_info = UserInfo.objects.create(user=self.teacher_user,
                                                    user_type='teacher',
                                                    first_name='Jane',
                                                    last_name='Doe',
                                                    email='janedoe@gmail.com')

    # test student login decorator

    # tests redirection for unauthenticated users
    def test_student_login_redirects_unauthenticated_users(self):
        response = self.client.get(reverse('student-home'))  # access a view that uses student_login
        self.assertRedirects(response, '/login/')  # redirect to login if unauthenticated

    # tests redirection for users with no Userinfo instance
    def test_student_login_redirects_users_without_userinfo(self):
        user_no_info = User.objects.create_user(username='no_info', password='password')
        response = self.client.get(reverse('student-home'))
        self.assertRedirects(response, '/login/')  # should redirect to login if no 'userinfo'

    # tests forbidden access for teacher login
    def test_student_login_forbidden_for_teacher(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('student-home'))
        self.assertEqual(response.status_code, 403)  # forbidden access

    # tests success access for student login
    def test_student_login_allows_student(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('student-home'))
        self.assertEqual(response.status_code, 200)  # student can access view

    # test teacher login decorator

    # tests redirection for unauthenticated users
    def test_teacher_login_redirects_unauthenticated_users(self):
        response = self.client.get(reverse('teacher-home'))  # access a view that uses teacher_login
        self.assertRedirects(response, '/login/')  # redirect to login if unauthenticated

    # tests redirection for users with no Userinfo instance
    def test_teacher_login_redirects_users_without_userinfo(self):
        user_no_info = User.objects.create_user(username='no_info', password='password')
        response = self.client.get(reverse('teacher-home'))
        self.assertRedirects(response, '/login/')  # should redirect to login if no 'userinfo'

    # tests forbidden access for teacher login
    def test_teacher_login_forbidden_for_student(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('teacher-home'))
        self.assertEqual(response.status_code, 403)  # forbidden access

    # tests success access for student login
    def test_teacher_login_allows_teacher(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('teacher-home'))
        self.assertEqual(response.status_code, 200)  # teacher can access view

    # test login & registeration page access

    # tests if authenticated user are redirected if accessing login page
    def test_check_login_redirects_authenticated_user_based_on_role(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('login'))  # access a view that uses check_login
        self.assertRedirects(response, reverse('teacher-home'))  # teacher home page
        
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('login'))  # access a view that uses check_login
        self.assertRedirects(response, reverse('student-home'))  # student home page

    # tests if unauthenticated user can access login page
    def test_check_login_allows_unauthenticated_user_to_access(self):
        response = self.client.get(reverse('login'))  # access a view that uses check_login
        self.assertEqual(response.status_code, 200)  # should allow access if not logged in

################# UNIT TESTS FOR MODELS #################

# test key features of UserInfo model
class UserInfoModelTests(TestCase):

    # set up dummy data
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_info = UserInfo.objects.create(
            user=self.user,
            user_type="student",
            first_name="John",
            last_name="Doe",
            email="john.doe@gmail.com"
        )

    # test if display name is set as first_name
    def test_display_name_default(self):
        self.user_info.save()
        self.assertEqual(self.user_info.display_name, "John")

    # test if profile picture is set to default image
    def test_profile_picture_default(self):
        self.user_info.save()
        self.assertEqual(self.user_info.profile_picture, 'profile/default.png')

    # test that second user cannot create a profile with an existing email
    def test_unique_email(self):
        self.user = User.objects.create_user(username='testuser1', password='password')
        try:
            self.user_info = UserInfo.objects.create(
                user=self.user,
                user_type="student",
                first_name="John",
                last_name="Doe",
                email="john.doe@gmail.com"
            )

        except Exception as error:
            self.assertEqual(type(error), IntegrityError)

# test key features of CourseDetails model
class CourseDetailsModelTests(TestCase):

    # set up dummy data
    def setUp(self):
        self.user = User.objects.create_user(username='teacheruser', password='password')
        self.teacher_info = UserInfo.objects.create(
            user=self.user,
            user_type="teacher",
            first_name="Jane",
            last_name="Doe",
            email="janedoe@gmail.com"
        )
        self.course = CourseDetails(
            teacher=self.user,
            course_name="Math 101",
            course_description="Introduction to Mathematics"
        )

    # test that only teacher can create a course
    def test_clean_teacher_validation(self):
        self.teacher_info.user_type = "student"
        self.teacher_info.save()
        with self.assertRaises(ValidationError):
            self.course.clean()

    # test that default header and thumbnail pictures are set if no file given
    def test_course_images_default(self):
        self.course.save()
        self.assertEqual(self.course.course_thumbnail_picture, 'course_pictures/thumbnail/default.jpg')
        self.assertEqual(self.course.course_header_picture, 'course_pictures/header/default.jpg')

# test key features of AssignmentUpload model
class AssignmentUploadModelTests(TestCase):

    # set up dummy data
    def setUp(self):
        self.user = User.objects.create_user(username='teacheruser', password='password')
        self.teacher_info = UserInfo.objects.create(
            user=self.user,
            user_type="teacher",
            first_name="Jane",
            last_name="Doe",
            email="janedoe@gmail.com"
        )
        self.course = CourseDetails.objects.create(
            teacher=self.user,
            course_name="Math 101",
            course_description="Introduction to Mathematics"
        )
        self.lesson = LessonDetails.objects.create(course=self.course, lesson_title="Algebra", lesson_description="Basic Algebra")
        self.assignment = AssignmentUpload(
            lesson=self.lesson,
            name="Assignment 1",
            description="Solve the equations.",
            deadline=timezone.now() + timezone.timedelta(days=1)
        )

    # test if an error is thrown if deadline is set in the past
    def test_clean_deadline_in_the_past(self):
        self.assignment.deadline = timezone.now() - timezone.timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.assignment.clean()

# test key features of MeetingDetails model

class MeetingDetailsTests(TestCase):
    # set up dummy data
    def setUp(self):
        # create test student and teacher users
        self.student = User.objects.create(username="student1")
        self.teacher = User.objects.create(username="teacher1")

        # create test RequestMeeting instance
        self.request_meeting = RequestMeeting.objects.create(
            student=self.student, teacher=self.teacher
        )

    # test that meeting status is set as "closed" when created
    def test_meeting_creation(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        meeting = MeetingDetails.objects.create(
            request=self.request_meeting,
            start_datetime=future_time,
            duration_minutes=30
        )
        self.assertEqual(meeting.meeting_status, "closed")  # default status

    # test that deadline can only be set in the future
    def test_start_datetime_in_future(self):
        past_time = timezone.now() - timezone.timedelta(days=1)
        meeting = MeetingDetails(
            request=self.request_meeting,
            start_datetime=past_time,
            duration_minutes=30
        )
        with self.assertRaises(ValidationError):
            meeting.full_clean()  # should raise ValidationError

    # test that a password of correct length and characters is created for meeting instance 
    def test_generate_password(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        meeting = MeetingDetails.objects.create(
            request=self.request_meeting,
            start_datetime=future_time,
            duration_minutes=30
        )
        meeting.generate_password()
        self.assertIsNotNone(meeting.password)
        self.assertEqual(len(meeting.password), 12)
        self.assertTrue(any(c in string.ascii_letters for c in meeting.password))
        self.assertTrue(any(c in string.digits for c in meeting.password))
        self.assertTrue(any(c in string.punctuation for c in meeting.password))

################# UNIT TESTS FOR FORMS #################

# TESTS FOR LOGGED OUT FORMS

# test for login form
class LoginFormTest(TestCase):

    # test that form is valid with correct data input
    def test_valid_login_form(self):
        form = LoginForm(data={"username": "testuser", "password": "securepassword"})
        self.assertTrue(form.is_valid())

    # test that form is invalid with empty data input
    def test_invalid_login_form(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)

# test for personal particulars form
class RegisterForm1Test(TestCase):

    # test that form is valid with correct data input
    def test_valid_register_form1(self):
        form = RegisterForm1(
            data={
                "user_type": "student",
                "first_name": "John",
                "middle_name": "A",
                "last_name": "Doe",
                "email": "johndoe@gmail.com",
                "email_alert": True,
                "display_name": "JDoe",
                "status_update": "Excited to learn!",
                "display_status": True,
                "profile_picture": None,
            }
        )
        self.assertTrue(form.is_valid())

    # test that form is invalid with empty data input
    def test_invalid_register_form1(self):
        form = RegisterForm1(data={})  # empty form
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)

# test for username & password form
class RegisterForm2Test(TestCase):

    # test that password is valid with valid input
    def test_valid_register_form2(self):
        form = RegisterForm2(
            data={
                "username": "newuser",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            }
        )
        self.assertTrue(form.is_valid())

    # test that password is invalid if passwords are different
    def test_password_mismatch(self):
        form = RegisterForm2(
            data={
                "username": "newuser",
                "password1": "ComplexPass123!",
                "password2": "DifferentPass456!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    # test that form is invalid with empty data input
    def test_invalid_register_form2(self):
        form = RegisterForm2(data={})  # empty form
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password1", form.errors)
        self.assertIn("password2", form.errors)

# TESTS FOR COMMON FORMS (USED BY BOTH STUDENTS AND TEACHERS)

# test for profile settings form
class ProfileSettingsTest(TestCase):
    # set up dummy data
    def setUp(self):
        self.user = User.objects.create(username='johndoe', password='Password123')
        self.user_info = UserInfo.objects.create(
            user = self.user,
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to learn!", 
            display_status=True, profile_picture=None
        )

    # test that form is valid with valid data changes
    def test_valid_profile_settings_form(self):
        form = ProfileSettings(
            instance=self.user_info,
            data={
                "first_name": "Jonathan",
                "middle_name": "A",
                "last_name": "Doe",
                "email": "jonathandoe@gmail.com",
                "email_alert": True,
                "display_name": "J_Doe",
                "status_update": "Ready to learn!",
                "display_status": True,
                "profile_picture": None,
            }
        )
        self.assertTrue(form.is_valid())

    # test that form is invalid with invalid data changes
    def test_invalid_profile_settings_form(self):
        form = ProfileSettings(instance=self.user_info, data={})  # empty form
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)

# test password reset form
class ResetPasswordTest(TestCase):
    # test valid password reset
    def test_valid_reset_password_form(self):
        form = ResetPassword(
            data={
                "password1": "NewPassword123!",
                "password2": "NewPassword123!",
            }
        )
        self.assertTrue(form.is_valid())

    # test invalid password reset (mismatched)
    def test_password_mismatch(self):
        form = ResetPassword(
            data={
                "password1": "NewPassword123!",
                "password2": "MismatchedPassword456!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)  # check there is an error in __all__
        self.assertIn("Passwords do not match.", form.errors["__all__"])  # check the specific error message

    # test invalid password reset (empty)
    def test_empty_reset_password_form(self):
        form = ResetPassword(data={})  # empty form
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)
        self.assertIn("password2", form.errors)

# test feedback forum form 
class AddFeedbackFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='johndoe', password='Password123')
        self.user_info = UserInfo.objects.create(
            user = self.user, user_type = 'teacher',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to learn!", 
            display_status=True, profile_picture=None
        )
        self.course = CourseDetails.objects.create(
            teacher=self.user,
            course_name="Math 101",
            course_description="Introduction to Mathematics"
        )
        self.feedback_forum = FeedbackForum.objects.create(user = self.user, course=self.course, feedback="Great course!")
    
    # test valid feedback
    def test_valid_add_feedback_form(self):
        form = AddFeedbackForm(
            instance=self.feedback_forum,
            data={"feedback": "The course content was very informative."}
        )
        self.assertTrue(form.is_valid())

    # test invalid feedback
    def test_invalid_add_feedback_form(self):
        form = AddFeedbackForm(instance=self.feedback_forum, data={})  # empty form
        self.assertFalse(form.is_valid())
        self.assertIn("feedback", form.errors)

# TEST STUDENT-SPECIFIC FORMS

# test request meeting form
class RequestMeetingFormTest(TestCase):
    def setUp(self):
        # create test users (teachers and students)
        self.teacher_user = User.objects.create_user(
            username="teacher1", password="password"
        )
        self.teacher = UserInfo.objects.create(
            user = self.teacher_user, user_type = 'teacher',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to learn!", 
            display_status=True, profile_picture=None
        )
        self.teacher_user.save()

        self.student_user = User.objects.create_user(
            username="student1", password="password"
        )
        self.student = UserInfo.objects.create(
            user = self.student_user, user_type = 'student',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe2@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to learn!", 
            display_status=True, profile_picture=None
        )
        self.student_user.save()

        # create course and enrollment
        self.course = CourseDetails.objects.create(course_name="Math 101",
                                                   teacher=self.teacher_user,
                                                   course_description="Introduction to Mathematics")
        CourseEnrollments.objects.create(student=self.student_user, course=self.course)

    # test valid e-meet request
    def test_valid_request_meeting_form(self):
        form = RequestMeetingForm(
            data={
                "student": self.student_user.id,
                "teacher": self.teacher_user.id,
                "req_description": "Request for an e-meet",
            },
            student=self.student_user
        )
        self.assertTrue(form.is_valid())

    # test invalid e-meet request
    def test_invalid_request_meeting_form_no_teacher(self):
        form = RequestMeetingForm(
            data={
                "student": self.student_user.id,
                "teacher": "",
                "req_description": "Request for an e-meet",
            },
            student=self.student_user
        )
        self.assertFalse(form.is_valid())
        self.assertIn("teacher", form.errors)

    # ensure that student field is not changeable
    def test_student_field_disabled(self):
        form = RequestMeetingForm(
            data={
                "student": self.student_user.id,
                "teacher": self.teacher_user.id,
                "req_description": "Request for an e-meet",
            },
            student=self.student_user
        )
        self.assertTrue(form.fields['student'].disabled)

    # test that student cannot query a teacher whose course they are not enrolled in
    def test_teacher_queryset_based_on_enrolled_courses(self):
        # another user who is not the teacher of the student's enrolled course
        unrelated_teacher_user = User.objects.create_user(
            username="unrelated_teacher", password="password"
        )
        unrelated_teacher = UserInfo.objects.create(
            user = unrelated_teacher_user, user_type = 'teacher',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe3@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to learn!", 
            display_status=True, profile_picture=None
        )
        unrelated_teacher.save()

        form = RequestMeetingForm(student=self.student_user)
        teachers = form.fields['teacher'].queryset

        # assert that only the teacher of the enrolled course is in the queryset
        self.assertIn(self.teacher_user, teachers)
        self.assertNotIn(unrelated_teacher_user, teachers)

# test filtering form for course search page
class FilterCourseFormTest(TestCase):
    def test_valid_filter_course_form_with_course_descriptor(self):
        form = FilterCourseForm(data={"courseDescriptor": "Math"})
        self.assertTrue(form.is_valid())

    def test_valid_filter_course_form_with_instructor(self):
        form = FilterCourseForm(data={"instructor": "teacher1"})
        self.assertTrue(form.is_valid())

    def test_invalid_filter_course_form_with_empty_fields(self):
        form = FilterCourseForm(data={})
        self.assertTrue(form.is_valid())

    def test_invalid_filter_course_form_with_non_existent_instructor(self):
        form = FilterCourseForm(data={"instructor": "nonexistent_instructor"})
        self.assertTrue(form.is_valid())


# TEST TEACHER-SPECIFIC FORMS

# test search & filter form
class SearchPeopleFormTest(TestCase):
    # test for valid data
    def test_valid_search_people_form(self):
        form = SearchPeopleForm(data={'name': 'John', 'type': 'teacher'})
        self.assertTrue(form.is_valid())

    # test for invalid data (empty)
    def test_invalid_search_people_form_with_empty_fields(self):
        form = SearchPeopleForm(data={})
        self.assertTrue(form.is_valid())

    # test for invalid data (non-existent account_type)
    def test_invalid_search_people_form_with_non_existent_type(self):
        form = SearchPeopleForm(data={'name': 'John', 'type': 'admin'})
        self.assertFalse(form.is_valid())

# test course creation form
class CreateCourseFormTest(TestCase):
    # set up dummy data
    def setUp(self):
        self.user = User.objects.create_user(
            username="teacher", password="password"
        )
        self.teacher = UserInfo.objects.create(
            user = self.user, user_type = 'teacher',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe3@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to teach!", 
            display_status=True, profile_picture=None
        )

    # test valid data
    def test_valid_create_course_form(self):
        form = CreateCourseForm(data={
            'course_name': 'Math 101',
            'course_description': 'Basic Math course'
        })
        form.instance.teacher = self.user
        self.assertTrue(form.is_valid())

    # test invalid data (blank data)
    def test_invalid_create_course_form(self):
        form = CreateCourseForm(data={'course_name': '',
                                      'course_description': ''})
        form.instance.teacher = self.user
        self.assertFalse(form.is_valid())

# test for lesson creation form
class CreateLessonFormTest(TestCase):
    # set up dummy data
    def setUp(self):
        self.user = User.objects.create_user(
            username="teacher", password="password"
        )
        self.teacher = UserInfo.objects.create(
            user = self.user, user_type = 'teacher',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe3@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to teach!", 
            display_status=True, profile_picture=None
        )
        self.course = CourseDetails.objects.create(
            course_name = '',
            course_description = '',
            teacher = self.user
        )

    # test valid data
    def test_valid_create_lesson_form(self):
        form = CreateLessonForm(data={
            'lesson_title': 'Lesson 1',
            'lesson_description': 'Introduction to Math',
        })
        form.instance.course = self.course
        self.assertTrue(form.is_valid())

    # test invalid data (empty data)
    def test_invalid_create_lesson_form(self):
        form = CreateLessonForm(data={'lesson_title': '', 'lesson_description': ''})
        self.assertFalse(form.is_valid())

class DeleteLessonFormTest(TestCase):
    # set up dummy data
    def setUp(self):
        self.user = User.objects.create_user(
            username="teacher", password="password"
        )
        self.teacher = UserInfo.objects.create(
            user = self.user, user_type = 'teacher',
            first_name="John", middle_name="A", last_name="Doe", 
            email="johndoe3@gmail.com", display_name="JDoe", 
            email_alert=True, status_update="Excited to teach!", 
            display_status=True, profile_picture=None
        )
        self.course = CourseDetails.objects.create(teacher=self.user, course_name='Math 101', course_description='Basic Math course')
        self.lesson = LessonDetails.objects.create(course=self.course, lesson_title='Lesson 1', lesson_description='Introduction to Math')

    # test on valid data
    def test_valid_delete_lesson_form(self):
        # self.lesson.lesson_id as dropdown uses id
        form = DeleteLessonForm(data={'lesson_title': self.lesson.lesson_id}, course_id=self.course.course_id)
        self.assertTrue(form.is_valid())

    # test on invalid data
    def test_invalid_delete_lesson_form(self):
        form = DeleteLessonForm(data={'lesson_title': ''}, course_id=self.course.course_id)
        self.assertFalse(form.is_valid())

# test decline meeting form
class DeclineMeetingReqTest(TestCase):
    # test on valid data
    def test_valid_decline_meeting_req_form(self):
        form = DeclineMeetingReq(data={'description': 'Declining reason'})
        self.assertTrue(form.is_valid())

    # test on invalid date (empty)
    def test_invalid_decline_meeting_req_form(self):
        form = DeclineMeetingReq(data={'description': ''})
        self.assertFalse(form.is_valid())
