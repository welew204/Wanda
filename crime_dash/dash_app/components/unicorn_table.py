from django_unicorn.components import UnicornView, QuerySetType
from dash_app.models import Crime, Evidence
from datetime import datetime
from pprint import pprint


class UnicornTableView(UnicornView):

    # similar to React, setting default state is required
    lat_lon = '37.804363,-122.255'
    crimes: QuerySetType[Crime] = Crime.objects.none()
    evidence: QuerySetType[Evidence] = Evidence.objects.none()
    #
    # variable: Type[define_type] = value

    def update_center(self, new_coords):
        self.lat_lon = new_coords
        self.nearby_crimes()

    def nearby_crimes(self):
        map_center = self.lat_lon.split(",")
        map_center = (float(map_center[0]), float(map_center[1]))
        # print(lat_lon)
        #print(type(lat_lon), type(lat_lon[0]))

        epsilon = .002  # or about 220m radius around the point selected // @38deg North latitude: .01 long==101ft, .01==80ft
        nearby_crimes = Crime.objects.filter(
            c_lon__range=(map_center[1]-(epsilon*0.8), map_center[1]+(epsilon*0.8)), c_lat__range=(map_center[0]-epsilon, map_center[0]+epsilon)).order_by('-c_date')
        self.crimes = nearby_crimes

    def mount(self):
        """ On mount, populate the crimes property w/ a QuerySet of all crimes """
        print("mounting...")
        # print(self.crimes)

        # self.nearby_crimes()
        #self.crimes = Crime.objects.all()
        # self.evidence = ["A", "List", "Of", "Things"]
        #self.evidence = Evidence.objects.all()
        print(self.evidence)  # >> this breaks it?

    def make_evidence_connect(self, crime_pk):
        """ populate evidence form w/ correct crime id """
        print("WAHDDUP PUNK")
        print(crime_pk)

        # self.evidence.create(e_description=self.name,
        #                     e_date=datetime.today(), e_lat=0.0, e_lon=0.0)
