"""djangolifechoices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
import elements.views
# import login.views
# import payment.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', elements.views.home, name='home'),
    path('plan-dash/', include('django_plotly_dash.urls')),
#     path('login/', login.views.home, name='home'),
#     path('payment/', payment.views.payment_details, name='payment_details')
]