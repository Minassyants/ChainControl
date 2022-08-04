from django.urls import path, include
from . import views

urlpatterns = [
    path('/',views.index, name='index'),
    path('CC/createRequest',views.createRequest, name='createRequest'),
    path('CC/login_user',views.login_user, name='login_user'),
    path('CC/logout_user',views.logout_user, name='logout_user'),
    path('CC',views.index, name='index'),
    path('CC/requests', views.requests, name="requests"),
    path('CC/requests_for_approval', views.requests_for_approval, name="requests_for_approval"),
    path('CC/requests_all', views.requests_all, name="requests_all"),
    path('CC/requests_my_requests', views.requests_my_requests, name="requests_my_requests"),
    ]
