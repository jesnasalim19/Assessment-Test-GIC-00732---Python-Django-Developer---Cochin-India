from django.urls import path
from .views import CSVUploadView,FileUpload

urlpatterns = [
    path('', FileUpload.as_view(), name='file-upload'),
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
]
