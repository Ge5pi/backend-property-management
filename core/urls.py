from django.urls import path

from .views import GetSignedURL, ModelChoicesListAPIView, UploadSignedURL

app_name = "core"

urlpatterns = [
    path("upload-signed-url/", UploadSignedURL.as_view(), name="upload_signed_url"),
    path("get-signed-url/", GetSignedURL.as_view(), name="get_signed_url"),
    path("model-choices/<str:model_label>/", ModelChoicesListAPIView.as_view(), name="model_choices"),
]
