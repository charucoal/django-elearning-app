# This file contains the serializers for the API endpoints of the e-learning platform.
# Each serializer defines how the data from the models should be represented in JSON format 
# for the API requests and responses.
# The serializers are used to validate and transform data between the database and the client.

from rest_framework import serializers
from .models import *

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'

class CourseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetails
        fields = '__all__'
        
class LessonDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonDetails
        fields = '__all__'

class MaterialUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialUpload
        fields = '__all__'

class AssignmentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentUpload
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class FeedbackForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForum
        fields = '__all__'

class CourseEnrollmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollments
        fields = '__all__'

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'

class RequestMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMeeting
        fields = '__all__'

class MeetingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingDetails
        fields = '__all__'
