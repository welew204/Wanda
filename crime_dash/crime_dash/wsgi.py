"""
WSGI config for crime_dash project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "crime_dash.settings")
# trying to update the path to the crime_dash settings file...

application = get_wsgi_application()
