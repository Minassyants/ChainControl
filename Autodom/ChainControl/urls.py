from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('/',views.index, name='index'),
    path('CC/createRequest',views.createRequest, name='createRequest'),
    path('CC/login_user',views.login_user, name='login_user'),
    path('CC/logout_user',views.logout_user, name='logout_user'),
    path('CC',views.index, name='index'),
    path('CC/requests/<id>', views.request_item, name="request_item"),
    path('CC/requests', views.requests, name="requests"),
    path('CC/requests_for_approval', views.requests_for_approval, name="requests_for_approval"),
    path('CC/requests_all', views.requests_all, name="requests_all"),
    path('CC/requests_my_requests', views.requests_my_requests, name="requests_my_requests"),
    path('CC/requests_to_be_done', views.requesrs_to_be_done, name="requests_to_be_done"),
    path('api/get_contracts',views.get_contracts,  name="get_contracts"),
    path('api/get_bank_accounts',views.get_bank_accounts,  name="get_bank_accounts"),
    path('api/get_ordering_for_new_request',views.get_ordering_for_new_request, name="get_ordering_for_new_request"),
    path('api/get_approval_status', views.get_approval_status, name='get_approval_status'),
    path('api/get_approval_form/<id>', views.get_approval_form, name='get_approval_form'),
    path('api/get_request_search_form', views.get_search_form, name='get_search_form'),
    path('api/set_request_done/<id>', views.set_request_done, name='set_request_done'),
    path('api/set_request_canceled/<id>', views.set_request_canceled , name='set_request_canceled'),

    ]
