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
def has_permissions(user, action, object_name, object_instance):
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
    * What about permissions that don't involve objects... ?
    """

    allowed = (True, 'Allowed.')
    denied_not_super   = (False, 'You are not a Super User.')
    denied_not_allowed = (False, 'You are missing the required privileges.')

    return allowed
    
def get_package(user, object_id, action):
    package = Package.objects.get(id=object_id)

    if package:
        allowed, message = has_permissions(user, action, 'package', package)
    else:
        raise Http404

    return (package, allowed, message)

def get_media_type(user, object_id, action):
    media_type = MediaType.objects.get(id=object_id)

    if media_type:
        allowed, message = has_permissions(user, action, 'media_type', media_type)
    else:
        raise Http404

    return (media_type, allowed, message)

def get_client(user, object_id, action):
    client = Client.objects.get(id=object_id)

    if client:
        allowed, message = has_permissions(user, action, 'client', client)
    else:
        raise Http404

    return (client, allowed, message)

def get_job(user, object_id, action):
    job = Job.objects.get(id=object_id)

    if job:
        allowed, message = has_permissions(user, action, 'job', job)
    else:
        raise Http404

    return (job, allowed, message)


#################
# Generic Views #
#################
def base_request(request):
    context = RequestContext(request)
    context_dict = dict()

    context_dict['base_url'] = '/frontend'

    # TODO: Cache this shit...
    media_types = MediaType.objects.all()

    for media_type in media_types:
        media_type.url = 'packages/?filter={0}'.format(media_type.name)

    context_dict['media_types'] = media_types

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

    media_types = MediaType.objects.all()

    for media_type in media_types:
        media_type.url  = 'media_types/{0}'.format(media_type.name)

    context_dict['list_name'] = 'Media Types'
    context_dict['list'] = media_types
    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def media_type_add(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/item_add.html', context_dict, context)

@login_required
def media_type_view(request, media_type_id):
    context, context_dict = base_request(request)

    media_type, allowed, message = get_media_type(request.user, media_type_id, 'view')

    context_dict['item'] = media_type
    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def media_type_edit(request, media_type_id):
    context, context_dict = base_request(request)

    media_type, allowed, message = get_media_type(request.user, media_type_id, 'edit')

    return render_to_response('frontend/item_edit.html', context_dict, context)

@login_required
def media_type_delete(request, media_type_id):
    context, context_dict = base_request(request)

    media_type, allowed, message = get_media_type(request.user, media_type_id, 'delete')

    if allowed:
        media_type.delete()
        redirect('/frontend/media_types')
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)


############
# Packages #
############
@login_required
def packages(request):
    context, context_dict = base_request(request)

    if request.method == 'GET' and 'filter' in request.GET:
        filterby = request.GET['filter']
        
        media_type = MediaType.objects.filter(name=filterby)

        if media_type:
            packages = Package.objects.filter(media_type=media_type)
        else:
            packages = Package.objects.all()
    else:
        packages = Package.objects.all()

    for package in packages:
        package.url = 'packages/{0}'.format(package.id)

        if has_permissions(request.user, 'edit',   'package', package)[0]:
            package.can_edit = True

        if has_permissions(request.user, 'delete', 'package', package)[0]:
            package.can_delete = True

    context_dict['list_name'] = 'Media Packages'
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

    package, allowed, message = get_package(request.user, package_id, 'view')

    if allowed:
        context_dict['item'] = package
        return render_to_response('frontend/item_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def package_edit(request, package_id):
    context, context_dict = base_request(request)

    package, allowed, message = get_package(request.user, package_id, 'edit')

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
        context_dict['message'] = message
        render_to_response('frontend/access_denied.html', context_dict, context)

def package_delete(request, package_id):
    context, context_dict = base_request(request)

    package, allowed, message = get_package(request.user, package_id, 'delete')

    if allowed:
        media_package.delete()
        redirect('/frontned/packages')
    else:
        context_dict['message'] = message
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
        # TODO: Client edit permissions (can_edit)
        # TODO: Client delete permissions (can_delete)

    context_dict['list_name'] = 'Clients'
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
    
    client, allowed, message = get_client(request.user, client_id, 'view')

    if allowed:
        context_dict['item'] = client
        return render_to_response('frontend/item_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def client_edit(request, client_id):
    context, context_dict = base_request(request)

    client, allowed, message = get_client(request.user, client_id, 'edit')

    if not allowed:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

    if request.method == 'POST':
        form = ClientForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
    else:
        form = ClientForm(instance=client)

    context_dict['form'] = form
    return render_to_response('frontend/item_edit.html', context_dict, context)

@login_required
def client_delete(request, client_id):
    context, context_dict = base_request(request)

    client, allowed, message = get_client(request.user, client_id, 'edit')

    if allowed:
        client.delete()
        redirect('/frontend/clients/')
        return render_to_response('frontend/item_delete.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def client_discovery(request, client_id):
    context, context_dict = base_request(request)

    client, allowed, message = get_client(request.user, client_id, 'edit')

    return render_to_response('frontend/client_discovery.html', context_dict, context)


###############
# Job Section #
###############
@login_required
def jobs(request):
    context, context_dict = base_request(request)

    jobs = Job.objects.filter(user=request.user) \
                      .filter(Q(state='PEND') | Q(state='PROG'))

    for job in jobs:
        job.name = str(job)
        job.url = 'jobs/{0}'.format(job.id)
        job.can_edit = False
        # TODO: Add in can_delete with permissions

    context_dict['list_name'] = 'Your Job Queue'
    context_dict['list'] = jobs
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

    job, allowed, message = get_job(request.user, job_id, 'view')

    if allowed:
        context_dict['item'] = Job
        return render_to_response('frontend/item_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

@login_required
def job_delete(request, job_id):
    context, context_dict = base_request(request)

    job, allowed, message = get_job(request.user, job_id, 'delete')

    if allowed:
        return render_to_response('frontend/item_delete.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

###############
# Job History #
###############
@login_required
def job_history(request):
    context, context_dict = base_request(request)

    jobs = Job.objects.filter(user=request.user) \
                                      .filter(Q(state='COMP') | Q(state='FAIL'))

    for job in jobs:
        job.url = 'jobs/{0}'.format(job.id)
        job.can_edit   = False
        job.can_delete = False

    context_dict['list'] = jobs
    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_history_client(request, client_id):
    context, context_dict = base_request(request)

    client, allowed, message = get_client(request.user, client_id, 'view')

    if allowed:
        jobs = Job.objects.filter(Q(destination_client=client) | Q(source_client=client)) \
                                          .filter(Q(state='COMP') | Q(state='FAIL'))

        for job in jobs:
            job.url = 'jobs/{0}'.format(job.id)
            job.can_edit   = False
            job.can_delete = False

        context_dict['list'] = jobs
        return render_to_response('frontend/list_view.html', context_dict, context)
    else:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)
