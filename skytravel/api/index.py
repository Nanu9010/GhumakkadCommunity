import os
import sys

# __file__ = skytravel/api/index.py
# Going up 2 dirs = skytravel/ (Django project root)
# We need parent of skytravel/ on sys.path for `import skytravel.settings`
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skytravel.settings')
os.environ.setdefault('VERCEL', '1')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
