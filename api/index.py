import os
import sys

# __file__ = Travel Community/api/index.py
# Django project root = Travel Community/skytravel/ (has manage.py)
# Django Python package = Travel Community/skytravel/skytravel/ (has settings.py)
# We need Travel Community/skytravel/ on sys.path so `import skytravel.settings` works

HERE = os.path.dirname(os.path.abspath(__file__))
DJANGO_ROOT = os.path.join(HERE, 'skytravel')

sys.path.insert(0, DJANGO_ROOT)
os.chdir(DJANGO_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skytravel.settings')
os.environ.setdefault('VERCEL', '1')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
