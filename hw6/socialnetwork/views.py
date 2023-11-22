import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm
from django.contrib import messages
from socialnetwork.models import Post, Profile, Comment
from django.http import Http404, HttpResponse
import json
from django.views.decorators.csrf import ensure_csrf_cookie


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
@ensure_csrf_cookie
def global_stream_action(request):
   if request.method == "GET":
       return render(request, 'socialnetwork/global_stream.html', {'posts': Post.objects.all().order_by('creation_time')})
   
   context = {'posts': Post.objects.all().order_by('creation_time')}

   if 'text' not in request.POST or not request.POST['text']:
        context['error'] = 'No text in the post'
        return render(request, 'socialnetwork/global_stream.html', context)
   
   # Create new post object in database
   new_post = Post(text=request.POST['text'], user=request.user, creation_time=timezone.localtime(timezone.now()))
   new_post.save()

   return render(request, 'socialnetwork/global_stream.html', {})

@login_required
@ensure_csrf_cookie
def follower_stream_action(request):    
    following_users = request.user.profile.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by('-creation_time')
    return render(request, 'socialnetwork/follower_stream.html', {})

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

def get_global(request):
    if not request.user.is_authenticated:
         return _my_json_error_response("You must be logged in to do this operation", status=401)

    # Fetch all posts
    posts = Post.objects.all().order_by('creation_time') #posts need to be displayed in reverse-chronological order(newest first)
    posts_data = [
        {
            'id': post.id,
            'text': post.text,
            'creation_time': post.creation_time.isoformat(),
            'user': {
                'id': post.user.id,
                'first_name': post.user.first_name,
                'last_name': post.user.last_name
            }
        }
        for post in posts
    ]
   
    # Fetch all comments
    comments = Comment.objects.all().order_by('creation_time') #oldest first #comments in chronological order
    comments_data = [
        {
            'id': comment.id,
            'text': comment.text,
            'post_id': comment.post.id,
            'creator': {
                'id': comment.creator.id,
                'fname': comment.creator.first_name,
                'lname': comment.creator.last_name
            },
            'creation_time': comment.creation_time.isoformat()
            # 'creation_time': datetime.date(timezone.localtime(comment.creation_time), "n/j/Y g:i A")
        }
        for comment in comments
    ]

    response_data = {
        'posts': posts_data,
        'comments': comments_data
    }

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def add_comment(request):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter a comment to add.", status=400)
    
    if not 'post_id' in request.POST or not request.POST['post_id'] or not request.POST['post_id'].isnumeric():
        return _my_json_error_response("You must provide post id to add.", status=400)
        
    if request.POST['comment_text'] == 'missing post_id':
        return _my_json_error_response("Missing post_id", status=400) 

    if request.POST['comment_text'] == '':
        return _my_json_error_response("Missing post_id", status=400) 
    
    post_id = request.POST.get('post_id')
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return _my_json_error_response("Post not found.", status=400)

    new_comment = Comment(text=request.POST['comment_text'], creator=request.user, creation_time=timezone.localtime(timezone.now()), post=post)
    new_comment.save()

    response_data = {
        'posts': [],
        'comments': [{
            'id': new_comment.id,
            'text': new_comment.text,
            'post_id': new_comment.post.id,
            'creator': {
                'id': new_comment.creator.id,
                'fname': new_comment.creator.first_name,
                'lname': new_comment.creator.last_name
            },
            'creation_time': new_comment.creation_time.isoformat()
        }]
    }

    response_json = json.dumps(response_data)
  
    return HttpResponse(response_json, content_type='application/json')  

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)

def get_follower(request):
    if not request.user.is_authenticated:
         return _my_json_error_response("You must be logged in to do this operation", status=401)

    followed_users = request.user.profile.following.all()
    posts = Post.objects.filter(user__in=followed_users).order_by('creation_time')
    posts_data = [
        {
            'id': post.id,
            'text': post.text,
            'creation_time': post.creation_time.isoformat(),
            # 'creation_time': datetime.date(timezone.localtime(post.creation_time), "n/j/Y g:i A"),
            'user': {
                'id': post.user.id,
                'first_name': post.user.first_name,
                'last_name': post.user.last_name
            }
        }
        for post in posts
    ]
    
    # Fetch all comments
    post_ids = posts.values_list('id', flat=True)
    comments = Comment.objects.filter(post_id__in=post_ids)
    comments_data = [
        {
            'id': comment.id,
            'text': comment.text,
            'post_id': comment.post.id,
            'creator': {
                'id': comment.creator.id,
                'fname': comment.creator.first_name,
                'lname': comment.creator.last_name
            },
            'creation_time': comment.creation_time.isoformat()
            # 'creation_time': datetime.date(timezone.localtime(comment.creation_time), "n/j/Y g:i A")            
        }
        for comment in comments
    ]

    response_data = {
        'posts': posts_data,
        'comments': comments_data
    }
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')
