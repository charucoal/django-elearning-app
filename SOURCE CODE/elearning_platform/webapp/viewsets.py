# This file contains the viewsets for the API endpoints of the e-learning platform.
# Each viewset handles CRUD operations for models.
# These viewsets are registered with the router to provide the necessary REST API functionality.

from rest_framework import viewsets
from .models import *
from .serializers import *

class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

class CourseDetailsViewSet(viewsets.ModelViewSet):
    queryset = CourseDetails.objects.all()
    serializer_class = CourseDetailsSerializer

class LessonDetailsViewSet(viewsets.ModelViewSet):
    queryset = LessonDetails.objects.all()
    serializer_class = LessonDetailsSerializer

class MaterialUploadViewSet(viewsets.ModelViewSet):
    queryset = MaterialUpload.objects.all()
    serializer_class = MaterialUploadSerializer

class AssignmentUploadViewSet(viewsets.ModelViewSet):
    queryset = AssignmentUpload.objects.all()
    serializer_class = AssignmentUploadSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class FeedbackForumViewSet(viewsets.ModelViewSet):
    queryset = FeedbackForum.objects.all()
    serializer_class = FeedbackForumSerializer

class CourseEnrollmentsViewSet(viewsets.ModelViewSet):
    queryset = CourseEnrollments.objects.all()
    serializer_class = CourseEnrollmentsSerializer

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer

class RequestMeetingViewSet(viewsets.ModelViewSet):
    queryset = RequestMeeting.objects.all()
    serializer_class = RequestMeetingSerializer

class MeetingDetailsViewSet(viewsets.ModelViewSet):
    queryset = MeetingDetails.objects.all()
    serializer_class = MeetingDetailsSerializer