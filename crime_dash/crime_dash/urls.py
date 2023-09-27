"""
URL configuration for crime_dash project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from dash_app import views

urlpatterns = [
    path("", views.login_page),
    path("u_login/", views.u_login, name="u_login"),
    path("users/<username>/add-evidence/confirm-location/<lat_lon>",
         views.confirm_location),
    path("see_data/", views.home_page, name="see_data"),
    path("see_data/crimes.geojson", views.crimes_to_geoJSON),
    path("logout/", views.logout, name="logout"),
    path("users/<username>/add-evidence/",
         views.add_evidence, name="add-evidence"),

    path("unicorn/", include("django_unicorn.urls")),
    path("admin/", admin.site.urls),
]
