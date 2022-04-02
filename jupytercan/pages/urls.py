# docs: https://docs.djangoproject.com/en/3.2/topics/http/urls/

from django.urls import path, include
from .views import DashboardView
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', views.home, name='home'),
    path('student/', views.student, name="student"),
    path('instructor/', views.instructor, name="instructor"),
   
]


# for use during development only, need to remove for production: 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
