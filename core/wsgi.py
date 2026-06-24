from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
application = WhiteNoise(application)
app = application