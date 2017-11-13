from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^person/', include([
        url(r'^create_order/$', views.person_create_order, name="create_order"),
        url(r'^history_orders/$', views.person_history_orders, name="history_orders"),
        url(r'^current_orders/$', views.person_current_orders, name="current_orders"),
        url(r'^info_order/(?P<order_id>\d+)/$', views.person_info_order, name="info_order"),
    ], namespace='person')),

    url(r'^driver/', include([
        url(r'^list_orders/$', views.driver_list_orders, name="list_orders"),
        url(r'^current_orders/$', views.driver_current_orders, name="current_orders"),
        url(r'^history_orders/$', views.driver_history_orders, name="history_orders"),
        url(r'^complete_order/(?P<order_id>\d+)/$', views.complete_order, name="complete_order"),
        url(r'^perform_order', views.driver_perform_order_ajax, name="perform_order"),
        url(r'^car_edit/$', views.car_edit, name='car_edit')
    ], namespace='driver')),

    url(r'^profile_edit/$', views.profile_edit, name="profile_edit"),
    url(r'^profile_info/(?P<user_id>\d+)/', views.profile_info, name="profile_info"),
    url(r'^close_order/(?P<order_id>\d+)/$', views.close_order, name="close_order"),
    url(r'^cancel_order/(?P<order_id>\d+)/$', views.cancel_order, name="cancel_order"),
    url(r'^in_driver/$', views.in_driver, name="in_driver"),
    url(r'^in_person/$', views.in_person, name="in_person"),
    # GEO
    # url(r'^geo_access', views.geo_access_ajax, name="geo_access"),
    url(r'^geo_send_position/$', views.geo_send_position_ajax, name='geo_send_position'),
    url(r'^', views.home, name='home'),
]
