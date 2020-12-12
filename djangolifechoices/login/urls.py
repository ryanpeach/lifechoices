from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from mysite.core import views as core_views

urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    url(r'^admin/', admin.site.urls),
]

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'