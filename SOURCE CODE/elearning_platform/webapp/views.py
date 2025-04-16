from asgiref.sync import async_to_sync
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db import transaction
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from channels.layers import get_channel_layer
from collections import defaultdict
from .decorators import *
from .forms import *
from .models import *
from .tasks import *
import datetime

# landing page for website, redirects to login page
def index(request):
    return redirect('login')

# LOGGED OUT VIEWS

@check_login
def user_login(request):
    # initialises empty form or with form data
    form = LoginForm(request.POST or None)

    # handles form submission
    if request.method == "POST":
        # validates form input
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # authenticates user
            user = authenticate(request, username=username, password=password)

            # if authentication is successful
            if user is not None:
                # logs user in
                login(request, user)

                # if no userinfo found, logs user out 
                if not hasattr(request.user, 'userinfo'):
                    logout(request)
                    return redirect('login')
                # if teacher, redirects to teacher's homepage
                elif request.user.userinfo.user_type == 'teacher':
                    return redirect('teacher-home')
                # if student, redirects to student's homepage
                elif request.user.userinfo.user_type == 'student':
                    return redirect('student-home')
            
            # if authentication fails
            else:
                messages.error(request, 'Invalid credentials.')
            
        # if form is invalid
        else:
            # logs form errors from the existing 'form' object
            print("Form Errors:", form.errors)
            return HttpResponse('Internal error', status=400)
    
    return render(request, "webapp/u_login.html", {'login_form': form})

@check_login
def user_signup(request):

    form_data1 = RegisterForm1(request.POST or None, request.FILES) # for user info (with file upload)
    form_data2 = RegisterForm2(request.POST or None) # for user credentials

    # handles form submission
    if request.method == "POST":
        # checks if both forms are valid
        if form_data1.is_valid() and form_data2.is_valid():
    
            user_info = form_data1.save(commit=False)
            user = form_data2.save(commit=False)
            user_info.user = user # associates user info with the user object
            
            # saves user credentials and info to the database
            user.save()
            user_info.save()

            login(request, user) # logs in user after successful signup

            # if teacher, redirects to teacher's homepage
            if request.user.userinfo.user_type == 'teacher':
                return redirect('teacher-home')
            
            # if student, redirects to student's homepage
            else:
                return redirect('student-home')
        
        # if either form is invalid, displays error message
        else:
            if not form_data1.is_valid():  # if form_data1 is invalid
                messages.error(request, 'Invalid user information inputs.')

            if not form_data2.is_valid():  # if form_data2 is invalid
                messages.error(request, 'Invalid user credentials inputs.')

    return render(request, "webapp/u_signup.html", {'register_form1': form_data1,
                                                    'register_form2': form_data2})

# logs user out if logout button is clicked
# redirects back to login page
def user_logout(request):
    logout(request)
    return redirect('login')

# STUDENT-RELATED VIEWS

@student_login
def student_homepage(request):
    student_profile = request.user # gets currently logged-in student's profile
    # gets courses student is enrolled in
    courses_enrolled = CourseEnrollments.objects.filter(student=student_profile, enrollment_status="enrolled").order_by('-created_at')

    # gets all open assignments based on courses enrolled in
    c = courses_enrolled.values_list("course", flat=True)
    assignments = AssignmentSubmission.objects.filter(
        Q(submission_status="due") | Q(submission_status="submitted"),
        assignment__assignment_status=True,
        assignment__lesson__course__in=c,
        student=student_profile
    ).order_by('assignment__deadline')

    progress_data = {} # initialises an empty dictionary to store progress data

    for enrolment in courses_enrolled:
        course = enrolment.course  # get course info from enrolment

        # get all assignments for the course
        total_assignments = AssignmentUpload.objects.filter(lesson__course=course).count()

        # get count of submitted assignments
        submitted_count = AssignmentSubmission.objects.filter(
            assignment__lesson__course=course, student=student_profile, submission_status="submitted"
        ).count()
    
        # calculate progress as percentage
        progress_percentage = (submitted_count / total_assignments) * 100 if total_assignments > 0 else 0

        # store data in dictionary for each course
        progress_data[course.course_id] = {
            "course": course,
            "submitted": submitted_count,
            "total": total_assignments,
            "progress": progress_percentage,
        }

    return render(request, "webapp/s_homepage.html", {'courses_enrolled': courses_enrolled,
                                                      'student_profile': student_profile,
                                                      'dict': progress_data,
                                                      'assignments': assignments})

@student_login
def student_view_courses(request):
    # get all courses
    courses = CourseDetails.objects.all()
    # initialises empty form or with data for filtering through courses
    form = FilterCourseForm(request.GET or None)

    # handles get request
    if request.method == 'GET':
         if 'action' in request.GET: # checks if request as an 'action' parameter
            action = request.GET['action']
            
            # if the action is 'search'
            if action == 'Search':
                # get search terms
                search_descriptor = request.GET.get('courseDescriptor', '')
                search_instructor = request.GET.get('instructor', '')

                # if filter includes course info
                if search_descriptor:
                    filtered_courses = courses.filter(Q(course_name__icontains=search_descriptor) |
                                       Q(course_description__icontains=search_descriptor))
                
                # if filter includes teacher info
                if search_instructor:
                    filtered_courses = filtered_courses.filter(Q(teacher__userinfo__first_name__icontains=search_instructor) |
                                       Q(teacher__userinfo__middle_name__icontains=search_instructor) |
                                       Q(teacher__userinfo__last_name__icontains=search_instructor))
                
                # set courses as newly filtered list
                courses = filtered_courses

            # if the action is 'clear filter', clear form data
            elif action == 'Clear Filters':
                form = FilterCourseForm()
    
    # get count of total courses found
    result_message = f"Courses found: {len(courses)}"
    return render(request, "webapp/s_viewcourses.html", {"courses": courses,
                                                         "form": form,
                                                         "result_message": result_message})

@student_login
def view_course_detail(request):
    # ensure that course exists
    if not request.GET.get('course_id'):
        return HttpResponse("Course ID is required", status=400)
    else:
        course_id = request.GET.get('course_id')
        course_profile = get_object_or_404(CourseDetails, course_id=course_id)

    # gets lesson data if enrolled
    enroll_status = None
    lessons = []  # stores all lessons of this course
    user_submissions = {} # stores all assignment submissions relating to this course
    try:
        enroll_status = CourseEnrollments.objects.filter(student=request.user, course_id=course_profile.course_id).first().enrollment_status
        if enroll_status == 'enrolled' or enroll_status == 'unenrolled':
            lessons = LessonDetails.objects.filter(course=course_profile) # get all lessons for this course

            for lesson in lessons:
                for assignment in lesson.assignments.all():
                    submission = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()
                    user_submissions[assignment.assign_id] = submission  # store the submission in the dictionary
    except:
        pass

    form = AddFeedbackForm() # initialise feedback form
    feedbacks = FeedbackForum.objects.filter(course=course_profile).order_by('-created_at') # get all feedbacks relating to this course

    if request.method == "POST":
        # gets the 'action' parameter of the POST request
        action_type = request.POST.get('action')
        
        # if feedback is posted to forum
        if action_type == "Post!":
            # saves new feedback to database
            # and displays new comment at the top of the forum
            FeedbackForum.objects.create(
                feedback=request.POST.get('feedback'),
                user=request.user,
                course=course_profile
            )

            # sends in-app notification to teacher + all students enrolled in this course
            message = f"Student @{request.user.userinfo.display_name} posted a comment in the {course_profile.course_name} course."
            enrolled_students = CourseEnrollments.objects.filter(course=course_profile) \
                                                        .exclude(student=request.user)

            notifications = []
            for enrollment in enrolled_students:
                student = enrollment.student
                notifications.append(Notification(user_id=student.userinfo.user_id, message=message, notif_type='forum'))

                # uncomment to send email notifications
                # if student.userinfo.email_alert:
                #     async_send_email.delay(student.userinfo.email, "New Course Comment", message)
            
            Notification.objects.bulk_create(notifications)

            teacher = course_profile.teacher.userinfo
            Notification.objects.create(user_id=teacher.user_id, message=message, notif_type='forum')
            
            # uncomment to send email notifications
            # if teacher.email_alert:
            #     async_send_email.delay(teacher.email, "New Course Comment", message)

            return redirect(f"/student/courses/?course_id={course_id}")
        
        # if student clicks on unenroll
        elif action_type == 'Unenroll':
            # deletes all related assignment submission and enrollment details
            AssignmentSubmission.objects.filter(assignment__lesson__course=course_profile, student=request.user).delete()
            CourseEnrollments.objects.filter(student=request.user, course=course_profile).delete()
            return redirect(f"/student/courses/?course_id={course_id}") # redirects to page again (cannot view course materials now)

        # if student clicks on enroll
        elif action_type == 'Enroll':
            # new enrollment instance created
            CourseEnrollments.objects.create(course=course_profile,
                                                student=request.user,
                                                enrollment_status="enrolled")
            
            # assignment submission instance for all assignments created
            today = timezone.now().date()
            assignments_due = AssignmentUpload.objects.filter(lesson__course=course_profile, deadline__gt=today)
            assignments_passed = AssignmentUpload.objects.filter(lesson__course=course_profile, deadline__lt=today)

            with transaction.atomic():
                # create submissions for assignments that are due (without submission status)
                AssignmentSubmission.objects.bulk_create([
                    AssignmentSubmission(
                        assignment=assignment,
                        student=request.user,
                    )
                    for assignment in assignments_due
                ])

                # create submissions for assignments that are passed (set submission_status=True)
                AssignmentSubmission.objects.bulk_create([
                    AssignmentSubmission(
                        assignment=assignment,
                        student=request.user,
                        submission_status="submitted",
                    )
                    for assignment in assignments_passed
                ])
            
            # sends in-app notification to teacher about new enrollment
            message = f"@{request.user.userinfo.display_name} has enrolled into your {course_profile.course_name} course!"
            Notification.objects.create(user=course_profile.teacher,
                                        message=message,
                                        notif_type="enrollment"
                                        )
            
            # uncomment to send email notification to teacher
            # if course_profile.teacher.userinfo.email_alert:
            #     async_send_email.delay(course_profile.teacher.userinfo.email, f"New Enrollment in {course_profile.course_name}", message)
            
            return redirect(f"/student/courses/?course_id={course_id}")
        
        # if student clicks on discontinue course
        elif action_type == 'Discontinue Course':
            CourseEnrollments.objects.filter(student=request.user, course=course_profile).update(enrollment_status="unenrolled")
            return redirect(f"/student/courses/?course_id={course_id}")
        
        # if student clicks on continue course
        elif action_type == 'Continue Course':
            CourseEnrollments.objects.filter(student=request.user, course=course_profile).update(enrollment_status="enrolled")
            return redirect(f"/student/courses/?course_id={course_id}")
        
        # if student submits an assignment
        elif action_type == 'upload' or action_type == 'reupload':
            # check if assignment exists
            try:
                assignment = AssignmentUpload.objects.filter(assign_id=request.POST.get('assignment_id')).first()
            except:
                return HttpResponse("Assignment not found", status=404)
            
            # check that deadline is in the future
            if assignment.deadline < timezone.now():
                    return HttpResponse("Deadline has passed.")
            
            # get submission instance
            submission = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()

            # if its first submission
            if action_type == "upload" and 'upload_file' in request.FILES:
                    if submission:
                        submission.upload_file = request.FILES['upload_file']
                        submission.submission_status = "submitted"
                        submission.save()
            
            # if re-submitting
            elif action_type == "reupload" and 'reupload_file' in request.FILES:
                    if submission:
                        submission.upload_file = request.FILES['reupload_file']
                        submission.save()

            return redirect(f"/student/courses/?course_id={course_id}")

    return render(request, "webapp/s_viewcoursedetail.html", {"course_profile": course_profile,
                                                              "enroll_status": enroll_status,
                                                              "lessons": lessons,
                                                              "form": form,
                                                              "feedbacks": feedbacks,
                                                              "user_submissions": user_submissions})

@student_login
def student_notifications(request):
    # get all notifications for logged-in student
    # ordered by newest first for display
    notifications = Notification.objects.filter(user = request.user).order_by('-created_at')
    
    forum = notifications.filter(notif_type="forum")  # forum notifications
    materials = notifications.filter(notif_type="materials")  # new course materials notifications
    e_meetings = notifications.filter(notif_type="qna")  # QnA or e-meeting notifications

    return render(request, "webapp/s_notificationspage.html", {"forum": forum,
                                                               "materials": materials,
                                                               "e_meetings": e_meetings})

@student_login
def student_profile(request):
    # get logged-in student's details
    student_profile = request.user.userinfo
    # initialise form with user's existing data
    form = ProfileSettings(instance=student_profile)

    if request.method == 'POST':
        # populate form with submitted data
        form = ProfileSettings(request.POST, request.FILES, instance=student_profile)

        if form.is_valid():
            form.save() # save updated data
            messages.success(request, "Changes successfully saved!")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "webapp/s_profile.html", {"form": form,
                                                     "student_profile": student_profile})

@student_login
def student_profile_password(request):
    # get logged-in student's details
    student_profile = request.user
    username = student_profile.username

    # initialise password reset form
    form = ResetPassword(request.POST or None)

    if request.method == "POST":
        # process submitted password reset form
        if form.is_valid():
            new_password = form.cleaned_data['password1']
            student_profile.set_password(new_password)
            student_profile.save()

            update_session_auth_hash(request, student_profile)
            
            messages.success(request, "Password updated successfully!")
            return redirect('student-profile-password')
        
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "webapp/s_passwordpage.html", {"form": form,
                                                          "username": username})

@student_login
def student_view_my_courses(request):
    # get logged-in student's details
    student_profile = request.user

    if request.method == 'POST':
        # retrieve course ID and action type from the form submission
        course_id = request.POST.get('course_id')
        action = request.POST.get('action')

        # handling the respective course actions
        if action == 'Continue Course':
            CourseEnrollments.objects.filter(student=student_profile, course=course_id).update(enrollment_status="enrolled")
            return redirect('student-profile-courses')

        elif action == 'Discontinue Course':
            CourseEnrollments.objects.filter(student=student_profile, course=course_id).update(enrollment_status="unenrolled")
            return redirect('student-profile-courses')

        elif action == 'Remove Course':
            CourseEnrollments.objects.filter(student=student_profile, course=course_id).delete()
            return redirect('student-profile-courses')
    
    # retrieve all courses the student is enrolled in
    courses = CourseEnrollments.objects.filter(student=student_profile)
    return render(request, "webapp/s_coursesettingspage.html", {"courses": courses})

@student_login
def student_request_meeting(request):
    # get logged-in student's details
    student_profile = request.user
    # initialize form with POST data (if have) and student info
    form = RequestMeetingForm(request.POST or None, student=student_profile)

    if request.method == "POST":
        if form.is_valid():
            # save request after adding student info to request
            meeting_request = form.save(commit=False)
            meeting_request.student = student_profile
            meeting_request.save()

            # generate a notification message for the teacher
            message = f"Student @{student_profile.userinfo.display_name} has requested for an e-meeting."
            # create a notification for the teacher
            Notification.objects.create(
                user = meeting_request.teacher,
                message = message,
                notif_type = "qna"
            )

            # uncomment to enable email alerts for teachers who have them enabled
            # if teacher.userinfo.email_alert:
            #         async_send_email.delay(teacher.userinfo.email, "New E-Meeting Request", message)

            messages.success(request, "Request sent successfully!")
            return redirect("student-request-meeting") # redirect to prevent duplicate form submission
        
        else:
            messages.error(request, "Cannot send a request with no teacher or request information.")

    # get all meeting requests made by the student
    req = RequestMeeting.objects.filter(student=student_profile)

    # filter accepted meeting requests, prioritse open meetings and order by meeting with latest datetime
    accepted_requests = req.filter(status="accepted").order_by(Case(
        When(meeting_details__meeting_status="open", then=Value(0)),
        default=Value(1),
        output_field=IntegerField(),
    ),
    '-meeting_details__start_datetime'
    )

    pending_requests = req.filter(status="pending") # get pending meeting requests
    declined_requests = req.filter(status="declined") # get declined meeting requests

    return render(request, "webapp/s_requestmeeting.html", {"form": form,
                                                            "pending_requests": pending_requests,
                                                            "accepted_requests": accepted_requests,
                                                            "declined_requests": declined_requests,})

# TEACHER-RELATED VIEWS

@teacher_login
def teacher_homepage(request):
    # fetch all courses taught by the current teacher, ordered by creation date
    courses = CourseDetails.objects.filter(teacher=request.user).order_by('created_at')
    return render(request, "webapp/t_homepage.html", {"courses": courses})

@teacher_login
def teacher_create_course(request):
    # initialise form
    form = CreateCourseForm()

    if request.method == 'POST':
        form = CreateCourseForm(request.POST, request.FILES)
        form.instance.teacher = request.user # set the current teacher as the course creator

        # check if the form is valid before saving the course
        if form.is_valid():
            course = form.save()
            return redirect(f'../courses/?course_id={course.course_id}') # redirect to course edit page

    return render(request, "webapp/t_createcoursepage.html", {"form": form})

@teacher_login
def teacher_course_setting(request):
    # get course_id
    course_id = request.GET.get('course_id') or request.session.get('course_id')
    try:
        request.session['course_id'] = course_id
        course_details = CourseDetails.objects.get(course_id=course_id)
    except CourseDetails.DoesNotExist:
        return HttpResponse("Course not found", status=404)
    
    # initialise form with existing data
    form = CreateCourseForm(instance=course_details)

    if request.method == 'POST':
        action = request.POST.get('action') # get 'action' from POST request

        # if action is delete
        if action == 'delete':
            # deletes the course and redirects to homepage
            CourseDetails.objects.filter(course_id=course_id).delete()
            return redirect('teacher-home')

        # if action is save
        if action == 'save':
            # update course data and save
            form = CreateCourseForm(request.POST, request.FILES, instance=course_details)
            if form.is_valid():
                form.save()
                messages.error(request, 'Changes saved successfully!')

            else:
                messages.error(request, 'Correct the errors below.')

    return render(request, "webapp/t_coursesettingspage.html", {"course_details": course_details,
                                                                "form": form})

@teacher_login
def teacher_view_course(request):
    course_details = CourseDetails.objects.get(course_id=request.session.get('course_id')) # get course details
    form = AddFeedbackForm()

    lessons = LessonDetails.objects.filter(course=course_details)  # get all lessons under this course
    feedbacks = FeedbackForum.objects.filter(course=course_details).order_by('-created_at') # get all feedback under this course

    if request.method == 'POST':
        action = request.POST.get('action')

        # if action is 'Post!'
        if action == "Post!":
            # save feedback to db
            FeedbackForum.objects.create(
                feedback=request.POST.get('feedback'),
                user=request.user,
                course=course_details
            )

            # send in-app notification to all enrolled students
            message = f"Teacher @{request.user.userinfo.display_name} posted a comment in their {course_details.course_name} course."
            enrolled_students = CourseEnrollments.objects.filter(course=course_details)#.values_list('student', flat=True)

            notifications = []
            for student in enrolled_students:
                notifications.append(Notification(user=student.student, message=message, notif_type='forum'))

                # uncomment to send email notification to students
                # if student.student.userinfo.email_alert:
                #         async_send_email.delay(student.student.userinfo.email, "New Course Comment", message)

            Notification.objects.bulk_create(notifications)
            return redirect('teacher-view-course')
            
    return render(request, "webapp/t_viewcourse.html", {"course_details": course_details,
                                                        "lessons": lessons,
                                                        "feedbacks": feedbacks,
                                                        "form": form})

@teacher_login
def teacher_add_course_items(request):
    # get current course's details
    course_id = request.session.get('course_id')
    course_details = CourseDetails.objects.get(course_id=course_id)

    # initialise the three forms
    lesson_form = CreateLessonForm()
    material_form = AddMaterialForm(course_id=course_id)
    assignment_form = AddAssignmentForm(course_id=course_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        # if a new lesson is added
        if action == 'Create Lesson':
            lesson_form = CreateLessonForm(request.POST)
            lesson_form.instance.course = course_details

            if lesson_form.is_valid():
                # save instance to db
                lesson_form.save()
                return redirect('teacher-view-course')
        
        # if a new material is added
        elif action == 'Add Material to Lesson':
            # get lesson details
            lesson_instance = LessonDetails.objects.get(lesson_id=request.POST.get('lesson'))

            material_form = AddMaterialForm(request.POST, request.FILES, course_id=course_id)
            material_form.instance.lesson = lesson_instance

            if material_form.is_valid():
                material_form.save()

                # notify all students enrolled in the course
                message = f"New materials have been added to the course {course_details.course_name}"
                enrolled_students = CourseEnrollments.objects.filter(course=course_details)

                notifications = []
                for student in enrolled_students:
                    notifications.append(Notification(user=student.student, message=message, notif_type='materials'))

                    # Uncomment to send email notifications to students
                    # if student.student.userinfo.email_alert:
                    #         async_send_email.delay(student.student.userinfo.email, f"New Material added to {course_details.course_name}", message)

                Notification.objects.bulk_create(notifications)

                return redirect('teacher-view-course')
        
        # if a new assignment is added
        elif action == 'Add Assignment to Lesson':
            # get lesson details
            lesson_instance = LessonDetails.objects.get(lesson_id=request.POST.get('lesson'))

            # convert deadline to correct format
            deadline_str = request.POST.get('deadline')
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            deadline = timezone.make_aware(deadline)

            # add relevant information to assignment instance
            assignment_form = AddAssignmentForm(request.POST, request.FILES, course_id=course_id)
            assignment_form.instance.lesson = lesson_instance
            assignment_form.instance.deadline = deadline

            if assignment_form.is_valid():
                # save assignment instance to db
                assignment = assignment_form.save()

                # create assignment submission instances for all students in the course
                # submission_status's default is 'due'
                enrolments = CourseEnrollments.objects.filter(course = course_details)
                for student in enrolments:
                    AssignmentSubmission.objects.create(
                        assignment = assignment,
                        student = student.student
                    )

                return redirect('teacher-view-course')

    return render(request, "webapp/t_additemspage.html", {"course_details": course_details,
                                                          "lesson_form": lesson_form,
                                                          "material_form": material_form,
                                                          "assignment_form": assignment_form})

@teacher_login
def get_materials(request, lesson_id):
    # fetch materials related to the selected lesson
    materials = MaterialUpload.objects.filter(lesson_id=lesson_id).values('material_id', 'name')
    return JsonResponse({'materials': list(materials)})

@teacher_login
def get_assignments(request, lesson_id):
    # fetch assignments related to the selected lesson
    assignments = AssignmentUpload.objects.filter(lesson_id=lesson_id).values('assign_id', 'name')
    return JsonResponse({'assignments': list(assignments)})

@teacher_login
def teacher_delete_course_items(request):
    course_id = request.session.get('course_id')
    course_details = CourseDetails.objects.get(course_id=request.session.get('course_id'))

    # initialise deletion forms
    lesson_delete_form = DeleteLessonForm(course_id=course_id)
    material_delete_form = DeleteMaterialForm(course_id=course_id)
    assignment_delete_form = DeleteAssignmentForm(course_id=course_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        # deletes entire lesson (and associated materials and assignment)
        if action == 'Delete Lesson':
            try:
                LessonDetails.objects.get(lesson_id=request.POST.get('lesson_title')).delete()
                return redirect('teacher-view-course')
            
            except LessonDetails.DoesNotExist:
                return HttpResponse("Lesson not found.", status=404)
        
        # deletes material
        elif action == 'Delete Material':
            try:
                MaterialUpload.objects.get(material_id=request.POST.get('name')).delete()
                return redirect('teacher-view-course')

            except MaterialUpload.DoesNotExist:
                return HttpResponse("Material not found.", status=404)
        
        # deltes assignment
        elif action == 'Delete Assignment':
            try:
                AssignmentUpload.objects.get(assign_id=request.POST.get('name')).delete()
                return redirect('teacher-view-course')

            except AssignmentUpload.DoesNotExist:
                return HttpResponse("Material not found.", status=404)

    return render(request, "webapp/t_deleteitemspage.html", {"course_details": course_details,
                                                             "lesson_delete_form": lesson_delete_form,
                                                             "material_delete_form": material_delete_form,
                                                             "assignment_delete_form": assignment_delete_form})

@teacher_login
def teacher_view_submissions(request):
    # get all assignment submissions for assignments associated to this course
    course_details = CourseDetails.objects.get(course_id=request.session.get('course_id'))
    submissions = AssignmentSubmission.objects.filter(assignment__lesson__course=course_details).order_by('-assignment__deadline')
    
    grouped_submissions = defaultdict(list)

    for submission in submissions:
        grouped_submissions[submission.assignment].append(submission)

    grouped_submissions = dict(grouped_submissions)

    return render(request, "webapp/t_viewsubmissions.html", {"course_details": course_details,
                                                             "grouped_submissions": grouped_submissions})

@teacher_login
def teacher_view_enrolments(request):
    course_id = request.session.get('course_id')
    course_details = CourseDetails.objects.get(course_id=course_id)

    # get all enrollments
    enrolments = CourseEnrollments.objects.filter(course_id=course_id)

    # get all assignments and its count relating to this course
    lessons = LessonDetails.objects.filter(course_id=course_id)
    assignments = AssignmentUpload.objects.filter(lesson__in=lessons)
    total_assignments = assignments.count()

    progress_data = {}

    # gets enrollment and progress data of each student
    for enrolment in enrolments:
        student = enrolment.student
        submitted_count = AssignmentSubmission.objects.filter(
            assignment__in=assignments, student=student, submission_status="submitted"
        ).count()

        # progress is calculated by getting percentage of assignments submitted
        progress = (submitted_count / total_assignments) * 100 if total_assignments > 0 else 0

        progress_data[student.id] = {
            "student": student,
            "submitted": submitted_count,
            "total": total_assignments,
            "progress": progress,
            "enrol_date": enrolment.created_at,
            "status": enrolment.enrollment_status
        }

    if request.method == 'POST':
        action = request.POST.get('action')
        student = request.POST.get("student_id")

        # if action is REMOVE
        if action == "REMOVE":
            # updates enrollment status to "removed"
            CourseEnrollments.objects.filter(student=student, course_id=course_id).update(enrollment_status='removed')

        # if action is ADD BACK
        elif action == "ADD BACK":
            # updates enrollment status to "enrolled"
            CourseEnrollments.objects.filter(student=student, course_id=course_id).update(enrollment_status='enrolled')
        
        redirect('teacher-view-enrolments')

    return render(request, "webapp/t_viewenrolmentspage.html", {"progress_data": progress_data,
                                                                "course_details": course_details})

@teacher_login
def teacher_notifications(request):
    # get all notifications associated with teacher
    # group according to notification type
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    forum_notif = notifications.filter(notif_type='forum')
    enrol_notif = notifications.filter(notif_type='enrollment')
    qna_notif = notifications.filter(notif_type='qna')

    return render(request, 'webapp/t_notificationspage.html', {"forum_notif": forum_notif,
                                                               "enrol_notif": enrol_notif,
                                                               "qna_notif": qna_notif})

@teacher_login
def teacher_search_person(request):
    # initialise search form with data (if any)
    form = SearchPeopleForm(request.GET or None)
    people = UserInfo.objects.all() # get all users

    if request.method == 'GET':
        action_type = request.GET.get('action')

        # if searching
        if action_type == 'Search':
            # get filters
            name = request.GET['name']
            type = request.GET['type'].lower()

            # get relevant matches
            if name or type:
                query = Q()

                if name:
                    query &= (Q(first_name__icontains=name) |
                            Q(middle_name__icontains=name) |
                            Q(last_name__icontains=name) | 
                            Q(display_name__icontains=name))
                
                if type and type.lower() != "all": # skip user_type filtering if 'All' is selected
                    query &= Q(user_type=type)
                
                people = people.filter(query)

            else:
                people = people.none()

        # if filters are cleared
        elif action_type == 'Clear Filters':
            form = SearchPeopleForm()
            
    return render(request, "webapp/t_searchpage.html", {"form": form,
                                                        "people": people,
                                                        "matches": len(people)})

@teacher_login
def teacher_profile(request):
    teacher_profile = request.user # get logged-in teacher's info
    form = ProfileSettings(instance=request.user.userinfo)

    # if profile info is updated
    if request.method == 'POST':
        form = ProfileSettings(request.POST, request.FILES, instance=teacher_profile.userinfo)

        if form.is_valid(): # check validity
            form.save() # save updated info into db
            messages.success(request, "Changes successfully saved!")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "webapp/t_profile.html", {"form": form,
                                                     "teacher_profile": teacher_profile})

@teacher_login
def teacher_profile_password(request):
    teacher_profile = request.user # get logged-in teacher's info
    form = ResetPassword(request.POST or None)

    # if new password is set
    if request.method == "POST":
        if form.is_valid(): # check validity
            new_password = form.cleaned_data['password1']
            teacher_profile.set_password(new_password)
            teacher_profile.save() # save updated password into db

            update_session_auth_hash(request, teacher_profile)
            
            messages.success(request, "Password updated successfully!")
            return redirect('teacher-profile-password')
        
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "webapp/t_passwordpage.html", {"form": form,
                                                          "teacher_profile": teacher_profile})

@teacher_login
def teacher_manage_meetings(request):
    teacher_profile = request.user

    # get all meeting info and group by accepted & pending e-meets
    meetings = RequestMeeting.objects.filter(teacher=teacher_profile)
    accepted = meetings.filter(status="accepted").order_by(
        Case(When(meeting_details__meeting_status="open", then=Value(0)),
             default=Value(1),
             output_field=IntegerField(),
             ),
        '-meeting_details__start_datetime'
    )
    pending = meetings.filter(status="pending")

    # default forms for each e-meeting request (will be replaced if there's a POST error)
    form_instances = {meet.request_id: {"accept_form": AcceptMeetingReq(), "decline_form": DeclineMeetingReq()} for meet in pending}

    if request.method == "POST":
        request_id = request.POST.get('request_id')
        action_type = request.POST.get('action')

        if request_id:
            request_id = int(request_id)
            meeting_request = RequestMeeting.objects.get(request_id=request_id)

            # if teacher accepts e-meeting request
            if action_type == "Accept":
                accept_form = AcceptMeetingReq(request.POST)
                if accept_form.is_valid():
                    # update e-meet instance
                    meeting_request.status = "accepted"
                    meeting_request.save()

                    # save a new e-meeting instance to db
                    meeting_details = accept_form.save(commit=False)
                    meeting_details.request = meeting_request
                    meeting_details.generate_password()
                    meeting_details.save()

                    message = f"Your meeting request with Teacher {meeting_details.request.teacher.userinfo.display_name} has been accepted. The scheduled date and time is: {meeting_details.start_datetime}"

                    Notification.objects.create(
                        user=meeting_request.student,
                        message=message,
                        notif_type="qna"
                    )

                    # Uncomment to send email alerts
                    # if meeting_request.student.userinfo.email_alert:
                    #     async_send_email.delay(meeting_request.student.userinfo.email, "E-Meeting Request Accepted", message)

                    return redirect('teacher-manage-meetings')
                
                else:
                    form_instances[request_id]["accept_form"] = accept_form  # retain errors

            # if teacher declines e-meeting request
            elif action_type == "Decline":
                decline_form = DeclineMeetingReq(request.POST)
                if decline_form.is_valid():
                    meeting_request.status = "declined"
                    meeting_request.status_desc = decline_form.cleaned_data['description']
                    meeting_request.save()

                    message = f"Your meeting request has been declined: {meeting_request.status_desc}"

                    Notification.objects.create(
                        user=meeting_request.student,
                        message=message,
                        notif_type="qna"
                    )

                    # Uncomment to send email alerts
                    # if meeting_request.student.userinfo.email_alert:
                    #     async_send_email.delay(meeting_request.student.userinfo.email, "E-Meeting Request Accepted", message)

                    return redirect('teacher-manage-meetings')
                
                else:
                    form_instances[request_id]["decline_form"] = decline_form  # retain errors

    # prepare form data with possible validation errors
    form_data = [{"meeting": meet, "accept_form": form_instances[meet.request_id]["accept_form"], "decline_form": form_instances[meet.request_id]["decline_form"]} for meet in pending]

    return render(request, "webapp/t_viewmeetings.html", {
        "accepted": accepted,
        "pending": pending,
        "form_data": form_data,
    })

def chat_meeting(request):
    user = request.user # gets user's info (student or teacher)
    meeting_id = request.GET.get('meeting_id')
    meeting_details = MeetingDetails.objects.get(meeting_id=meeting_id)
    is_authenticated = False

    # prevents login if meeting status is expired
    if meeting_details.meeting_status == "expired":
        return HttpResponse("This meeting has expired.")

    if request.method == "POST":
        # if meeting has ended
        if 'end-meeting' == request.POST.get('action'):

            # redirection after meeting ends occurs in joinmeeting.html
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"meeting_{meeting_id}",
                {"type": "meeting_ended"}
            )

            meeting_details.meeting_status = 'expired' # meeting status updated to 'expired'
            meeting_details.save()

        # checks password to allow/deny entry
        if meeting_details.password == request.POST.get('password'):
            is_authenticated = True

        else:
            messages.error(request, 'Incorrect password.')

    return render(request, "webapp/joinmeeting.html", {"meeting_details": meeting_details,
                                                       "user": user,
                                                       "is_authenticated": is_authenticated})
