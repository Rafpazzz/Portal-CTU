from django.urls import path

from . import views


urlpatterns = [
    path('', views.manage_lab_objects, name='admin_lab_objects'),
    path('api/', views.lab_objects_api, name='admin_lab_objects_api'),
    path('api/<int:object_id>/', views.lab_object_detail_api, name='admin_lab_object_detail_api'),
    path('exportar/csv/', views.export_lab_objects_csv, name='admin_lab_objects_export_csv'),
    path('exportar/pdf/', views.export_lab_objects_pdf, name='admin_lab_objects_export_pdf'),
]
