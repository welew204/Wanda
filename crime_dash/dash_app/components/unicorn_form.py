from django_unicorn.components import UnicornView, QuerySetType
from django import forms
from dash_app.models import Crime, Evidence
from django.contrib.auth.models import User
from datetime import datetime

# NOT USED/COULDN"T GET IT TO PLAY NICE


class UnicornFormView(UnicornView):
    crime = None # this is an empty QuerySet
    user = None # this is an empty QuerySet
    #evidence: QuerySetType[Evidence] = Evidence.objects.none()
    # form = AddEvidenceForm # couldn't get this to show AFTER I remounted component with fresh data
    description = ''
    lat_lon = ''

            

    def populate_crime_info(self, c_id):
        print(c_id)
        user = self.request.user
        self.crime = Crime.objects.get(pk=c_id)
        evidence = Evidence.objects.filter(author=user.id, c_correlated=c_id).first()
        if evidence:
            self.user = user
            print(f"user associated w/ this evidence: {self.user}")
        else:
            self.user=None
            print("no user associated with this crime")


    def clear_crime(self):
        self.crime = None
        self.user = None

    def set_lat_lon(self, lat_lon):
        
        self.lat_lon = lat_lon
        #print("set it!", lat_lon)

    def add_evidence(self):

        lat_lon = self.lat_lon.split(',')
        lat = float(lat_lon[0])
        lon = float(lat_lon[1])
        #print(lat, lon)
        user = User.objects.get(id=self.request.user.id)
        print(self.crime)
        print(type(self.crime))
        print("Signing this evidence by user_id: ", self.request.user)
        evidence = Evidence(e_description=self.description, c_correlated=self.crime,
                            e_date=datetime.today(), e_lat=lat, e_lon=lon, author=user)
        evidence.save()
        self.user=user
        self.description = ''
        self.populate_crime_info(self.crime.id)
        print("finished WRITING evidence row")
