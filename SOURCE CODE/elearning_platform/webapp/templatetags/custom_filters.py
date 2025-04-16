from django import template
from django.utils import timezone

register = template.Library()

# get current date and time
@register.simple_tag
def current_time():
    current_time = timezone.now()
    formatted_time = current_time.strftime('%d-%m-%Y %H:%M')
    return formatted_time

# retrieve the file associated with a submission
@register.filter(name='submitted_file')
def submitted_file(submission):
    return submission.upload_file

# filter to calculate the progress of a course (rounded to nearest integer)
@register.filter(name='progress_val')
def progress_val(dictionary, key):
    if isinstance(dictionary, dict):
        course_data = dictionary.get(key)
        if course_data and isinstance(course_data, dict):
            progress = course_data.get('progress', 0)
            return round(progress)
    return 0

# filter to return the count of submitted assignments out of total submissions
@register.filter(name='submission_count')
def submission_count(submissions):
    submitted = 0
    total = len(submissions)
    for s in submissions:
        if s.submission_status == "submitted":
            submitted += 1

    return f"{submitted}/{total}"

# filter to retrieve a value from a dictionary using the given key
@register.filter(name='get_s')
def get_s(submissions, key):
    if isinstance(submissions, dict):
        return submissions.get(key, None)  # returns None if the key doesn't exist
    return None

# filter to check if a deadline is still in the future
@register.filter(name='get_time')
def get_time(deadline):
    if deadline > timezone.now():
        return True
    else:
        return False
