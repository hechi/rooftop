from django.conf.urls import patterns, include, url
from django.contrib import admin
from rooftop.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rooftop.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^start/$',start),
    url(r'^userprofile/$',userprofile),
    url(r'^logout/$', 'django.contrib.auth.views.logout',{'next_page': '/'}),
)
