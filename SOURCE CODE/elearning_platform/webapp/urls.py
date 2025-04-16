from drf_yasg import openapi
from django.urls import include, path, re_path
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from .views import *
from .viewsets import *

# API Schema View (Swagger/Redoc Docs)
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="API documentation for the e-learning platform, Voyage.",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

# DefaultRouter to automatically register viewsets
router = DefaultRouter()
router.register(r'users', UserInfoViewSet)
router.register(r'courses', CourseDetailsViewSet)
router.register(r'lessons', LessonDetailsViewSet)
router.register(r'materials', MaterialUploadViewSet)
router.register(r'assignments', AssignmentUploadViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'feedbacks', FeedbackForumViewSet)
router.register(r'enrollments', CourseEnrollmentsViewSet)
router.register(r'submissions', AssignmentSubmissionViewSet)
router.register(r'meeting_requests', RequestMeetingViewSet)
router.register(r'meetings', MeetingDetailsViewSet)

# URL patterns for API and views
urlpatterns = [
    # API endpoints and documentation URLs
    path('api/', include(router.urls)),
    re_path(r'^api/schema/$', schema_view.without_ui(cache_timeout=0), name='api_schema'),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # Logged out views
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('signup/', user_signup, name='signup'),

    # Student views
    path('student/home/', student_homepage, name='student-home'),
    path('student/courses/all/', student_view_courses, name='student-courses-view'),
    path('student/courses/', view_course_detail, name='student-course-view'),
    path('student/notifications/', student_notifications, name='student-notifications'),
    path('student/profile/settings', student_profile, name='student-profile-settings'),
    path('student/profile/password', student_profile_password, name='student-profile-password'),
    path('student/profile/courses', student_view_my_courses, name='student-profile-courses'),
    path('student/meeting/request', student_request_meeting, name='student-request-meeting'),

    # Teacher views
    path('teacher/home/', teacher_homepage, name='teacher-home'),
    path('teacher/courses/create', teacher_create_course, name='teacher-create-course'),
    path('teacher/courses/', teacher_course_setting, name='teacher-course-setting'),
    path('teacher/courses/view', teacher_view_course, name='teacher-view-course'),
    path('teacher/courses/add-items', teacher_add_course_items, name='teacher-add-items'),
    path('get-materials/<int:lesson_id>/', get_materials, name='get-materials'),
    path('get-assignments/<int:lesson_id>/', get_assignments, name='get_assignments'),
    path('teacher/courses/delete-items', teacher_delete_course_items, name='teacher-delete-items'),
    path('teacher/courses/submissions', teacher_view_submissions, name='teacher-view-submissions'),
    path('teacher/courses/enrolments', teacher_view_enrolments, name='teacher-view-enrolments'),
    path('teacher/meeting/manage', teacher_manage_meetings, name='teacher-manage-meetings'),
    path('teacher/search/', teacher_search_person, name='teacher-search-person'),
    path('teacher/notifications/', teacher_notifications, name='teacher-notifications'),
    path('teacher/profile/settings', teacher_profile, name='teacher-profile-settings'),
    path('teacher/profile/password', teacher_profile_password, name='teacher-profile-password'),

    # E-meeting view
    path('join/meeting/', chat_meeting, name='join-meeting'),
]
