from django.db import models
# tried importing PointField but this demands a ton of GIS libraries to be installed and work (had trouble w/ GEOS lib)
#from django.contrib.gis.db.models import PointField

# Create your models here.


class Crime(models.Model):
    # add all the incoming columns here
    c_type = models.CharField(
        "Crime Type", max_length=50, blank=True, null=True)
    c_description = models.CharField("Crime Description", max_length=50)
    c_date = models.DateField("Date")
    c_lat = models.DecimalField("Latitude", max_digits=15, decimal_places=9)
    c_lon = models.DecimalField("Longitude", max_digits=15, decimal_places=9)
    c_city = models.CharField(max_length=30)
    c_state = models.CharField(max_length=3)


class Evidence(models.Model):
    # add all the incoming columns here
    c_correlated = models.ForeignKey(
        Crime, blank=True, null=True, on_delete=models.SET_NULL)
    e_description = models.CharField(
        "Scene/Evidence Description", max_length=200)
    e_date = models.DateField("Date")
    e_lat = models.DecimalField("Latitude", max_digits=15, decimal_places=9)
    e_lon = models.DecimalField("Longitude", max_digits=15, decimal_places=9)
