from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Cloud Project Admin"
admin.site.site_title = "Cloud Project Admin Portal"
admin.site.index_title = "Project Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("irms_app.urls"), name="irms_urls")
    
]
