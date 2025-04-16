from celery import Celery, shared_task
from celery.utils.log import get_task_logger
import os, django
import sendgrid
from sendgrid.helpers.mail import Mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elearning_platform.settings")
django.setup()

# initialize celery
celery_app = Celery("webapp")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

logger = get_task_logger(__name__)
logger.info("This is a Celery task log")

# asynchronous task to send an email
@shared_task(max_retries=0)
def async_send_email(customer_email, email_subject, statement):
    
    # create the email message using SendGrid's Mail object
    message = Mail(from_email='charu.sgp@gmail.com',
                   to_emails='charu.sgp@gmail.com', # customer_email not used due to Sendgrid's rules
                   subject=email_subject,
                   html_content=statement)
    
    try:
        # initialise the SendGrid client with the API key
        sg = sendgrid.SendGridAPIClient(api_key='SENDGRID_API_KEY_HERE')
        
        # send the email message using SendGrid's send method
        response = sg.send(message)

        print(response.status_code, response.body, response.headers)
    
    # catch any exceptions and print the error message
    except Exception as e:
        print(str(e))
        