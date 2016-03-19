from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rooftop.views import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'rooftop.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',auth_views.login, {'template_name': 'login.html'}),
    url(r'^start/$',login_required(start)),
    url(r'^userprofile/$',login_required(UserprofileView.as_view())),
    url(r'^adduser/$',login_required(AddUserView.as_view())),
    url(r'^addgroup/$',login_required(AddGroupView.as_view())),
    url(r'^logout/$', auth_views.logout,{'next_page': '/'}),
]
