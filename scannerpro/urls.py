from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_homepage, name='homepage'),
    path('scanner/', views.fetch_tickers_for_scanner, name='scanner_home'),
    path('dummy/', views.dummy_homepage, name='dummy_homepage'),
    path('ticker/create/', views.create_ticker, name='create_ticker'),
    path('ticker/<int:pk>/update/', views.update_ticker, name='update_ticker'),
    path('ticker/<int:pk>/delete/', views.delete_ticker, name='delete_ticker'),
    path('tickers/', views.list_tickers, name='list_tickers'),
    path('event-stream/', views.sse_event_view, name='event_stream'),
    # path('histdata_update_db', views.histdata_update_db, name="histdata"),
    path('api/get_ticker_data', views.get_ticker_data, name='get_ticker_data'),
    path('api/get_tickers', views.fetch_tickers_for_scanner, name='get_tickers'),  # New endpoint for populating dropdown
    path('api/home', views.api_home, name='api_home'),
    path('dynamicscanner/', views.dynamicscanner, name='dynamicscanner'),
]
