from django_unicorn.components import UnicornView, QuerySetType
from django import forms
from dash_app.models import Crime, Evidence
from datetime import datetime

# NOT USED/COULDN"T GET IT TO PLAY NICE


class AddEvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['e_description']


class UnicornFormView(UnicornView):
    crime: QuerySetType[Crime] = Crime.objects.none()
    #evidence: QuerySetType[Evidence] = Evidence.objects.none()
    # form = AddEvidenceForm # couldn't get this to show AFTER I remounted component with fresh data
    description = ''
    lat_lon = ''

    def populate_crime_info(self, c_id):

        print(c_id)
        self.crime = Crime.objects.get(pk=c_id)

    def clear_crime(self):
        self.crime = Crime.objects.none()

    def set_lat_lon(self, lat_lon):
        self.lat_lon = lat_lon
        #print("set it!", lat_lon)

    def add_evidence(self):

        lat_lon = self.lat_lon.split(',')
        lat = float(lat_lon[0])
        lon = float(lat_lon[1])
        #print(lat, lon)
        evidence = Evidence(e_description=self.description, c_correlated=self.crime,
                            e_date=datetime.today(), e_lat=lat, e_lon=lon)
        evidence.save()
        self.description = ''
