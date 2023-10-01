from django.shortcuts import render, redirect
#from django.core.serializers import serialize
from django.db import models
from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse

import django_tables2 as tables
import pygal

import os
import datetime
import json
from pprint import pprint

from .models import Crime
from .models import Evidence

# TODO change access method to .env variable!

mapbox_access_token = os.environ.get('MAP_KEY')


class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email']


class LoginUserForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput()) # this also works

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class CrimeTable(tables.Table):
    class Meta:
        #attrs = {"class": "table"}
        model = Crime
        sequence = ("c_date", "c_type", "c_description", "c_lat", "c_lon")
        exclude = ("id", "c_city", "c_state")


class AddEvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['e_description']


class CrimeEvidenceTable(tables.Table):
    class Meta:
        #attrs = {"class": "table"}
        model = Crime
        sequence = ("c_date", "c_type", "c_description",)
        exclude = ("id",  "c_lat", "c_lon", "c_city", "c_state")


'''    {
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [125.6, 10.1]
  },
  "properties": {
    "name": "Dinagat Islands"
  }
}'''


def crimes_to_geoJSON(request):
    crimes = Crime.objects.all()
    # iterate thru qs to make a FeatureCollection
    fc = {"type": "FeatureCollection", "features": []}
    for c in crimes:

        formatted_feature = {"type": "Feature", "properties": {"c_type": c.c_type, "c_date": c.c_date.strftime("%m/%d/%Y")}, "geometry": {
            "type": "Point", "coordinates": [float(c.c_lon), float(c.c_lat)]}}
        fc["features"].append(formatted_feature)
    # pprint(fc)
    # JsonResponse does the serializing into Json for me :)
    return JsonResponse(fc)


def home_page(request):
    print("lookin at DATA")

    # pass items if_valid() to Crime
    crimes = Crime.objects.all().order_by('-c_date')

    pie = make_pie(crimes=crimes)
    timeline = make_timeline(crimes=crimes)

    table = CrimeTable(crimes)

    # share this is context
    context = {"most_recent": crimes[0].c_date,
               "table": table,
               "pie": pie,
               "timeline": timeline,
               "mapbox_access_token": mapbox_access_token}

    # pass context to a table
    return render(request, "crime_dash.html", context)


def logout(request):
    auth.logout(request)
    return redirect('/')


def u_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        print("Success!")
        auth.login(request, user)
    else:
        print("Incorrect username or password")

    return redirect('/')


def login_page(request):

    if request.method == 'POST':

        # Create a form instance and populate it with data from the request
        form = NewUserForm(request.POST)
        print(form.data)

        if form.is_valid():
            # Create a new user object populated with the data we are
            # giving it from the cleaned_data form
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])

            user = form.save()

            # As soon as our new user is created, we make this user be
            # instantly "logged in"
            auth.login(request, user)
            return redirect('/')

    else:
        # if a GET we'll create a blank form
        form = NewUserForm(auto_id="register_%s")
        login_form = LoginUserForm()
    context = {
        'form': form,
        'login_form': login_form
    }
    return render(request, "home_page.html", context)


def add_evidence(request, username):
    user = User.objects.get(username=username)
    # map_center = lat_lon

    #table = CrimeEvidenceTable(nearby_crimes.order_by('-c_date'))
    form = AddEvidenceForm()
    evidence = Evidence.objects.all()
    # map centered on: (37.804363, -122.255)
    context = {"mapbox_access_token": mapbox_access_token,
               # "table": table,
               "form": form,
               }
    return render(request, "add_evidence.html", context)


def make_pie(crimes):
    # make the pie graph, with options

    crime_types = Crime.objects.values('c_type').distinct()
    # pprint(crime_types)
    crimes_breakdown = {}
    total_crimes = len(crimes)
    for result in crime_types:
        t = result['c_type']
        num = Crime.objects.filter(c_type=t).count()
        crimes_breakdown[t] = round(num / total_crimes, 2)*100

    # this is redundant w/ 'None'
    #crimes_breakdown["No type"] = round(null_rows / total_crimes, 2)*100
    auto_totals = 0.0
    burg_totals = 0.0
    theft_totals = 0.0
    sex_crimes_totals = 0.0
    violence_totals = 0.0
    keys_to_collape = []
    none_crime_types_to_add = crimes_breakdown.pop(None)
    for c_type, val in crimes_breakdown.items():
        if any(crime_opt in c_type for crime_opt in ['AUTO', 'VEHICLE']):
            keys_to_collape.append(c_type)
            auto_totals += val
        elif any(crime_opt in c_type for crime_opt in ['PROSTITUTION', 'SEX']):
            keys_to_collape.append(c_type)
            sex_crimes_totals += val
        elif any(crime_opt in c_type for crime_opt in ['BURG -', 'BURGLARY']):
            keys_to_collape.append(c_type)
            burg_totals += val
        elif any(crime_opt in c_type for crime_opt in ['THEFT', 'O/S']):
            keys_to_collape.append(c_type)
            theft_totals += val
        elif any(crime_opt in c_type for crime_opt in ['ASSAULT', 'RAPE', 'BATTERY', 'VIOLENCE']):
            keys_to_collape.append(c_type)
            violence_totals += val
        elif val == 0.0:
            keys_to_collape.append(c_type)
    for ky in keys_to_collape:
        crimes_breakdown.pop(ky)
    crimes_breakdown["OTHER"] += none_crime_types_to_add
    crimes_breakdown["AUTO"] = auto_totals
    crimes_breakdown["BURGLARY"] = burg_totals
    crimes_breakdown["THEFT"] = theft_totals
    if sex_crimes_totals > 0:
        crimes_breakdown["SEX CRIMES"] = sex_crimes_totals
    # delete the key:vals from keys_to_collapse
    # pprint(crimes_breakdown)

    pie_chart = pygal.Pie(legend_at_bottom=True,
                          height=900, style=pygal.style.Style(legend_font_size=25))
    # this isn't exact height of result, but gives me a nice proportion
    #pie_chart.title = "Breakdown of Crime Types (in %)"
    for type, val in crimes_breakdown.items():
        pie_chart.add(type, val)
    # for testing only:
    # pie_chart.render_to_file('pie_chart.svg')

    return pie_chart.render_data_uri()


def make_timeline(crimes):
    # make the timeline, with options
    # using simple Dot chart style
    crimes_list = [[c.c_type, c.c_date] for c in crimes]
    # pprint(crimes_list)
    for c in crimes_list:
        if c[0] == None:
            # print(c)
            c[0] = 'OTHER'
            continue
        if any(crime_opt in c[0] for crime_opt in ['AUTO', 'VEHICLE']):
            c[0] = 'AUTO'
        elif any(crime_opt in c[0] for crime_opt in ['BURGLARY', 'ROBBERY', 'THEFT']):
            c[0] = 'THEFT'
        elif any(crime_opt in c[0] for crime_opt in ['RAPE', 'DOMESTIC', 'ASSAULT']):
            c[0] = 'VIOLENCE'
        else:
            c[0] = 'OTHER'

    # pprint(crimes_list)
    dot_chart = pygal.Dot(
        show_legend=False, style=pygal.style.Style(
            label_font_size=10,
            major_label_font_size=15
        ), x_label_rotation=30)
    # NONE OF THESE ^^ values seem to be working...how to formate pygal??
    #dot_chart.title = 'Timeline of Crimes'
    min_date = crimes.aggregate(min_value=models.Min('c_date'))['min_value']
    max_date = crimes.aggregate(max_value=models.Max('c_date'))['max_value']
    # print(type(min_date))
    timeline_x = []
    major_timeline_x = []
    crimes_for_this_dot = []
    all_crimes_timelines = []
    for delta in range((max_date - min_date).days):
        date = min_date + datetime.timedelta(days=delta)
        crimes_for_this_dot.extend([c for c in crimes_list if date == c[1]])
        if delta != 0 and delta % 7 == 0:
            timeline_x.append(date.strftime("%m/%d/%Y"))
            all_crimes_timelines.append(crimes_for_this_dot)
            crimes_for_this_dot = []
        if delta != 0 and delta % 28 == 0:
            major_timeline_x.append(date.strftime("%m/%d/%Y"))

    dot_chart.x_labels = timeline_x
    dot_chart.x_labels_major = major_timeline_x
    # this is good ^^ and gives me datetime.date objects

    for i, dt in enumerate(all_crimes_timelines):
        theft_cs = [c for c in dt if c[0] == 'THEFT']
        auto_cs = [c for c in dt if c[0] == 'AUTO']
        violence_cs = [c for c in dt if c[0] == 'VIOLENCE']
        other_cs = [c for c in dt if c[0] == 'OTHER']
        all_crimes_timelines[i] = {
            'THEFT': len(theft_cs),
            'AUTO': len(auto_cs),
            'VIOLENCE': len(violence_cs),
            'OTHER': len(other_cs)
        }
    thefts = [ctl['THEFT'] for ctl in all_crimes_timelines]
    autocs = [ctl['AUTO'] for ctl in all_crimes_timelines]
    violencecs = [ctl['VIOLENCE'] for ctl in all_crimes_timelines]
    othercs = [ctl['OTHER'] for ctl in all_crimes_timelines]

    dot_chart.add('Thefts/Burlgary', thefts)
    dot_chart.add('Auto', autocs)
    dot_chart.add('Violence', violencecs)
    dot_chart.add('Other', othercs)
    # pprint(dot_chart.x_labels)

    return dot_chart.render_data_uri()


def make_map():
    # make heatmap depicting rows

    # TODO: move this token to Django settings from an environment variable
    # found in the Mapbox account settings and getting started instructions
    # see https://www.mapbox.com/account/ under the "Access tokens" section
    mapbox_access_token = 'pk.my_mapbox_access_token'
    pass
