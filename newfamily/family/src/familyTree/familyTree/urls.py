"""familyTree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from familytree.views import render_search,render_data_entry,get_data_from_search_form,get_data_from_entry_form,get_all_person_male\
    ,get_all_person_female,last_fill_select,get_name_filter,show_profile



urlpatterns = [
    path('admin/', admin.site.urls),

    path('search/', render_search, name='search'),
    path('search_form/', get_data_from_search_form,name="search_form"),

    path('entry/', render_data_entry,name='entry'),
    path('entry_form/', get_data_from_entry_form, name='entry_form'),

    path('name_filter', get_name_filter, name='name_filter'),

    path('fathers/', get_all_person_male, name='fatherslist'),
    path('mothers/', get_all_person_female, name='motherslist'),

    path('profile/<int:person_id>',show_profile,name="profile")

    # path('all/<str:gender>/',last_fill_select,name = "last_fill")
]
