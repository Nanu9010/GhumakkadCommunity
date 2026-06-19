import os
import sys
import shutil

# Ensure we're in the right directory and can import Django
HERE = os.path.dirname(os.path.abspath(__file__))
DJANGO_ROOT = os.path.join(HERE, 'skytravel')

sys.path.insert(0, DJANGO_ROOT)
os.chdir(DJANGO_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skytravel.settings')
os.environ.setdefault('VERCEL', '1')

# Copy DB to /tmp on cold start
if os.environ.get('VERCEL') == '1':
    src_db = os.path.join(DJANGO_ROOT, 'db.sqlite3')
    dst_db = '/tmp/db.sqlite3'
    if os.path.exists(src_db) and not os.path.exists(dst_db):
        shutil.copy2(src_db, dst_db)

from django.core.wsgi import get_wsgi_application
from serverless_wsgi import handle_request

django_app = get_wsgi_application()


def handler(request, response):
    return handle_request(django_app, request, response)
