# docs: https://docs.djangoproject.com/en/3.2/topics/http/urls/

from django.urls import path, include
from .views import ProjectsPageView, ChatPageView, RegisterView, DashboardView, FilesPageView, UploadFilesView #HomePageView, AboutPageView 
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
#    path('home/', HomePageView.as_view(), name='home'),
#    path('about/', AboutPageView.as_view(), name='about'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', views.home, name='home'),
   
]


# for use during development only, need to remove for production: 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
