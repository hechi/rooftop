from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rooftop.views import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'rooftop.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',auth_views.login, {'template_name': 'login.html'}),
    url(r'^start/$',start),
    url(r'^userprofile/$',userprofile),
    url(r'^logout/$', auth_views.logout,{'next_page': '/'}),
]
