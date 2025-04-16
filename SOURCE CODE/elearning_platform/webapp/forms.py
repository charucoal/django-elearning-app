from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm

# LOGGED OUT FORMS

# login form (username and passowrd)
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        label=''
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label=''
    )

# registration form 1 (personal particulars)
class RegisterForm1(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['user_type', 'first_name', 'middle_name', 'last_name', 'email', 'email_alert', 'display_name', 'status_update', 'display_status', 'profile_picture']

# registration form 2 (username and password)
class RegisterForm2(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

# FORMS COMMON TO STUDENTS AND TEACHERS

# edit personal particulars form
class ProfileSettings(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'email_alert', 'display_name', 'status_update', 'display_status', 'profile_picture']

# reset password form
class ResetPassword(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}),
        label="New Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label="Confirm Password"
    )

    # ensures that both passwords match
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

# add feedback to course's feedback forum
class AddFeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackForum
        fields = ['feedback']


# STUDENT-SPECIFIC FORMS

# form to request an e-meet with teacher
class RequestMeetingForm(forms.ModelForm):
    # get only the teachers whose courses the student has enrolled in
    # to display in the dropdown selection
    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            self.fields['student'].initial = student
            self.fields['student'].disabled = True
        
        enrolled_courses = CourseEnrollments.objects.filter(student=student).values_list("course", flat=True)

        teachers = User.objects.filter(
            courses_taught__course_id__in=enrolled_courses
        ).distinct()

        self.fields['teacher'].queryset = teachers
        self.fields['teacher'].widget = forms.Select(
            choices=[(teacher.id, teacher.userinfo.display_name) for teacher in teachers]
        )

    class Meta:
        model = RequestMeeting
        fields = ["student", "teacher", "req_description"]

# filter form to filter through all courses
class FilterCourseForm(forms.Form):
    courseDescriptor = forms.CharField(max_length=150, required=False)
    instructor = forms.CharField(max_length=150, required=False)

# TEACHER-SPECIFIC FORMS

# filter form to filter through all users
class SearchPeopleForm(forms.Form):
    ROLE_CHOICES = [
        ('', 'All'),
        ('student', 'Student'),
        ('teacher', 'Teacher')
    ]
    
    name = forms.CharField(max_length=150, required=False)
    type = forms.ChoiceField(choices=ROLE_CHOICES, required=False)

# form to create new course
class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = CourseDetails
        fields = ['course_name', 'course_description', 'course_thumbnail_picture', 'course_header_picture']

# form to create new lesson
class CreateLessonForm(forms.ModelForm):
    class Meta:
        model = LessonDetails
        fields = ['lesson_title', 'lesson_description']

# form to add new material to existing lesson
class AddMaterialForm(forms.ModelForm):
    class Meta:
        model = MaterialUpload
        fields = ['name', 'description', 'lesson', 'upload_file']

    # display dropdown of all lessons in the course
    # to which a material is to be added
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        if course_id:
            self.fields['lesson'].queryset = LessonDetails.objects.filter(course_id=course_id)
        else:
            self.fields['lesson'].queryset = LessonDetails.objects.none()

# form to add new material to existing lesson
class AddAssignmentForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = AssignmentUpload
        fields = ['name', 'description', 'lesson', 'upload_file', 'deadline']

    # display dropdown of all lessons in the course
    # to which an assignment is to be added
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        if course_id:
            self.fields['lesson'].queryset = LessonDetails.objects.filter(course_id=course_id)
        else:
            self.fields['lesson'].queryset = LessonDetails.objects.none()

# form to delete a lesson
class DeleteLessonForm(forms.ModelForm):
    lesson_title = forms.ModelChoiceField(
        queryset=LessonDetails.objects.none(),
        empty_label="Select a Lesson",
        label="Lesson Title"
    )

    class Meta:
        model = LessonDetails
        fields = ['lesson_title']

    # display dropdown of all lessons in the course
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        if course_id:
            self.fields['lesson_title'].queryset = LessonDetails.objects.filter(course_id=course_id)

# form to delete a material from an existing lesson
class DeleteMaterialForm(forms.ModelForm):
    lesson = forms.ModelChoiceField(
        queryset=LessonDetails.objects.none(),
        empty_label="Select a Lesson",
        label="Lesson Title"
    )

    name = forms.ModelChoiceField(
        queryset=MaterialUpload.objects.none(),
        empty_label="Select a Material",
        label="Material Name"
    )

    class Meta:
        model = MaterialUpload
        fields = ['lesson', 'name']

    # display dropdown of all lessons and after which materials in the chosen lesson
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        if course_id:
            self.fields['lesson'].queryset = LessonDetails.objects.filter(course_id=course_id)
            
            if 'lesson' in kwargs.get('data', {}):
                lesson_id = kwargs['data'].get('lesson')
                if lesson_id:
                    self.fields['name'].queryset = MaterialUpload.objects.filter(lesson_id=lesson_id)
        else:
            self.fields['lesson'].queryset = LessonDetails.objects.none()
            self.fields['name'].queryset = MaterialUpload.objects.none()

# form to delete an assignment from an existing lesson
class DeleteAssignmentForm(forms.ModelForm):
    lesson = forms.ModelChoiceField(
        queryset=LessonDetails.objects.none(),
        empty_label="Select a Lesson",
        label="Lesson Title",
        widget=forms.Select(attrs={'id': 'id_lesson_assignment'})
    )

    name = forms.ModelChoiceField(
        queryset=AssignmentUpload.objects.none(),
        empty_label="Select an Assignment",
        label="Assignment Name",
        widget=forms.Select(attrs={'id': 'id_name_assignment'})
    )

    class Meta:
        model = AssignmentUpload
        fields = ['lesson', 'name']

     # display dropdown of all lessons and after which assignments in the chosen lesson
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        if course_id:
            self.fields['lesson'].queryset = LessonDetails.objects.filter(course_id=course_id)
            
            if 'lesson' in kwargs.get('data', {}):
                lesson_id = kwargs['data'].get('lesson')
                if lesson_id:
                    self.fields['name'].queryset = AssignmentUpload.objects.filter(lesson_id=lesson_id)
        else:
            self.fields['lesson'].queryset = LessonDetails.objects.none()
            self.fields['name'].queryset = AssignmentUpload.objects.none()

# form to accept e-meet request
class AcceptMeetingReq(forms.ModelForm):
    class Meta:
        model = MeetingDetails
        fields = ['start_datetime', 'duration_minutes']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # DateTime picker for start time
            'duration_minutes': forms.NumberInput(attrs={'min': '10', 'max': '60', 'step': '1', 'placeholder': 'Mins'}),  # number input for duration
        }

# form to decline e-meet request
class DeclineMeetingReq(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter decline message"}),
        label="Declining Reason",
        required=True
    )