from django.http      import HttpResponse, HttpResponseRedirect, Http404
from django.template  import RequestContext
from django.shortcuts import render_to_response, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from frontend.models import Client, MediaType, Job, Package, File, ClientPackageAvailability

from frontend.forms import ClientForm, MediaTypeForm, PackageForm, JobForm

####################
# Helper Functions #
####################
def has_permissions(user, action, object_id):
    """
    Think about how I am going to implement permissions
    * Has someone online got a good method?
    * What levels of permissions?
        * Superuser
            * Not Restricted
        * User
            * Has Content Restriction
            * Has Job Queue Restriction
            * Has Package Restriction

    Permission Actions:
    * view_client
    * view_job
    """
    allowed = (True, 'Allowed.')
    denied_not_super   = (False, 'You are not a Super User.')
    denied_not_allowed = (False, 'You are missing the required privileges.')

    if action == 'view_client':
        client = Client.objects.get(id=object_id)
        if client and client.user == user:
            return allowed
            
    return allowed
    
def get_package_and_permissions(package_id, action):
    package = Package.objects.get(id=package_id)

    if package:
        allowed, message = has_permissions(request.user, 'package_{0}'.format(action), media_type)
    else:
        raise Http404

    return (package, allowed, message)

def get_media_type_and_permissions(media_type_id, action):
    media_type = MediaType.objects.get(id=media_type_id)

    if media_type:
        allowed, message = has_permissions(request.user, 'media_type_{0}'.format(action), media_type)
    else:
        raise Http404

    return (package, allowed, message)


#################
# Generic Views #
#################
def base_request(request):
    context = RequestContext(request)
    context_dict = dict()

    context_dict['base_url'] = '/frontend'

    return context, context_dict

@login_required
def index(request):
    context, context_dict = base_request(request)

    context_dict['user_job_queue']   = Job.objects.filter(user=request.user) \
                                                  .filter(Q(state='PEND') | Q(state='PROG'))

    context_dict['user_job_history'] = Job.objects.filter(user=request.user) \
                                                  .filter(Q(state='COMP') | Q(state='FAIL'))[:5]

    return render_to_response('frontend/index.html', context_dict, context)

def user_login(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(context_dict['base_url'] + '/' )
            else:
                context_dict['disabled_account'] = True
        else:
            context_dict['bad_details'] = True

    return render_to_response('frontend/login.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)
    return redirect('/frontend/')

@login_required
def profile(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/profile.html', context_dict, context)


###############
# Media Types #
###############
@login_required
def media_types(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def media_type_add(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/item_add.html', context_dict, context)

@login_required
def media_type_view(request, media_type_id):
    context, context_dict = base_request(request)

    media_type = MediaType.objects.get(id = media_type_id)

    if not media_type:
        raise Http404

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def media_type_edit(request, media_type_id):
    context, context_dict = base_request(request)

    media_type = MediaType.objects.get(id = media_type_id)

    if not media_type:
        raise Http404

    return render_to_response('frontend/item_edit.html', context_dict, context)

@login_required
def media_type_delete(request, media_type_id):
    context, context_dict = base_request(request)

    media_type = MediaType.objects.get(id = media_type_id)

    if not media_type:
        raise Http404

    return render_to_response('frontend/item_delete.html', context_dict, context)


#####################
# Package Discovery #
#####################
@login_required
def media_discover(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_discover.html', context_dict, context)

@login_required
def media_discover_client(request, client_id):
    context, context_dict = base_request(request)

    client = Client.objects.get(id=client_id)

    if not client:
        raise Http404

    return render_to_response('frontend/media_discover_client.html', context_dict, context)


############
# Packages #
############
@login_required
def packages(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        filterby = request.POST['filterby']
        media_type = MediaType.objects.filter(name=filterby)    
        packages = Package.objects.filter(media_type=media_type)
    else:
        packages = Package.objects.all()

    for package in packages:
        package.url = 'packages/{0}'.format(package.id)

        if has_permissions(request.user, 'package_edit', package.id)[0]:
            package.can_edit = True

        if has_permissions(request.user, 'package_delete', package.id)[0]:
            package.can_delete = True

    context_dict['list'] = packages
    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def package_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = PackageForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/frontend/packages')
    else: 
        form = PackageForm()

    context_dict['form'] = form
    return render_to_response('frontend/item_add.html', context_dict, context)

@login_required
def package_view(request, package_id):
    context, context_dict = base_request(request)

        
    package, allowed, message = get_package_and_permissions(package_id, 'view')
    package = Package.objects.get(id=package_id)

    if package:
        allowed, message = has_permissions(request.user, 'package_view', package)
    else:
        raise Http404

    if allowed:
        return render_to_response('frontend/item_view.html', context_dict, context)
    else:
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def package_edit(request, package_id):
    context, context_dict = base_request(request)

    package = Package.objects.get(id=package_id)

    if package:
        allowed, message = has_permissions(request.user, 'package_edit', package)
    else:
        raise Http404

    if allowed:
        form = PackageForm(instance=package)

        if request.method == 'POST':
            form = PackageForm(request.POST)

            if form.is_valid():
                form.save(commit=True)
                return redirect(base_url + 'packages/')

        context_dict['form'] = form
        return render_to_response('frontend/item_edit.html', context_dict, context)
    else: 
        render_to_response('frontend/access_denied.html', context_dict, context)

def package_delete(request, package_id):
    context, context_dict = base_request(request)

    package = Package.objects.get(id=package_id)

    if package:
        allowed, message = has_permissions(request.user, 'package_delete', package)
    else:
        raise Http404

    if allowed:
        media_package.delete()
        redirect('/frontned/packages')
    else:
        return render_to_response('frontend/access_denied.html', context_dict, context)


##################
# Client Section #
##################
@login_required
def clients(request):
    context, context_dict = base_request(request)

    clients = Client.objects.all()
    for client in clients:
        client.url  = 'clients/{0}/'.format(client.id)
        if has_permissions(request.user, 'edit_client', client.id)[0]:
            client.can_edit = True

    context_dict['list'] = clients
    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def client_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = ClientForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
    else:
        form = ClientForm()

    context_dict['form'] = form
    return render_to_response('frontend/item_add.html', context_dict, context)

@login_required
def client_view(request, client_id):
    context, context_dict = base_request(request)
    
    client = Client.objects.get(id=client_id)

    if client:
        allowed, message = has_permissions(request.user, 'view_client', client_id)
    else:
        raise Http404

    if allowed:
        context_dict['item'] = Client
        return render_to_response('frontend/item_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def client_edit(request, client_id):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = ClientForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
    else:
        # Need to figure out here how to pre-fill a form
        form = ClientForm()

    context_dict['form'] = form
    return render_to_response('frontend/item_edit.html', context_dict, context)

###############
# Job Section #
###############
@login_required
def jobs(request):
    context, context_dict = base_request(request)

    context_dict['list'] = Job.objects.filter(user=request.user) \
                                      .filter(Q(state='PEND') | Q(state='PROG'))

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = JobForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
    else:
        form = JobForm()

    context_dict['form'] = form
    return render_to_response('frontend/item_add.html', context_dict, context)

@login_required
def job_view(request, job_id):
    context, context_dict = base_request(request)

    job  = Job.objects.get(id=job_id)

    if job:
        allowed, message = has_permissions(request.user, 'view_job', job_id)
    else:
        raise Http404

    if allowed:
        context_dict['item'] = Job
        return render_to_response('frontend/item_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def job_history(request):
    context, context_dict = base_request(request)

    jobs = Job.objects.filter(user=request.user) \
                                      .filter(Q(state='COMP') | Q(state='FAIL'))

    for job in jobs:
        job.url = 'jobs/{0}'.format(job.id)

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_history_client(request, client_id):
    context, context_dict = base_request(request)

    client = Client.objects.get(id=client_id)

    if client:
        allowed, message = has_permissions(request.user, 'view_client', client_id)
    else:
        raise Http404

    if allowed:
        context_dict['list'] = Job.objects.filter(Q(destination_client=client) | Q(source_client=client)) \
                                          .filter(Q(state='COMP') | Q(state='FAIL'))
        return render_to_response('frontend/list_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)


