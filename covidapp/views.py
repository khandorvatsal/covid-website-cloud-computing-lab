from django.shortcuts import render,redirect,reverse,HttpResponse
from .models import Suggestion
from .forms import SuggestionForm
from django.contrib import messages
import geoip2.database

import datetime
from datetime import date
import calendar
import pytz
import requests
from operator import itemgetter
import json
from .models import Suggestion
import copy
from babel.numbers import format_currency

def globalview(request):
    d=datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    global_stats = requests.get('http://api.coronatracker.com/v3/stats/worldometer/global')
    global_timeline = requests.get('https://corona-api.com/timeline')
    global_timeline1 = global_timeline.json()
    global_timeline1 = global_timeline1['data']
    l= len(global_timeline1)
    l=l-1 
    global_timeline1 = global_timeline1[0:l:10]
    global_timeline1 = global_timeline1[::-1]

    global_stats = global_stats.json()
    last_updated = global_stats['created']
    del global_stats['totalCasesPerMillionPop']
    del global_stats['created']
    for x in global_stats:
        a = global_stats[x]
        b = format_currency(a, 'INR', locale='en_IN')
        c = b[1:len(b)-3]
        global_stats[x] = c
    all_country = requests.get('https://corona-api.com/countries')
    all_country = all_country.json()
    country_data = all_country['data']
    for x in country_data:
        x['total_confirmed'] = (x['latest_data']['confirmed'])    
    country_data = sorted(country_data, key=itemgetter('total_confirmed'),reverse=True)
    for x in country_data:
        total = x['latest_data']['confirmed']
        total = format_currency(total, 'INR', locale='en_IN')
        total = total[1:len(total)-3]
        x['latest_data']['confirmed'] = total
    data={
        'all_country':country_data ,
        '1':country_data[0],
        '2':country_data[1],
        '3':country_data[2],
        'global': global_stats,
        
        'globaltimeline': global_timeline1,
        'd':d,
        'last_updated':last_updated
       
        
    }
    return render(request,'covidapp/globalview.html',data)

def api(request):
    global_stats = requests.get('http://api.coronatracker.com/v3/stats/worldometer/global')
    global_stats = global_stats.json()
    
    del global_stats['totalCasesPerMillionPop']
    del global_stats['created']
    for x in global_stats:
        a = global_stats[x]
        b = format_currency(a, 'INR', locale='en_IN')
        c = b[1:len(b)-3]
        global_stats[x] = c
    all_country = requests.get('https://corona-api.com/countries')
    all_country = all_country.json()
    country_data = all_country['data']
    for x in country_data:
        x['total_confirmed'] = (x['latest_data']['confirmed'])    
    country_data = sorted(country_data, key=itemgetter('total_confirmed'),reverse=True)
    ranknumber = 1
    for x in country_data:
        x['rank'] = ranknumber
        ranknumber = ranknumber + 1
    country_total_data_commas = ['confirmed', 'deaths', 'recovered']
    country_daily_data_commas = ['confirmed', 'deaths']
    for x in country_data:
        for l in country_total_data_commas:
            total = x['latest_data'][l]
            total = format_currency(total, 'INR', locale='en_IN')
            total = total[1:len(total)-3]
            x['latest_data'][l] = total

    for x in country_data:
        for l in country_daily_data_commas:
            total = x['today'][l]
            total = format_currency(total, 'INR', locale='en_IN')
            total = total[1:len(total)-3]
            x['today'][l] = total

    response_india = requests.get('https://api.covid19india.org/data.json')
    india = response_india.json()
    
    
    state=india['statewise']
    india1_comma = ['active', 'confirmed', 'deaths','recovered' ,'deltaconfirmed', 'deltadeaths', 'deltarecovered', ]
    for x in state:
            for l in india1_comma:
                total = x[l]
                total = format_currency(total, 'INR', locale='en_IN')
                total = total[1:len(total)-3]
                x[l] = total
    state=list(state)
    newstate={}
    for entry in state:
        name = entry.pop('state')
        newstate[name] = entry
    # statelist=list(newstate)
    del newstate['Total']
    data={
        'all_country':country_data ,
        '1':country_data[0],
        '2':country_data[1],
        '3':country_data[2],
        'global': global_stats,
        'india_total':india['statewise'][0],
        'statelist':newstate,
        'india':india,
        
        
    }
    
    
    return render(request, 'covidapp/api.html',data)


def statewise(request):
    d=datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    url = 'http://corona-api.com/countries/{}'
        
    info = requests.get(url.format('IN')).json()
        
        
        
    country=info['data']
    response_india = requests.get('https://api.covid19india.org/data.json')
    
    india = response_india.json()    
    india1=india['statewise']
    india1_comma = ['active', 'confirmed', 'deaths','recovered' ,'deltaconfirmed', 'deltadeaths', 'deltarecovered', ]
    for x in india1:
        for l in india1_comma:
            total = x[l]
            total = format_currency(total, 'INR', locale='en_IN')
            total = total[1:len(total)-3]
            x[l] = total
    graph=india['cases_time_series']
    daywise={}
    for entry in graph:
        day = entry.pop('date')
        daywise[day] = entry
    l=len(daywise)
    l=l-1
    daywise = dict(list(daywise.items())[l:0: -10])


    daywise2 = dict(list(daywise.items())[::-1 ])
    
    
    


    data={
        'india':india1,
        'india_total':india['statewise'][0],
        'd':d,
        'daywise':daywise2,
        'info':country,
        
      
    }

    return render(request, 'covidapp/india.html',data)

def stateview(request,sname, scode):
    scode = scode.lower()
    if sname == 'Total':
        return redirect('statewise')
    else:    
        d=datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        state_timeline = requests.get('https://api.covid19india.org/states_daily.json').json()
        state_timeline = state_timeline['states_daily']
        zones = requests.get('https://api.covid19india.org/zones.json')
        zones = zones.json()
        zones = zones['zones']
        zone_name = {}
        for entry in zones:
            district_name = entry.pop('district')
            zone_name[district_name] = entry


        response_india = requests.get('https://api.covid19india.org/data.json')
        india = response_india.json()

        response_state=requests.get('https://api.covid19india.org/state_district_wise.json')
        districts= response_state.json()
        state=india['statewise']
        india1_comma = ['active', 'confirmed', 'deaths','recovered' ,'deltaconfirmed', 'deltadeaths', 'deltarecovered', ]
        for x in state:
            for l in india1_comma:
                total = x[l]
                total = format_currency(total, 'INR', locale='en_IN')
                total = total[1:len(total)-3]
                x[l] = total
        state=list(state)
        newstate={}
        for entry in state:
            name = entry.pop('state')
            newstate[name] = entry
        s=newstate[sname]
        dis=districts[sname]['districtData']

        for key,value in dis.items():
            for x in zone_name:
                if x == key:
                    dis[key]['zone'] = zone_name[x]['zone']
        deceased = []
        confirmed = []
        recovered = []
        for x in state_timeline:
            if x['status'] == 'Deceased':
                deceased.append(x[scode])  
            if x['status'] == 'Confirmed':
                confirmed.append(x[scode]) 
            if x['status'] == 'Recovered':
                recovered.append(x[scode])               

        data={
            's':s,
            'sname':sname,
            'scode':scode,
            'd':d,
            'dis':dis,
            'zone_name':zone_name,
            'state_timeline':state_timeline,
            'deceased':deceased,
            'confirmed':confirmed,
            'recovered':recovered
            
         
        }
       
        
    return render(request, 'covidapp/stateview.html',data)

    
def statesearch(request):
    
    statelist={'MH' : 'Maharashtra', 'TN' : 'Tamil Nadu', 'DL' : 'Delhi', 'GJ' : 'Gujarat', 'UP' : 'Uttar Pradesh', 'RJ' : 'Rajasthan', 'MP' : 'Madhya Pradesh', 'WB' : 'West Bengal', 'UN' : 'State Unassigned', 'KA' : 'Karnataka', 'HR' : 'Haryana', 'BR' : 'Bihar', 'AP' : 'Andhra Pradesh', 'JK' : 'Jammu and Kashmir', 'TG' : 'Telangana', 'OR' : 'Odisha', 'AS' : 'Assam', 'PB' : 'Punjab', 'KL' : 'Kerala', 'UT' : 'Uttarakhand', 'JH' : 'Jharkhand', 'CT' : 'Chhattisgarh', 'TR' : 'Tripura', 'HP' : 'Himachal Pradesh', 'GA' : 'Goa', 'MN' : 'Manipur', 'CH' : 'Chandigarh', 'PY' : 'Puducherry', 'LA' : 'Ladakh', 'NL' : 'Nagaland', 'MZ' : 'Mizoram', 'AR' : 'Arunachal Pradesh', 'ML' : 'Meghalaya', 'AN' : 'Andaman and Nicobar Islands', 'DN' : 'Dadra and Nagar Haveli and Daman and Diu', 'SK' : 'Sikkim', 'LD' : 'Lakshadweep' }
    
    state_list=list(statelist)


    countrylist=['AF', 'AL', 'AX', 'AS', 'DZ', 'AD', 'AO', 'AI', 'AG', 'AQ', 'AU', 'AT', 'BH', 'BD', 'BJ', 'BZ', 'AR', 'AM', 'BA', 'AW', 'AZ', 'BS', 'BN', 'BQ', 'BY', 'BB', 'IO', 'BM', 'BE', 'CM', 'BT', 'BO', 'KH', 'CF', 'BW', 'TD', 'BG', 'BV', 'BR', 'CC', 'CO', 'CA', 'BF', 'BI', 'CR', 'CV', 'KY', 'CK', 'CN', 'CW', 'CY', 'CX', 'CL', 'DO', 'KM', 'CG', 'CD', 'DM', 'GQ', 'CI', 'HR', 'CU', 'ER', 'CZ', 'DK', 'DJ', 'FJ', 'FO', 'SV', 'EG', 'TF', 'PF', 'EC', 'GH', 'EE', 'ET', 'DE', 'FK', 'FI', 'GD', 'FR', 'GP', 'GA', 'GF', 'GN', 'GM', 'GW', 'HN', 'GI', 'GE', 'GR', 'GL', 'VA', 'GT', 'ID', 'GG', 'IN', 'GU', 'IM', 'IL', 'GY', 'HK', 'HT', 'HM', 'JE', 'HU', 'IS', 'IR', 'IQ', 'IE', 'IT', 'JM', 'JP', 'KP', 'LV', 'LI', 'MG', 'MT', 'YT', 'MN', 'MM', 'NC', 'NU', 'JO', 'KR', 'LB', 'LT', 'MW', 'MH', 'KE', 'MX', 'KG', 'ME', 'KI', 'LR', 'LA', 'MO', 'LY', 'MV', 'MK', 'MR', 'ML', 'MU', 'NA', 'PK', 'MD', 'NZ', 'MA', 'NF', 'NP', 'PY', 'NE', 'MC', 'MZ', 'NL', 'NO', 'NG', 'PT', 'OM', 'RU', 'LC', 'SM', 'PW', 'SC', 'PE', 'SI', 'PR', 'SS', 'RW', 'SJ', 'MF', 'TW', 'ST', 'TG', 'SL', 'TR', 'SB', 'UA', 'ES', 'UY', 'SZ', 'VG', 'TJ', 'TK', 'TM', 'AE', 'UZ', 'VI', 'ZW', 'KZ', 'KW', 'LS', 'LU', 'MY', 'MQ', 'FM', 'MS', 'NR', 'NI', 'MP', 'PA', 'PN', 'RE', 'SH', 'VC', 'SN', 'SX', 'ZA', 'SD', 'CH', 'TH', 'TT', 'TV', 'US', 'VE', 'PG', 'PL', 'RO', 'KN', 'WS', 'RS', 'SK', 'GS', 'SR', 'SY', 'TL', 'TN', 'UG', 'UM', 'VN', 'PS', 'PH', 'QA', 'BL', 'PM', 'SA', 'SG', 'SO', 'LK', 'SE', 'TZ', 'TO', 'TC', 'GB', 'VU', 'WF', 'ZM', 'EH', 'YE']
    
    countrylist=set(countrylist)
    if request.method == 'POST':
        code = request.POST.get("searchstate")
            
        if code in state_list:
                return redirect('stateview',sname=statelist[code], scode = code)
        elif code in countrylist:
                if code == 'IN':
                    return redirect('statewise')
                else:
                    return redirect('countryview',code=code)
        else:
                messages.info(request, 'No search found.')
                return redirect('api')


def dev(request):
    from datetime import date
    from datetime import datetime
    info = requests.get('https://covid19-update-api.herokuapp.com/api/v1/cases').json()
    totalCases = info['graphs']['totalCases']
    del totalCases['source']
    del totalCases['sourceLink']
    x = datetime.now(pytz.timezone('Asia/Kolkata'))
    today = date.today()

    d2 = today.strftime("%B %d, %Y")


    all_country = requests.get('https://corona-api.com/countries')
    all_country = all_country.json()
    country_data = all_country['data']
    return render(request,'covidapp/dev.html', {'d':d2, 'x':x, 'totalCases':totalCases, 'country_data':country_data})

def countryview(request,code):
    if code == 'IN':
        return redirect('statewise')
    else:    
        d=datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        url = 'http://corona-api.com/countries/{}'
        
        info = requests.get(url.format(code)).json()
        
        
        
        country=info['data']
        timeline=info['data']['timeline']
        l=len(timeline)
        l=l-1
        daywise = timeline[0:l: 10]
        daywise2 = daywise[::-1 ]
        daywise1={}
        for entry in daywise2:
            date = entry.pop('date')
            daywise1[date] = entry
                
        data={
            
            'info':country,
            'd':d,
            'timeline':daywise1,
        }
    return render(request,'covidapp/countryview.html',data)

def Helpline(request):
    
    regional= [
        {"loc": "Andhra Pradesh", "number": "+91-866-2410978"},
        {"loc": "Arunachal Pradesh", "number": "+91-9436055743"},
        {"loc": "Assam", "number": "+91-6913347770"},
        {"loc": "Bihar", "number": "104"},
        {"loc": "Chhattisgarh", "number": "104"},
        {"loc": "Goa", "number": "104"},
        {"loc": "Gujarat", "number": "104"},
        {"loc": "Haryana", "number": "+91-8558893911"},
        {"loc": "Himachal Pradesh", "number": "104"},
        {"loc": "Jharkhand", "number": "104"},
        {"loc": "Karnataka", "number": "104"},
        {"loc": "Kerala", "number": "+91-471-2552056"},
        {"loc": "Madhya Pradesh", "number": "+91-755-2527177"},
        {"loc": "Maharashtra", "number": "+91-20-26127394"},
        {"loc": "Manipur", "number": "+91-3852411668"},
        {"loc": "Meghalaya", "number": "108"},
        {"loc": "Mizoram", "number": "102"},
        {"loc": "Nagaland", "number": "+91-7005539653"},
        {"loc": "Odisha", "number": "+91-9439994859"},
        {"loc": "Punjab", "number": "104"},
        {"loc": "Rajasthan", "number": "+91-141-2225624"},
        {"loc": "Sikkim", "number": "104"},
        {"loc": "Tamil Nadu", "number": "+91-44-29510500"},
        {"loc": "Telengana", "number": "104"},
        {"loc": "Tripura", "number": "+91-381-2315879"},
        {"loc": "Uttarakhand", "number": "104"},
        {"loc": "Uttar Pradesh", "number": "18001805145"},
        {"loc": "West Bengal", "number": "1800313444222,+91-3323412600,"},
        {"loc": "Andaman and Nicobar Islands", "number": "+91-3192-232102"},
        {"loc": "Chandigarh", "number": "+91-9779558282"},
        {"loc": "Dadra and Nagar Haveli", "number": "104"},
        {"loc": "Daman & Diu", "number": "104"},
        {"loc": "Delhi", "number": "+91-11-22307145"},
        {"loc": "Jammu and Kashmir", "number": "+91-191-2520982,+91-194-2440283"},
        {"loc": "Ladakh", "number": "+91-1982-256462"},
        {"loc": "Lakshadweep", "number": "104"},
        {"loc": "Puducherry", "number": "104"},
    ]
    
    data={
        'helpline1':regional,

    }
    
    return render(request,'covidapp/helpline.html',data)



def about(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for the review. It motivates us to do more great stuff!')
    else:
        form = SuggestionForm()
    count = Suggestion.objects.all().count()
    return render(request, 'covidapp/about.html', {'form':form, 'count':count})



def map(request):
    all_country = requests.get('https://corona-api.com/countries')
    all_country = all_country.json()
    country_data = all_country['data']
    return render(request, 'covidapp/map.html',{'country_data':country_data})

def districtview(request,sname,dname):
    d=datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    response_state=requests.get('https://api.covid19india.org/state_district_wise.json')
    response_state=response_state.json()
    dis=response_state[sname]['districtData'][dname]


           

    all_districts = requests.get('https://api.covid19india.org/districts_daily.json')
    all_districts=all_districts.json()
    all_districts=all_districts['districtsDaily']
    state=all_districts[sname]
    district_timeline=state[dname]
    l=len(district_timeline)
    l=l-1
    timeline = district_timeline[l:0:-5]
    timeline2 = timeline[::-1]

    
    data={
        'district':timeline2,
        'dis':dis,
        'dname':dname,
        'd':d,

    }
    return render(request,'covidapp/districtview.html',data)

def wiki(request):
    return render(request, 'covidapp/wiki.html')

def essentials(request):
    category_list = ['Fundraisers', 'Free Food', 'Mental well being and Emotional Support', 'Accommodation and Shelter Homes', 'Delivery [Vegetables, Fruits, Groceries, Medicines, etc.]','CoVID-19 Testing Lab'] 
    data = requests.get('https://api.covid19india.org/resources/resources.json').json()
    data = data['resources']
    categorymake=request.GET.get('category')
    
    
    print(categorymake)
    return render(request, 'covidapp/essentials.html', {'data':data, 'category':categorymake, 'category_list':category_list})    
