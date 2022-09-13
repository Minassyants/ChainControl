from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('CC/createRequest',views.RequestCreateView.as_view(), name='createRequest'),
    path('CC/login_user',views.login_user, name='login_user'),
    path('CC/logout_user',views.logout_user, name='logout_user'),
    path('CC',views.index, name='index'),
    path('CC/requests/<int:pk>', views.RequestDetailView.as_view(), name="request_item"),
    path('CC/requests/<int:pk>/update', views.RequestUpdateView.as_view(), name="request_update"),
    path('CC/requests', views.requests, name="requests"),
    path('CC/requests_list', views.RequestListView.as_view(), name="request_list"),
    path('api/get_contracts',views.get_contracts,  name="get_contracts"),
    path('api/get_clients',views.get_clients,  name="get_clients"),
    path('api/get_bank_accounts',views.get_bank_accounts,  name="get_bank_accounts"),
    path('api/get_ordering_for_new_request',views.get_ordering_for_new_request, name="get_ordering_for_new_request"),
    path('api/get_approval_status', views.get_approval_status, name='get_approval_status'),
    path('api/get_approval_form/<id>', views.get_approval_form, name='get_approval_form'),
    path('api/get_request_search_form', views.get_search_form, name='get_search_form'),
    path('api/set_request_done/<id>', views.set_request_done, name='set_request_done'),
    path('api/set_request_canceled/<id>', views.set_request_canceled , name='set_request_canceled'),
    path('tg_api/reg_user', views.tg_reg_user, name='tg_reg_user')
    ]
