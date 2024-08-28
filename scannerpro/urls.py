from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name="homepage"),
    # path('scanner/', views.scannerhome, name="scannerhome"),
    path('tickerlist/', views.ticker_list, name='ticker_list'),
    path('create/', views.ticker_create, name='ticker_create'),
    path('update/<int:pk>/', views.ticker_update, name='ticker_update'),
    path('delete/<int:pk>/', views.ticker_delete, name='ticker_delete'),
   
]



