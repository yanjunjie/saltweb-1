# coding: utf-8

from django.db.models import  Q
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render_to_response
from user_manager.models import *
from perm.models import *
from saltweb.api import *

@require_super_user
def user_add(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = gen_rand_pwd(8)
		email = request.POST.get('email','')
		usergroup = request.POST.get('usergroup','')
		role = request.POST.get('role','CU')
		is_active = request.POST.get('is_active','')
                mail_subject = u'SALTWEB用户添加成功'
                mail_msg = u"""
		Hi, %s
			您的用户名: %s
			您的角色: %s
			您的用户组: %s
			您的WEB登入密码: %s
			WEB地址: http://172.16.30.219
                """ %(username,username,role,usergroup,password)
		if usergroup:
			try:
				usergroup_obj = UserGroup.objects.get(name=usergroup)
                        	User.objects.create(
                                	username=username,
                                	password=md5_crypt(password),
                                	email=email,
                                	role=role,
                                	is_active=is_active,
                                	date_joined=datetime.datetime.now()
                        	)
				user = User.objects.get(username=username)
				user.group.add(usergroup_obj)
				send_mail(mail_subject,mail_msg,MAIL_FROM,[email],fail_silently=True)
				result = u'添加用户 %s 成功,密码已发至用户邮箱 %s' %(username,email)
			except Exception as e:
				error = u'添加用户 %s 失败 %s' %(username,e)
		else:
			try:
				user = User(
					username=username,
					password=md5_crypt(password),
					email=email,
					role=role,
					is_active=is_active,
					date_joined=datetime.datetime.now()
				)
				user.save()
				send_mail(mail_subject,mail_msg,MAIL_FROM,[email],fail_silently=True)
				result = u'添加用户 %s 成功,密码已发至用户邮箱 %s' %(username,email)
			except Exception as e:
				error = u'添加用户 %s 失败 %s' %(username,e)
	else:
		groupname = UserGroup.objects.all()
	return render_to_response('user_manager/user_add.html',locals())

@require_super_user
def usergroup_add(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
	if request.method == 'POST':
		groupname = request.POST.get('groupname')
		comment = request.POST.get('comment')
		try:
			group = UserGroup(
				name=groupname,
				comment=comment
			)
			group.save()
			result = u'添加用户组 %s 成功' %(groupname)
		except Exception as e:
			error = u'添加用户组 %s 失败 %s' %(groupname,e)
	return render_to_response('user_manager/usergroup_add.html',locals())

@require_super_user
def user_list(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
	search = request.GET.get('search','')
        if search:
                users = User.objects.filter(Q(username__icontains=search)).order_by('-date_joined')
        else:
                users = User.objects.all().order_by('-date_joined')
        '''分页'''
        try:
                page = int(request.GET.get('page','1'))
        except ValueError:
                page = 1
        pagenum = 10
        p = paging(page,pagenum,users)
        pt = p.pt()
        ppn = p.ppn()
        npn = p.npn()
        pn = p.pn()
        pl = p.pl()
        if page < 9:
                pr = p.pr()[0:9]
        elif int(pn) - page < 9:
                pr = p.pr()[int(pn)-9:int(pn)]
        else:
                pr = p.pr()[page-9:page+8]
	return render_to_response('user_manager/user_list.html',locals())

@require_super_user
def usergroup_list(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
        search = request.GET.get('search','')
        if search:
                groups = UserGroup.objects.filter(Q(name__icontains=search))
        else:
                groups = UserGroup.objects.all()
        '''分页'''
        try:
                page = int(request.GET.get('page','1'))
        except ValueError:
                page = 1
        pagenum = 10
        p = paging(page,pagenum,groups)
        pt = p.pt()
        ppn = p.ppn()
        npn = p.npn()
        pn = p.pn()
        pl = p.pl()
        if page < 9:
                pr = p.pr()[0:9]
        elif int(pn) - page < 9:
                pr = p.pr()[int(pn)-9:int(pn)]
        else:
                pr = p.pr()[page-9:page+8]
	return render_to_response('user_manager/usergroup_list.html',locals())

@require_super_user
def user_del_ajax(request):
	username = request.POST.get('username')
	try:
		User.objects.get(username=username).delete()
		ret = u'用户%s删除成功' %username
	except Exception as e:
		ret = u'用户删除失败, %s' %e
	return HttpResponse(ret)

@require_super_user
def usergroup_del_ajax(request):
	groupname = request.POST.get('groupname')
	try:
		UserGroup.objects.get(name=groupname).delete()
		ret = u'用户组%s删除成功' %groupname
	except Exception as e:
		ret = u'用户组删除失败: %s' %e
	return HttpResponse(ret)
	
@require_super_user
def user_edit(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
	if request.method == 'GET':
		id = request.GET.get('id','')
		result = User.objects.get(id=id)
		return render_to_response('user_manager/user_edit.html',locals())
	else:
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		email = request.POST.get('email','')
		role = request.POST.get('role','')
		is_active = request.POST.get('is_active','')
		if password:
			User.objects.filter(username=username).update(
				password = md5_crypt(password),
				email = email,
				role = role,
				is_active = is_active
			)
		else:
			User.objects.filter(username=username).update(
				email = email,
				role = role,
				is_active = is_active
			)
		return HttpResponseRedirect('/user_manager/user_list/')

@require_super_user
def usergroup_edit(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
	if request.method == 'GET':
		gid = request.GET.get('gid','')
		result = UserGroup.objects.get(id=gid)
		'''select all user'''
		users = User.objects.all()
		'''in the group user'''
		in_group_users = result.user_set.all()
		'''not in the group user'''
		not_in_group_users = [ user for user in users if user not in in_group_users ]
		return render_to_response('user_manager/usergroup_edit.html',locals())		
	else:
		groupname = request.POST.get('groupname')
		user_add_in_group = request.POST.getlist('in_group')
		user_remove_in_group = request.POST.getlist('not_in_group')
		comment = request.POST.get('comment','')
		user_group = UserGroup.objects.filter(name=groupname)
		user_group.update(name=groupname,comment=comment)
		if user_add_in_group:
			for add in user_add_in_group:
				add_user = User.objects.get(username=add)
				user_group[0].user_set.add(add_user)
		if user_remove_in_group:
			for remove in user_remove_in_group:
				remove_user = User.objects.get(username=remove)
				user_group[0].user_set.remove(remove_user)
		return HttpResponseRedirect('/user_manager/usergroup_list/')

@require_super_user
def g_user_list_ajax(request):
	'''查询用户组所属的用户'''
	groupname = request.GET.get('groupname','')
	group = UserGroup.objects.get(name=groupname)
	userlist = group.user_set.all()
	u = [ user.username for user in userlist ]
	return HttpResponse(json.dumps(u))

@require_super_user
def user_perm_edit(request):
	username,role_name,usergroup_name = get_session_user(request)
	session_role_id = request.session['role_id']
	nav = perm_nav(request)
	if request.method == "GET":
		uid = request.GET.get("id")
		perm_id = u_submenu_id(request)
		tree = parent_sub_tree()
	else:
		uid = request.POST.get('uid')
		sub_ids =request.POST.getlist('sub_menus')
		user_obj = User.objects.get(id=int(uid))
		'''先删除uid所有的submenus'''
		user_perms = user_obj.perm.all()
		for user_perm in user_perms:
			user_obj.perm.remove(user_perm)
		'''再将submenus授权为uid'''
		for sub_id in sub_ids:
			submenu_obj = Sub_Menu.objects.get(id=int(sub_id))
			user_obj.perm.add(submenu_obj)
		ret = u"授权完成,重新登入生效"
	return render_to_response('user_manager/user_perm_edit.html',locals())

def parent_sub_tree():
	'''遍历出父目录与子目录的树状结构'''
	parent_menus_list = Parent_Menu.objects.all()
	tree_dict = {}
	for parent_menu in parent_menus_list:
		tree_dict[parent_menu.name] = parent_menu.sub_menu_set.all
	return tree_dict

def u_submenu_id(request):
	'''根据用户的id,查询出对应的子菜单id'''
	u_obj = User.objects.get(id=request.GET.get("id"))
	u_submenus = u_obj.perm.all()
	u_sub_id = [ int(u_submenu.id) for u_submenu in u_submenus ]
	return u_sub_id
