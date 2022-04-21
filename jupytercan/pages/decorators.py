from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
	def wrapper_func(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('home')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):

			group = None
			if request.user.groups.exists():
				group = request.user.groups.all()[0].name

			if group in allowed_roles:
				return view_func(request, *args, **kwargs)
			else:
				return HttpResponse('You are not authorized to view this page')
		return wrapper_func
	return decorator


#only directs the user to the admin page if they have admin privelages, if they do not it sends them back to instructor or student
def admin_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if group == 'student':
			return redirect('student')

		if group == 'admin':
			return view_func(request, *args, **kwargs)
			
		if group == 'instructor':
			return redirect('instructor')

	return wrapper_function
	
#only directs the user to the instructor page if they have instructor privelages, if they do not it sends them back to admin or student
def instructor_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if group == 'student':
			return redirect('student')

		if group == 'admin':
			return redirect('administrator')
			
		if group == 'instructor':
			return view_func(request, *args, **kwargs)

	return wrapper_function

#only directs the user to the student page if they have student privelages, if they do not it sends them back to instructor or admin	
def student_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if group == 'student':
			return view_func(request, *args, **kwargs)

		if group == 'admin':
			return redirect('administrator')
			
		if group == 'instructor':
			return redirect('instructor')

	return wrapper_function
