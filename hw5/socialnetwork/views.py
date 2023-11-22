from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm
from django.contrib import messages
from socialnetwork.models import Post, Profile
from django.http import Http404, HttpResponse


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
    
    # Create a Profile instance for the new_user
    profile = Profile(user=new_user)
    
    profile.save()

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
   if request.method == "GET":
       return render(request, 'socialnetwork/global_stream.html', {'posts': Post.objects.all().order_by('-creation_time')})
   
   context = {'posts': Post.objects.all().order_by('-creation_time')}

   if 'text' not in request.POST or not request.POST['text']:
        context['error'] = 'No text in the post'
        return render(request, 'socialnetwork/global_stream.html', context)
   
   # Create new post object in database
   new_post = Post(text=request.POST['text'], user=request.user, creation_time=timezone.now())
   new_post.save()

   return render(request, 'socialnetwork/global_stream.html', {'posts': Post.objects.all().order_by('-creation_time')})

@login_required
def follower_stream_action(request):
    following_users = request.user.profile.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by('-creation_time')
    return render(request, 'socialnetwork/follower_stream.html', {'posts': posts})
   #return render(request, 'socialnetwork/follower_stream.html', {'posts': Post.objects.all().order_by('-creation_time')})

@login_required
def profile_action(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'GET':
        context = {'form': ProfileForm(initial={'bio': request.user.profile.bio})}
        return render(request, 'socialnetwork/profile.html', context)
    
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context = {'form': form}
        return render(request, 'socialnetwork/profile.html', context)
    
    pic = form.cleaned_data['picture']
    profile.picture = pic  # Update the picture in the profile
    profile.bio = form.cleaned_data.get('bio', profile.bio)  # Update bio as well
    profile.content_type = pic.content_type
    profile.save()

    # Prepare the context
    context = {
        'user': user,
        'bio': profile.bio,  
        'profile': profile,
        'form': form,  
    }
    
    return render(request, 'socialnetwork/profile.html', context)

@login_required
def other_profile_action(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    form = ProfileForm(request.POST, request.FILES)

    context = {
        'form': form,  
        'profile': other_user.profile
    }

    return render(request, 'socialnetwork/other_profile.html', context)

@login_required
def unfollow(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return render(request, 'socialnetwork/other_profile.html', {'profile': user_to_unfollow.profile})

@login_required
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return render(request, 'socialnetwork/other_profile.html', {'profile': user_to_follow.profile})

@login_required
def get_photo(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if not user.profile.picture:
        raise Http404

    return HttpResponse(user.profile.picture, content_type=user.profile.content_type)
