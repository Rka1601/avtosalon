from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/agreement/', views.purchase_agreement, name='purchase_agreement'),
    path('api/models/', views.get_models, name='get_models'),
    path('car/<int:car_id>/inspection/', views.inspection_request, name='inspection_request'),
    path('get-available-times/', views.get_available_times, name='get_available_times'),
    path('car/<int:car_id>/upload-photos/', views.upload_car_photos, name='upload_car_photos'),
]