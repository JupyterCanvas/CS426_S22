# docs:
# function-based views: https://docs.djangoproject.com/en/3.2/topics/http/views/
# class-based views: https://docs.djangoproject.com/en/3.2/ref/class-based-views/
# classy class-based views: https://ccbv.co.uk/

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import Upload

from django.contrib.auth import authenticate, login, logout

from .decorators import unauthenticated_user, allowed_users, admin_only, instructor_only, student_only

from django.contrib import messages

from django.contrib.auth.decorators import login_required


@unauthenticated_user
def loginPage(request):
	
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')
			
			user = authenticate(request, username=username, password=password)
			
			if user is not None:
				login(request, user)
				return redirect('administrator')
			else:
				messages.error(request, 'username or password invalid')
				return render(request, 'registration/login.html')
				
		return render(request, 'registration/login.html')


#admin dashboard page, if user is not logged in they will be redirected back to the login page
#if user logged in and not admin they will be redirected to either student or instructor pages
@login_required(login_url='login')
@admin_only
def administrator(request):
	return render(request, 'administrator.html')
	
#directs user back to login page
def logoutUser(request):
	logout(request)
	return redirect('login')

#student dashboard page, if user is not logged in they will be redirected back to the login page
#if user logged in and not admin they will be redirected to either admin or instructor pages
@login_required(login_url='login')  
@student_only  
def student(request):
	return render(request, 'student.html')
	  
#instructor dashboard page, if user is not logged in they will be redirected back to the login page
#if user logged in and not admin they will be redirected to either student or admin pages
@login_required(login_url='login')    
@instructor_only
def instructor(request):
	return render(request, 'instructor.html')  


