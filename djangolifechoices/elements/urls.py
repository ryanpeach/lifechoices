from django.urls import path
from elements import views
from django.contrib.auth import views as auth_views

app_name = 'elements'

urlpattern = [
    #plan views
    path('', views.plan_list, name='plan_list'),
    path('<int:year>/<int:month>/<int:day>/', views.plan_detail, name='plan_detail')
]