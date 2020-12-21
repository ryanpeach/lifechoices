from django.conf.urls import include, path

urlpatterns = [
    path('payments/', include('payments.urls')),
]