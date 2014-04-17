from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, cookie
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django.template import RequestContext
from forms import UserForm
# Create your views here.

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse('fail', status=400)
        else:
            return HttpResponseRedirect(reverse('login'))
    elif request.method == 'GET':
        return render_to_response('ImageUser/index.html', context_instance = RequestContext(request))

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def user_register(request):
    context = RequestContext(request)

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))

    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.is_active = True
            user.save()

            registered = True

            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponse('invalid', status=500)
    else:
        user_form = UserForm()

    return render_to_response('User/register.html', {'user_form': user_form, \
        'registered': registered}, context)
