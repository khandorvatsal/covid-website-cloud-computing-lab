from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    path('dev/',views.dev,name='dev'),
    path('',views.api,name='api'),
    path('global/',views.globalview,name='globalview'),
    path('india/',views.statewise,name='statewise'),
    path('india/<sname>/<scode>',views.stateview,name='stateview'),
    path('country/<code>/',views.countryview,name='countryview'),
    path('search/',views.statesearch,name='statesearch'),
    path('helpline/',views.Helpline,name='Helpline'),
    path('about/', views.about, name='about'),
    path('map/', views.map, name='map'),
    path('wiki/', views.wiki, name='wiki'),
    path('india/<sname>/<dname>/', views.districtview, name='districtview'),
    path('essentials/', views.essentials, name='essentials'),
    
    
]
