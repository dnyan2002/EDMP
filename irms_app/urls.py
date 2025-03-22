
from django.urls import path, include, re_path
from irms_app import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home', views.home, name="home"),
    path('report', views.report, name="report"),
    path('user-register', views.user_register, name="user"),
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root' : settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$',serve,{'document_root' : settings.STATIC_ROOT}),
]