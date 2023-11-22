from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from socialnetwork.forms import LoginForm, RegisterForm
from django.contrib import messages


def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        context['form_errors'] = form.errors
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        context['form_errors'] = form.errors
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    login(request, new_user)
    return redirect(reverse('home'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

@login_required
def global_stream_action(request):
   return render(request, 'socialnetwork/global_stream.html')

@login_required
def follower_stream_action(request):
   return render(request, 'socialnetwork/follower_stream.html')

@login_required
def profile_action(request):
    user = request.user  # Use the logged-in user when no username is provided in the URL

    # Prepare the context
    context = {
        'user': user,
        'bio': 'This is a dummy bio.',  
        'followed_users': [{'username': 'jane_lee', 'first_name': 'Jane', 'last_name': 'Lee'}],  # Update as needed
    }
    
    return render(request, 'socialnetwork/profile.html', context)

@login_required
def other_profile_action(request, username):
    #user = User.objects.get(username=username)

    user = User.objects.create_user(username=username, 
                                        password="b",
                                        email="b@b",
                                        first_name="b",
                                        last_name="b")
    user.save()

    context = {
        'other_user': user,
        'bio': 'This is a dummy bio.',  
    }
    
    return render(request, 'socialnetwork/other_profile.html', context)

