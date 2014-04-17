from django.conf.urls import patterns, include, url
urlpatterns = patterns('',
    url(r'^login/$', 'ImageUser.views.user_login', name='login'),
    url(r'^logout/$', 'ImageUser.views.user_logout', name='logout'),
    url(r'^register/$', 'ImageUser.views.user_register', name='register'),
)
