from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(CourseDetails)
admin.site.register(CourseEnrollments)
admin.site.register(Notification)
admin.site.register(AssignmentUpload)
admin.site.register(AssignmentSubmission)
admin.site.register(FeedbackForum)
admin.site.register(MaterialUpload)
admin.site.register(LessonDetails)
admin.site.register(RequestMeeting)
admin.site.register(MeetingDetails)