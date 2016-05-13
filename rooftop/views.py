# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.template import Context
from django.template.response import TemplateResponse
from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.conf import settings
import json
import ldap
import ldap.modlist as modlist
from passlib.hash import ldap_md5 as lsm
from .forms import UserprofileForm, AddUserForm, AddGroupForm

from .models import LdapUser

import sys, traceback

def custom_login(request, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect('start/')
    else:
        return login(request,**kwargs)

@login_required
def start(request):
    template = get_template('start.html')
    param = getHeaderParam(request)

    context = Context(param)
    html = template.render(context)
    return HttpResponse(html)

def getHeaderParam(request):
    param = {}
    groups=[]

    if isUserInGroup(request.user.username,"admin"):
        group={}
        group['icon']="fa-wrench"
        group['link']="/manage/"
        group['name']="Admin"
        groups.append(group)

    param['displayname'] = request.user.first_name
    param['groups'] = groups
    return param

class UserprofileView(View):
    template_name = 'userprofileview.html'

    def get(self, request, *args, **kwargs):
        param = {}
        param=getHeaderParam(self.request)

        userfields=dict([])
        userfields['EMail']=request.user.email
        userfields['Username']=request.user.username
        userfields['Full Name']=request.user.first_name + " " + request.user.last_name

        param['userfields']=userfields
        param['ldapGroups']=getGroupsOfUser(request.user.username)

        return render(request, self.template_name, param)

class UserprofilePasswordChange(View):
    form_class = UserprofileForm
    template_name = 'userpasswordchange.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        return render(request, self.template_name, param)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        if form.is_valid():
            # <process form cleaned data>
            if form['newPassword'].value() != form['confirmPassword'].value():
                # print("not the same")
                param['form']=form
                param['statusError']=str("Passwords did not match, please try again.")
                return render(request, self.template_name, param)
            param['form'] = self.form_class()
            if changePassword(request,form['oldPassword'].value(),form['newPassword'].value()):
                param['status']=("Password has been changed.")
            else:
                param['statusError']=("Wrong password, please try again.")
        else:
            param['statusError']=("Invalid informations, please try again.")

        return render(request, self.template_name, param)

class AddUserView(View):
    form_class = AddUserForm
    template_name = 'add.html'

    def get(self, request, *args, **kwargs):
        #TODO check if user is in administration group
        form = self.form_class()
        param={}
        param=getHeaderParam(self.request)
        param['formtitle']='Add User'
        param['form']=form
        return render(request, self.template_name, param)

    def post(self, request, *args, **kwargs):
        #TODO check if user is in administration group
        form = self.form_class(request.POST)
        check=False
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        if form.is_valid() and isUserInGroup(request.user.username,settings.AUTH_LDAP_ADMIN_GROUP):
            # <process form cleaned data>
            uid= form['username'].value()
            cn= form['firstname'].value()
            sn= form['lastname'].value()
            mail= form['email'].value()
            password= form['password'].value()
            user = LdapUser(cn,sn,uid,mail,password)
            check=addUserToLdap(user)

        return HttpResponse(json.dumps(check), content_type="application/json")

class AddGroupView(View):
    form_class = AddGroupForm
    template_name = 'add.html'

    def get(self, request, *args, **kwargs):
        #TODO check if user is in administration group
        form = self.form_class()
        param={}
        param=getHeaderParam(self.request)
        param['formtitle']='Add Group'
        param['form']=form
        return render(request, self.template_name, param)

    def post(self, request, *args, **kwargs):
        #TODO check if user is in administration group
        form = self.form_class(request.POST)
        check=False
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        if form.is_valid() and isUserInGroup(request.user.username,settings.AUTH_LDAP_ADMIN_GROUP):
            # <process form cleaned data>
            groupname = form['groupname'].value()
            description = form['description'].value()
            username = request.user.username
            check=addGroupToLdap(groupname,description,username)

        return HttpResponse(json.dumps(check), content_type="application/json")

class AdminView(View):
    template_name = 'adminpage.html'

    def get(self, request, *args, **kwargs):
        #TODO check if user is in administration group
        param={}
        param=getHeaderParam(self.request)
        param['ldapUsers'] = getAllUserInformations()
        param['ldapGroups'] = getAllGroups()
        param['formGroup']=AddGroupForm()
        param['formUser']=AddUserForm()
        return render(request, self.template_name, param)

def addUserToLdap(user):
    check = False
    try:
        # Open a connection
        con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

        # Bind/authenticate with a user with apropriate rights to add objects
        con.simple_bind_s(settings.AUTH_LDAP_BIND_DN,str(settings.AUTH_LDAP_BIND_PASSWORD))
        # The dn of our new entry/object
        dn="uid="+user.getUid()+","+str(settings.AUTH_LDAP_BASE_USER_DN)

        # A dict to help build the "body" of the object
        # TODO: clean this
        attrs = {}
        attrs['objectclass'] = [str('inetOrgPerson').encode('utf-8'),str('top').encode('utf-8'),str('person').encode('utf-8'),str('shadowAccount').encode('utf-8'),str('posixAccount').encode('utf-8')]
        attrs['cn'] = [str(user.getFirstname()).encode('utf-8')]
        attrs['displayname'] = [str(user.getDisplayname()).encode('utf-8')]
        attrs['mail'] = [str(user.getMail()).encode('utf-8')]
        attrs['sn'] = [str(user.getLastname()).encode('utf-8')]
        attrs['uid'] = [str(user.getUid()).encode('utf-8')]
        attrs['userpassword'] = [str(lsm.encrypt(user.getPassword())).encode('utf-8')]

        # necessary for posixAccount
        attrs['gidNumber']=[str(1000).encode('utf-8')]
        attrs['homeDirectory']=[str('/home/').encode('utf-8')+str(user.getUid()).encode('utf-8')]
        # TODO generate uniq uidNumber
        # TODO check if its uniq
        attrs['uidNumber']=[str(1000).encode('utf-8')]
        #print(attrs)
        # Convert our dict to nice syntax for the add-function using modlist-module
        ldif = modlist.addModlist(attrs)

        # Do the actual synchronous add-operation to the ldapserver
        #print('add_s')
        #print(type(dn))
        #print(type(ldif))
        con.add_s(dn,ldif)

        # Its nice to the server to disconnect and free resources when done
        con.unbind_s()
        check = True
    except ldap.LDAPError:
    #except Exception:
        traceback.print_exc(file=sys.stdout)
    return check

def addGroupToLdap(groupname,description,username):
    check = False
    try:
        # Open a connection
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

        # Bind/authenticate with a user with apropriate rights to add objects
        l.simple_bind_s(settings.AUTH_LDAP_BIND_DN,str(settings.AUTH_LDAP_BIND_PASSWORD))

        # The dn of our new entry/object
        dn="cn="+groupname+","+str(settings.AUTH_LDAP_BASE_GROUP_DN)

        member="uid="+username+","+str(settings.AUTH_LDAP_BASE_USER_DN)

        # A dict to help build the "body" of the object
        attrs = {}
        attrs['objectclass'] = [str('groupOfNames').encode('utf-8')]
        attrs['cn'] = str(groupname).encode('utf-8')
        attrs['description'] = str(description).encode('utf-8')
        attrs['member']=[str(member).encode('utf-8')]
        attrs['owner']=[str(member).encode('utf-8')]
        # Convert our dict to nice syntax for the add-function using modlist-module
        ldif = modlist.addModlist(attrs)

        # Do the actual synchronous add-operation to the ldapserver
        l.add_s(dn,ldif)

        # Its nice to the server to disconnect and free resources when done
        l.unbind_s()
        check = True
    except ldap.LDAPError:
        traceback.print_exc(file=sys.stdout)
    return check

def isUserInGroup(username,groupname):
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter = "(&(objectClass=groupOfNames)(CN="+groupname+"))"
    isInGroup=False

    try:
            ldap_result_id = l.search(settings.AUTH_LDAP_BASE_GROUP_DN, searchScope, searchFilter, retrieveAttributes)
            result_set = []
            res = {}
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                #print result_data
                if (result_data == []):
                    break
                else:
                    #print "check"
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        # find user in group
                        for u in result_data[0][1]['member']:
                            #print(str(u).split("uid=")[1].split(",")[0])
                            if str(u).split("uid=")[1].split(",")[0] == username:
                                isInGroup=True
            l.unbind_s()
    except ldap.LDAPError:
        traceback.print_exc(file=sys.stdout)

    return isInGroup

def changePassword(request,oldPassword,newPassword):
    retValue = False
    user = request.user

    # Open a connection
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

    # The dn of our new entry/object
    dn="uid="+user.username+","+settings.AUTH_LDAP_BASE_USER_DN

    try:
        # Bind/authenticate with a user with apropriate rights to add objects
        l.simple_bind_s(dn,oldPassword)
        l.passwd_s(dn,oldPassword,newPassword)
        user.set_password(newPassword)
        user.save()
        retValue=True
    except:
        traceback.print_exc(file=sys.stdout)
        retValue=False

    # Its nice to the server to disconnect and free resources when done
    #print(retValue)
    l.unbind_s()
    return retValue

def getAllUsers():
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter = "(objectClass=posixAccount)"
    users=[]

    try:
            ldap_result_id = l.search(settings.AUTH_LDAP_BASE_USER_DN, searchScope, searchFilter, retrieveAttributes)
            result_set = []
            res = {}
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                #print result_data
                if (result_data == []):
                    break
                else:
                    #print "check"
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        for entry in result_data:
                                try:
                                    uid=entry[1]['uid'][0]
                                except:
                                    uid="ERROR"
                                try:
                                    cn=entry[1]['cn'][0]
                                except:
                                    cn="ERROR"
                                try:
                                    sn=entry[1]['sn'][0]
                                except:
                                    sn="ERROR"
                                try:
                                    mail=entry[1]['mail'][0]
                                except:
                                    mail="ERROR"
                                user=LdapUser(encMsg(cn),encMsg(sn),encMsg(uid),encMsg(mail))
                                #user.display()
                                users.append(user)
            l.unbind_s()
    except ldap.LDAPError:
        traceback.print_exc(file=sys.stdout)
    return users

def getAllGroups():
    #print "return all groups from ldap"
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter = "(objectClass=groupOfNames)"
    groups=[]

    try:
            ldap_result_id = l.search(settings.AUTH_LDAP_BASE_GROUP_DN, searchScope, searchFilter, retrieveAttributes)
            result_set = []
            res = {}
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                #print result_data
                if (result_data == []):
                    break
                else:
                    #print "check"
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        for entry in result_data:
                                cn=entry[1]['cn'][0]
                                try:
                                    description=entry[1]['description'][0]
                                except:
                                    description="None"
                                member=[]
                                for mem in entry[1]['member']:
                                    #member.append(str(mem.split(str("uid=").encode('utf-8'))[1].split(str(",").encode('utf-8'))[0]).encode('utf-8'))
                                    member.append(encMsg(mem.split(str("uid=").encode('utf-8'))[1].split(str(",").encode('utf-8'))[0]).encode('utf-8'))

                                group={}
                                group['cn']=cn
                                group['cnDisplay']=encMsg(cn).replace(" ","_").replace(".","")[:1].upper
                                group['member']=member
                                group['description']=description
                                #print group
                                groups.append(group)
            l.unbind_s()
    except ldap.LDAPError:
        traceback.print_exc(file=sys.stdout)
    return groups

def modGroup(request):
    check = False
    if isUserInGroup(request.user.username,settings.AUTH_LDAP_ADMIN_GROUP):
        if 'modGroupname' in request.POST and 'modDescription' in request.POST:
            groupname=request.POST['modGroupname']
            description=request.POST['modDescription']
            check=modGroupInLdap(groupname,description)
        if 'modGroupname' in request.POST and 'addUser' in request.POST:
            check=modUserToGroup(request.POST['addUser'],request.POST['modGroupname'],False)
        if 'modGroupname' in request.POST and 'delUser' in request.POST:
            check=modUserToGroup(request.POST['delUser'],request.POST['modGroupname'],True)
    return HttpResponse(json.dumps(check), content_type="application/json")

def modUserToGroup(username,groupname,removeFlag=False):
    check = False
    if not isUserInGroup(username,groupname) or removeFlag:
        # Open a connection
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

        # Bind/authenticate with a user with apropriate rights to add objects
        l.simple_bind_s(settings.AUTH_LDAP_BIND_DN,str(settings.AUTH_LDAP_BIND_PASSWORD))

        # The dn of our new entry/object
        dn="uid="+str(username)+","+str(settings.AUTH_LDAP_BASE_USER_DN)

        ## The next lines will also need to be changed to support your search requirements and directory
        baseDN = str(settings.AUTH_LDAP_BASE_GROUP_DN)
        searchScope = ldap.SCOPE_SUBTREE
        ## retrieve all attributes - again adjust to your needs - see documentation for more options
        retrieveAttributes = None
        #searchFilter = "(&(objectClass=groupOfNames)(CN=owncloud))"
        searchFilter = "(&(objectClass=groupOfNames)(CN="+groupname+"))"

        try:
            ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
            result_set = []
            res = {}
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    ## here you don't have to append to a list
                    ## you could do whatever you want with the individual entry
                    ## The appending to list is just for illustration.
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        # add user to group
                        result_data[0][1]['member'].append(dn)
                        result_set.append(result_data)
            members = []
            for r in result_set[0][0][1]['member']:
                #print(str(r)+"!="+str(dn)+" FLAG:"+str(removeFlag))
                if r != dn or (removeFlag == False and r == dn):
                    #print(type(r)==bytes)
                    if(type(r)==bytes):
                        members.append(r)
                    else:
                        members.append(str(r).encode('utf-8'))
            print(members)
            attr=[(ldap.MOD_REPLACE,'member',members)]
            l.modify_s('cn='+str(groupname)+","+str(baseDN),attr)

            l.unbind_s()
            check=True
        #print result_set
        except ldap.LDAPError:
            traceback.print_exc(file=sys.stdout)
            check=False
    else:
        check = True
    return check

def getUsersOfGroup(groupname):
    #print "return users of given group"
    groups=getAllGroups()
    for group in groups:
        if group['cn']==groupname:
            return group['member']

def getGroupsOfUser(username):
    #print "return all groups where user is memberof"
    groups=getAllGroups()
    listOfGroups=[]
    for group in groups:
        #print(type(group['member'][0]))
        #print(type(str(username).encode('utf-8')))
        if str(username) in str(group['member']):
            listOfGroups.append(group['cn'])
    return listOfGroups

def getAllUserInformations():
    users = getAllUsers()
    info=[]
    for u in users:
        userInfos={}
        userInfos['user']=u
        userInfos['groups']=getGroupsOfUser(u.getUid())
        info.append(userInfos)
    return info


def encMsg(msg):
    dec=""
    try:
        dec = msg.decode('utf-8')
    except:
        try:
            msgA = unicode(msg.encode('iso-8859-1'),'iso-8859-1')
            dec = msgA
        except:
            dec = "ERROR CAN NOT BE PRINTED"
    return dec
