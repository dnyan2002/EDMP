
from django.urls import path, include, re_path
from irms_app import views
from django.views.static import serve
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'pid-data', views.PIDDataViewSet)
router.register(r'report',views.ReportViewset, basename='report')

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('pid_data/', views.pid_data, name="pid_data"),
    path('report', views.report, name="report"),
    path('feedstock-report/', views.feedstock_report, name='feedstock_report'),
    path('powerconsumption-report/', views.powerconsumption_report, name='powerconsumption_report'),
    path('create/', views.create_user, name='create_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('bags-generator-report/', views.bagsgenerated_report, name='bagsgenerar_report'),
    path('biogas-reports/', views.biogas_report_json, name='biogas-report-json'),
    path('api/', include(router.urls), name="route_urls"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root' : settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$',serve,{'document_root' : settings.STATIC_ROOT}),
    # path('dashboard/', views.dashboard_view, name='dashboard'),
    path('manual-entry/', views.cost_entry_view, name='manual_entry'),
    path('running_hours/', views.running_hours, name='running_hours'),
    path('driver-status', views.driver_status, name='driver_status'),
    # path('biogas-reports/', views.biogas_report_list, name='biogas-report-list'),
]