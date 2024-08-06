from django.urls import path
from . import views


urlpatterns = [
    path('', views.scannerhome, name="scannerhome"),
   
]
