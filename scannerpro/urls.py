from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_homepage, name='homepage'),
    path('scanner/', views.fetch_tickers_for_scanner, name='scanner_home'),
    path('ticker/create/', views.create_ticker, name='create_ticker'),
    path('ticker/<int:pk>/update/', views.update_ticker, name='update_ticker'),
    path('ticker/<int:pk>/delete/', views.delete_ticker, name='delete_ticker'),
    path('tickers/', views.list_tickers, name='list_tickers'),
    path('event-stream/', views.sse_event_view, name='event_stream'),
]
