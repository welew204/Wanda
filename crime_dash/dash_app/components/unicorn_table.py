from django_unicorn.components import UnicornView, QuerySetType
from dash_app.models import Crime, Evidence
from datetime import datetime
from pprint import pprint


class UnicornTableView(UnicornView):
    name: str = ''
    crimes: Crime.objects.none()
    evidence: Evidence.objects.none()

    def mount(self):
        """ On mount, populate the crimes property w/ a QuerySet of all crimes """
        print("mounting...")
        # print(self.crimes)
        self.crimes = Crime.objects.all()
        # self.evidence = ["A", "List", "Of", "Things"]
        self.evidence = Evidence.objects.all()
        # pprint(self.evidence) >> this breaks it?

    def add_evidence(self):
        """ Create the new evidence, get new list of all crimes, 
            and clear the 'name' property """
        print(self.name)
        self.evidence.create(e_description=self.name,
                             e_date=datetime.today(), e_lat=0.0, e_lon=0.0)
        self.name = ''
