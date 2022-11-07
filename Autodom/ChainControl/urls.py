from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('CC/login_user',views.login_user, name='login_user'),
    path('CC/logout_user',views.logout_user, name='logout_user'),
    path('CC',views.index, name='index'),
    path('CC/missions', views.missions, name="missions"),
    path('CC/missions_list', views.MissionListView.as_view(), name="mission_list"),
    path('CC/createMission',views.MissionCreateView.as_view(), name='createMission'),
    path('CC/missions/<int:pk>', views.MissionDetailView.as_view(), name="mission_item"),
    path('CC/missions/<int:pk>/update', views.MissionUpdateView.as_view(), name="mission_update"),
    path('CC/missions/<int:model_id>/<int:pk>/print',views.request_print, name='mission_print'),
    path('CC/requests', views.requests, name="requests"),
    path('CC/requests_list', views.RequestListView.as_view(), name="request_list"),
    path('CC/createRequest',views.RequestCreateView.as_view(), name='createRequest'),
    path('CC/requests/<int:pk>', views.RequestDetailView.as_view(), name="request_item"),
    path('CC/requests/<int:pk>/update', views.RequestUpdateView.as_view(), name="request_update"),
    path('CC/requests/<int:model_id>/<int:pk>/print',views.request_print, name='request_print'),
    path('api/get_contracts',views.get_contracts,  name="get_contracts"),
    path('api/get_clients',views.get_clients,  name="get_clients"),
    path('api/get_individuals',views.get_individuals,  name="get_individuals"),
    path('api/get_bank_accounts',views.get_bank_accounts,  name="get_bank_accounts"),
    path('api/get_individual_bank_accounts',views.get_individual_bank_accounts,  name="get_individual_bank_accounts"),
    path('api/get_ordering_for_new_request',views.get_ordering_for_new_request, name="get_ordering_for_new_request"),
    path('api/get_approval_status', views.get_approval_status, name='get_approval_status'),
    path('api/get_approval_form/<id>', views.get_approval_form, name='get_approval_form'),
    path('api/get_request_search_form', views.get_search_form, name='get_search_form'),
    path('api/get_mission_search_form', views.get_mission_search_form, name='get_mission_search_form'),
    path('api/set_request_done/<model_id>/<id>', views.set_request_done, name='set_request_done'),
    path('api/set_request_canceled/<id>', views.set_request_canceled , name='set_request_canceled'),
    path('tg_api/reg_user', views.tg_reg_user, name='tg_reg_user'),
    path('tg_api/logout', views.tg_logout, name='tg_logout'),
    path('tg_api/get_auth_qrcode',views.tg_get_auth_qrcode, name='tg_get_auth_qrcode'),
    path('CC/docs',views.docs, name='docs'),
    path('CC/docs/create',views.create, name='create'),
    path('CC/docs/execution',views.execution, name='execution'),
    path('CC/docs/approval',views.approval, name='approval'),
    path('CC/docs/request_description',views.request_description, name='request_description'),
    path('CC/docs/main_screen_description',views.main_screen_description, name='main_screen_description'),
    path('CC/docs/app_description',views.app_description, name='app_description'),
    path('CC/docs/request_life_cycle',views.request_life_cycle, name='request_life_cycle'),
    ]
