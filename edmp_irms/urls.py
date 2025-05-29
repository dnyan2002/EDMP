from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings

admin.site.site_header = "Cloud Project Admin"
admin.site.site_title = "Cloud Project Admin Portal"
admin.site.index_title = "Project Administration"

urlpatterns = [
    path('', include("irms_app.urls"), name="irms_urls"),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root' : settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$',serve,{'document_root' : settings.STATIC_ROOT}),
]
