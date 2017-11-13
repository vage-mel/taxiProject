from django.conf.urls import url

import apps.loginsys.views

urlpatterns = [
    url(r'^login/$', apps.loginsys.views.login, name='login'),
    url(r'^logout/$', apps.loginsys.views.logout, name='logout'),
    url(r'^register/(driver|user|reg_phone)/$', apps.loginsys.views.register, name='register'),
    url(r'^register/$', apps.loginsys.views.register),
    url(r'^register/car/$', apps.loginsys.views.register_car),
    url(r'^ajax_send_pin/$', apps.loginsys.views.ajax_send_pin, name="ajax_send_pin"),
]
