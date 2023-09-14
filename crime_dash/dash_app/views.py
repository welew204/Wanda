from django.shortcuts import render, redirect
import django_tables2 as tables

from datetime import datetime
from pprint import pprint

from .models import Crime

# imported sodapy thru pipenv --> does this mean it's stored in a different area (NOT on PATH, so therefore warning here?)
from sodapy import Socrata


class CrimeTable(tables.Table):
    class Meta:
        #attrs = {"class": "table"}
        model = Crime
        sequence = ("c_date", "c_type", "c_description", "c_lat", "c_lon")
        exclude = ("id", "c_city", "c_state")


def home_page(request):
    print("lookin at DATA")
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
    for crime in results:
        try:
            c_type = crime['crimetype']
        except KeyError:
            # pprint(crime)
            missing_type += 1
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
                c_type = None

        Crime.objects.create(
            c_type=c_type,
            c_description=crime['description'],
            c_date=datetime.strptime(
                crime['datetime'], "%Y-%m-%dT%H:%M:%S.%f"),
            c_lat=crime['location_1']['coordinates'][0],
            c_lon=crime['location_1']['coordinates'][1],
            c_city=crime['city'],
            c_state=crime['state']
        )
    print(missing_type)
    # pass items if_valid() to Crime
    table = CrimeTable(Crime.objects.all().order_by('-c_date'))
    # share this is context
    context = {"table": table}
    # fake data:
    """ [{"date": "9-1-23", "type": "burglary", "location": "Redwoord Heights"},
    {"date": "9-1-23", "type": "assault", "location": "Laurel"}] """

    # pass context to a table
    return render(request, "crime_dash.html", context)


def make_pie():
    # make the pie graph, with options
    pass


def make_timeline():
    # make the timeline, with options
    pass


def make_map():
    # make heatmap depicting rows
    pass


def login_page(request):
    print("whaddup funker!")
    # user form

    # share this form in context
    context = {}

    # pass context to a table
    return render(request, "home_page.html", context)
