
from django.urls import path, include, re_path
from irms_app import views
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'pid-data', views.PIDDataViewSet)

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
    path('api/', include(router.urls), name="route_urls"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]