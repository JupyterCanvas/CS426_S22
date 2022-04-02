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

from .decorators import unauthenticated_user, allowed_users, admin_only

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
				return redirect('home')
			else:
				messages.info(request, 'Username OR password is incorrect')
		context = {}
		return render(request, 'registration/login.html', context)



@login_required(login_url='login')
@admin_only
def home(request):
	return render(request, 'dashboard.html')

def logoutUser(request):
	logout(request)
	return redirect('login')

	
class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
@login_required(login_url='login')    
def student(request):
	context = {}
	return render(request, 'student.html', context)  
	
@login_required(login_url='login')    
def instructor(request):
	context = {}
	return render(request, 'instructor.html', context)  


