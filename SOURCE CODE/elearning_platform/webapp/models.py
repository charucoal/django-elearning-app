from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import secrets, string

# model to store user information (for both students and teachers)
class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=[("student", "Student"), ("teacher", "Teacher")])
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=False, default='')
    last_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    email_alert = models.BooleanField(default=False)
    status_update = models.TextField(default="Hello! I'm on Voyage!")
    display_status = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profile/', null=True,  blank=True, default='profile/default.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # if display_name not set, default to user's first name
        if not self.display_name:
            self.display_name = self.first_name

        # if profile_picture not set, default to default profile picture
        if not self.profile_picture:
            self.profile_picture = self._meta.get_field('profile_picture').get_default()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username}) - {self.user_type.capitalize()}"

# model to store course information
# each course is associated with a teacher user
class CourseDetails(models.Model):
    course_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses_taught")
    course_name = models.CharField(max_length=255)
    course_description = models.TextField()
    course_thumbnail_picture = models.ImageField(upload_to='course_pictures/thumbnail', null=True,  blank=True, default='course_pictures/thumbnail/default.jpg')
    course_header_picture = models.ImageField(upload_to='course_pictures/header', null=True,  blank=True, default='course_pictures/header/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def clean(self):
        # ensures that only teachers can create courses
        if self.teacher.userinfo.user_type != 'teacher':
            raise ValidationError("Selected user must be a teacher.")

    def save(self, *args, **kwargs):
        # if course_thumbnail_picture not set, default to default thumbnail picture
        if not self.course_thumbnail_picture:
            self.course_thumbnail_picture = self._meta.get_field('course_thumbnail_picture').get_default()

        # if course_header_picture not set, default to default header picture
        if not self.course_header_picture:
            self.course_header_picture = self._meta.get_field('course_header_picture').get_default()

        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_name} by {self.teacher.userinfo.first_name} {self.teacher.userinfo.last_name}"

# model to store lesson information
# each lesson is associated with a course
class LessonDetails(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(CourseDetails, on_delete=models.CASCADE)
    lesson_title = models.CharField(max_length=255)
    lesson_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lesson: {self.lesson_title} (Course: {self.course.course_name})"

# model to store material information
# each material is associated with a lesson
class MaterialUpload(models.Model):
    material_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(LessonDetails, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    upload_file = models.FileField(upload_to='materials/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Material: {self.name} (Lesson: {self.lesson.lesson_title})"

# model to store assignment information
# each assignment is associated with a lesson
class AssignmentUpload(models.Model):
    assign_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(LessonDetails, on_delete=models.CASCADE, null=True, related_name='assignments')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, default='Refer to attached file.')
    upload_file = models.FileField(upload_to='assignments/', null=True)
    deadline = models.DateTimeField()
    assignment_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.pk:
            # ensures that deadline set is in the future
            if self.deadline <= timezone.now():
                raise ValidationError({"deadline": 'The deadline must be in the future.'})
        
    def __str__(self):
        return f"Assignment: {self.name} (Lesson: {self.lesson.lesson_title}, Deadline: {self.deadline.strftime('%Y-%m-%d %H:%M')})"

# model to store notification information
# each notification is associated with a user (who will receive it)
class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ("forum", "Forum"),
        ("materials", "Materials"), # specifically for student
        ("enrollment", "Enrollment"), # specifically for student
        ("qna", "QnA"),
        ("others", "Others"),
    ]

    notif_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.first_name} {self.user.last_name}: [{self.get_notif_type_display()}] {self.message}"

# model to store feedbacks
# each feedback is associated with a course (forum) and user (who posted the feedback)
class FeedbackForum(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseDetails, on_delete=models.CASCADE, null=True)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.userinfo.first_name} {self.user.userinfo.last_name} on {self.course.course_name}: {self.feedback[:20]}..."

# model to store course enrollment info
# each enrollment is associated with a course and a student
class CourseEnrollments(models.Model):
    ENROLLMENT_STATUS_CHOICES = [
        ("enrolled", "Enrolled"),
        ("unenrolled", "Unenrolled"),
        ("removed", "Removed"),
    ]

    enroll_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(CourseDetails, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrolled_courses")
    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.userinfo.first_name} {self.student.userinfo.last_name} - {self.course.course_name} ({self.get_enrollment_status_display()})"

# model to store students' assignment submissions
# each submission is associated with original assignment and student (who submitted)
class AssignmentSubmission(models.Model):
    SUBMISSION_STATUS = [
        ("submitted", "Submitted"),
        ("overdue", "Overdue"),
        ("due", "Due"),
    ]

    upload_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(AssignmentUpload, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_submissions')
    upload_file = models.FileField(upload_to='uploaded_assignments/', null=True)
    submission_status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default="due")
    submitted_on = models.DateTimeField(auto_now=True) # updated if assignment is resubmitted
    
    def __str__(self):
        return f"{self.student.userinfo.first_name} {self.student.userinfo.last_name} - {self.assignment.name} ({self.get_submission_status_display()})"

# model to store e-meeting request data
# each request is associated with a student (who requested) and teacher (who receives the request)
class RequestMeeting(models.Model):
    REQ_STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    request_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, related_name="meeting_requests", on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, related_name="received_meeting_requests", on_delete=models.CASCADE)
    req_description = models.TextField()
    status = models.CharField(max_length=20, choices=REQ_STATUS, default="pending")
    status_desc = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting Request: {self.student.userinfo.first_name} → {self.teacher.userinfo.first_name} ({self.get_status_display()})"

# model to store e-meeting details
# each e-meeting is associated with the original e-meet request (which is associated to the student and teacher)
class MeetingDetails(models.Model):
    STATUS = [
        ("closed", "Closed"),
        ("open", "Open"),
        ("expired", "Expired"),
    ]
    
    meeting_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(RequestMeeting, related_name="meeting_details", on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()  
    duration_minutes = models.IntegerField()
    meeting_status = models.CharField(max_length=20, choices=STATUS, default="closed")
    password = models.CharField(max_length=16, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Meeting: {self.request.student.userinfo.first_name} & {self.request.teacher.userinfo.first_name} on {self.start_datetime.strftime('%Y-%m-%d %H:%M')} ({self.get_meeting_status_display()})"

    def clean(self):
        if not self.pk:
            # ensures that start time is in the future
            if self.start_datetime <= timezone.now():
                raise ValidationError({"start_datetime": "Start time must be in the future."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # generates a password when an e-meet is created
    def generate_password(self):
        # generates a random password using the secrets module
        password = [
            secrets.choice(string.ascii_letters),  # at least one letter
            secrets.choice(string.digits),         # at least one digit
            secrets.choice(string.punctuation)     # at least one punctuation character
        ]
        
        # fill the rest of the password with random choices from all character sets
        password += [secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(9)]
        
        # shuffle to ensure the password isn't predictable
        secrets.SystemRandom().shuffle(password)
        
        # join the list of characters into a final password string
        self.password = ''.join(password)
        self.save()

