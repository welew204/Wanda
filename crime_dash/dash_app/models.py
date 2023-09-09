from django.db import models

# Create your models here.


class Crime(models.Model):
    # add all the incoming columns here
    pass

    def __str__(self, raw=False):
        if raw == True:
            return  # the row, comma-delimited
        return  # a nice readable snippet
