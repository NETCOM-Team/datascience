from django.urls import path, include

urlpatterns = [
    path('asn', include('api.urls')),
    path('ip', include('api.urls')),
]
