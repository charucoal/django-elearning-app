PROJECT TITLE: Django-based E-Learning Platform (Voyage)

PROJECT DESCRIPTION: Voyage, is a comprehensive, real-time educational hub that supports students and teachers with interactive course management, feedback systems, secure user authentication, and dynamic real-time communication for a seamless learning experience.

INSTALLATION INSTRUCTIONS
1. Navigate to the root directory of the application
2. Install required modules: pip install -r requirements.txt

ENVIRONMENT SETUP
- Operating System: macOS
- Python Version: 3.9.6

ENSURE MIGRATIONS ARE DONE
- python manage.py makemigrations
- python manage.py showmigrations (to view migrations)
- python manage.py migrate (for future migrations)

TO VIEW DATABASE (ensure directory is set to 'AWD Finals/SOURCE CODE/elearning_platform')
- sqlite3 db.sqlite3
- .tables (to view tables present in database)

SETTING UP THE APPLICATION (ensure directory is set to 'AWD Finals/SOURCE CODE/elearning_platform')
- Run '/usr/local/bin/redis-server' in a new terminal (sets up Redis server)
- Run 'celery -A elearning_platform.celery:app worker --loglevel=info' in another new terminal (sets up Celery)

RUNNING THE APPLICATION (ensure directory is set to 'AWD Finals/SOURCE CODE/elearning_platform')
- Run 'daphne -b 127.0.0.1 -p 8080 elearning_platform.asgi:application' in another new terminal
- Access web application via http://127.0.0.1:8080

ACCESSING API DOCUMENTATION
- Access via http://127.0.0.1:8080/redoc

LOGIN CREDENTIALS FOR DJANGO ADMIN SITE (access via http://127.0.0.1:8080/admin/)
Username: admin
Password: admin123

ACCESS API Endpoints (need to first login as admin via Django-admin site)
After logging in as admin:
- http://127.0.0.1:8080/api (view all APIs)
- http://127.0.0.1:8080/docs (API endpoints via Swagger)

RUNNING UNIT TESTS (ensure directory is set to 'AWD Finals/SOURCE CODE/elearning_platform')
- Run 'python manage.py test' in the terminal

DEPENDENCIES - Can be viewed in the requirements.txt file

DEMO VIDEO: https://youtu.be/bEoAZCO4hKo