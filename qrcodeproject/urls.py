"""qrcodeproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from adminapp import views as adminapp_views
from userapp import views as userapp_views
from mainapp import views as mainapp_views
from conductorapp import views as conductorapp_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/tracking/', include('conductorapp.urls')),


# create mainapp views
path('',mainapp_views.main_index,name='main_index'),
path('main-about/',mainapp_views.main_about,name='main_about'),
path('main-contact/',mainapp_views.main_contact,name='main_contact'),
path('main-parent/',mainapp_views.main_parent,name='main_parent'),
path('main-admin-login/',mainapp_views.main_admin_login,name='main_admin_login'),
path('main-conductor-login/',mainapp_views.main_conductor_login,name='main_conductor_login'),


# create adminapp views

path('admin-addnewstudent/',adminapp_views.admin_addnewstudent,name='admin_addnewstudent'),
path('admin-index/',adminapp_views.admin_index,name='admin_index'),
path('admin-manage-student/',adminapp_views.admin_managestudent,name='admin_managestudent'),
path('admin-busdelay/',adminapp_views.admin_busdelay,name='admin_busdelay'),
path('admin-feedback-analysis/',adminapp_views.admin_feedbackanalysis,name='admin_feedbackanalysis'),
path('admin-sentimentanalysis/',adminapp_views.admin_sentimentanalysis,name='admin_sentimentanalysis'),
# path('admin-home', adminapp_views.admin_home,name='admin_home'),



#create conductorapp views
path('conductor-bus-delay-update/', conductorapp_views.conductor_bus_delay, name='conductor_bus_delay'),
path('conductor-index/', conductorapp_views.conductor_dashboard, name='conductor_index'),
path('conductor-dashboard/',conductorapp_views.conductor_dashboard,name='conductor_dashboard'),
path('conductor-home-school/',conductorapp_views.conductor_home_school,name='conductor_home_school'),
path('conductor-boarding-status/',conductorapp_views.conductor_boarding_status,name='conductor_boarding_status'),
path('conductor-drop-status/',conductorapp_views.conductor_drop_status,name='conductor_drop_status'),
path('conductor-school-home/',conductorapp_views.conductor_school_home,name='conductor_school_home'),

#create userapp views
path('user-index/',userapp_views.user_index,name='user_index'),
path('user-about/',userapp_views.user_about,name='user_about'),
path('user-feedback/',userapp_views.user_feedback,name='user_feedback'),
path('user-myprofile/',userapp_views.user_myprofile,name='user_myprofile'),
path('user-view-status/',userapp_views.user_view_status,name='user_view_status'),
path('user-changepassword/',userapp_views.user_changepassword,name='user_changepassword'),
path('user-boarding-status/',userapp_views.boarding_status,name='boarding_status'),
path('user-dropping-status/',userapp_views.dropping_status,name='dropping_status'),
path('user-notification/',userapp_views.notification_status,name='notification_status'),
path('api/v1/routing/calculate_route/', userapp_views.api_calculate_route, name='api_calculate_route'),
] + static (settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)