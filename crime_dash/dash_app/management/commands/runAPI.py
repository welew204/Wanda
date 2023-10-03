from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from sodapy import Socrata

from ...models import Crime


class Command(BaseCommand):
    help = "Runs the SODA call to grab data from Oakland Gov"

    def handle(self, *args, **options):
        # make request w/ requests library
        # >> heroku scheduler recommends a 'return' at the end of every logical conclusion to make sure the dyno knows to end!
        try:
            client = Socrata("data.oaklandca.gov", None)
        except:
            self.stdout.write("could not connect with 'data.oaklandca.gov'")
            # if the connection fails, should stop the job
            return

        results = client.get("ym6k-rx7a", limit=2000)
        # "ym6k-rx7a" is the 'dataset identifier
        if results:
            Crime.objects.all().delete()
            self.stdout.write(
                f"Deleted previous crimes, current model count: (this num should be 0) {Crime.objects.all().count()}")
        # print(results[0])
        missing_type = 0
        corrected = 0
        for crime in results:
            if len(crime["description"]) >= 100:
                c_desc = crime["description"][:100]
                self.stdout.write(f"Truncating crime {crime['casenumber']}")
            else:
                c_desc = crime["description"]
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
                c_description=c_desc,
                c_date=datetime.strptime(
                    crime['datetime'], "%Y-%m-%dT%H:%M:%S.%f"),
                c_lon=crime['location_1']['coordinates'][0],
                c_lat=crime['location_1']['coordinates'][1],
                c_city=crime['city'],
                c_state=crime['state']
            )
        self.stdout.write(
            f"Model now includes {Crime.objects.all().count()} crimes")
        self.stdout.write(
            f" --> Most recent date = {Crime.objects.all().order_by('-c_date').first().c_date}")
        self.stdout.write(
            f"{missing_type} rows w/ missing 'type'// \n--> corrected {corrected} / {missing_type}")
        self.stdout.write("DB updated w/ fresh data!")
        return
