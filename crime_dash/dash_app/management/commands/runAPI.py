from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from sodapy import Socrata

from ...models import Crime


class Command(BaseCommand):
    help = "Runs the SODA call to grab data from Oakland Gov"

    def handle(self, *args, **options):
        # make request w/ requests library
        # SODA call
        client = Socrata("data.oaklandca.gov", None)
        # OaklandDataSet ID: ym6k-rx7a
        # App token: qYX2jLFsWcJBkQkrRaEeiGBRa
        # ---> not sure about how to use this token as a kwarg in my .get call...
        # https://dev.socrata.com/docs/app-tokens.html
        results = client.get("ym6k-rx7a", limit=2000)
        if results:
            Crime.objects.all().delete()
        # print(results[0])
        missing_type = 0
        corrected = 0
        for crime in results:
            try:
                c_type = crime['crimetype']
            except KeyError:
                # pprint(crime)
                missing_type += 1
                corrected += 1
                if "VEHICLE" in crime['description'] and "THEFT" in crime['description']:
                    c_type = "STOLEN VEHICLE"
                elif "BURGLARY" in crime['description']:
                    c_type = "BURGLARY"
                elif "BATTERY" in crime['description']:
                    c_type = "BATTERY"
                elif "ASSAULT" in crime['description']:
                    c_type = "ASSAULT"
                elif "ROBBERY" in crime['description']:
                    c_type = "ROBBERY"
                elif "VANDALISM" in crime['description']:
                    c_type = "VANDALISM"
                elif "THEFT" in crime['description']:
                    c_type = "THEFT"
                elif "DUI" in crime['description']:
                    c_type = "DUI"
                else:
                    corrected -= 1
                    c_type = None

            Crime.objects.create(
                c_type=c_type,
                c_description=crime['description'],
                c_date=datetime.strptime(
                    crime['datetime'], "%Y-%m-%dT%H:%M:%S.%f"),
                c_lon=crime['location_1']['coordinates'][0],
                c_lat=crime['location_1']['coordinates'][1],
                c_city=crime['city'],
                c_state=crime['state']
            )
        self.stdout.write(
            f"{missing_type} rows w/ missing 'type'// \n-->{corrected} corrected")
        self.stdout.write("DB updated w/ fresh data!")
