from django.utils import timezone
from webapp.models import AssignmentSubmission, MeetingDetails
from datetime import timedelta

# Middleware class to check deadlines and meeting status on each request
class DeadlineCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # call deadline and meeting status check on every request
        self.check_deadlines() # check and update assignment submission statuses
        self.check_meetings() # check and update meeting statuses
        response = self.get_response(request)  # get the response after processing the request
        return response

    # check and update the status of assignment submissions based on their deadlines
    def check_deadlines(self):
        # get all assignment submissions
        deadlines = AssignmentSubmission.objects.filter()
        
        # loop through each submission and check if it is overdue
        for d in deadlines:

            # if the deadline has passed
            if d.assignment.deadline < timezone.now():
                d.submission_status = "overdue"
                d.assignment.assignment_status = False
                d.assignment.save()
    
    # check and update the status of meetings based on their timing
    def check_meetings(self):
        # get all meetings with the status 'closed' and check if they are now in progress
        meetings_closed = MeetingDetails.objects.filter(meeting_status='closed')

        # loop through each meeting that was closed and check if it's within the meeting duration
        for m in meetings_closed:
            if m.start_datetime <= timezone.now() <= m.start_datetime + timedelta(minutes=m.duration_minutes):
                m.meeting_status = 'open'
                m.save()

        # get all meetings with the status 'open' and check if they have expired
        meetings_opened = MeetingDetails.objects.filter(meeting_status='open')

        # loop through each open meeting and check if it has passed the duration
        for m in meetings_opened:
            if m.start_datetime + timedelta(minutes=m.duration_minutes) < timezone.now():
                m.meeting_status = 'expired'
                m.save()
