from django.http      import HttpResponse, HttpResponseRedirect, Http404
from django.template  import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from frontend.models import Client, Category, Job, Package, File, ClientPackageAvailability

from frontend.forms import ClientForm, CategoryForm, PackageForm, JobForm

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

# TODO: Figure out how to turn all below into a single function
def get_package(user, context_dict, context, object_id, action):
    package = get_object_or_404(Package, id=object_id)

    allowed, message = has_permissions(user, action, 'package', package)

    if not allowed:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

    return package

def get_category(user, context_dict, context, object_id, action):
    category = get_object_or_404(Category, id=object_id)

    allowed, message = has_permissions(user, action, 'category', category)

    if not allowed:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

    return category

def get_client(user, context_dict, context, object_id, action):
    client = get_object_or_404(Client, id=object_id)

    allowed, message = has_permissions(user, action, 'client', client)

    if not allowed:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

    return client

def get_job(user, context_dict, context, object_id, action):
    job = get_object_or_404(Job, id=object_id)

    allowed, message = has_permissions(user, action, 'job', job)

    if not allowed:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

    return job


#################
# Generic Views #
#################
def base_request(request):
    context = RequestContext(request)
    context_dict = dict()

    context_dict['base_url'] = '/frontend/'

    # TODO: Cache this shit...
    categories = Category.objects.all()

    for category in categories:
        category.url = 'packages/?filter={0}'.format(category.name)

    context_dict['categories'] = categories

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
                return redirect(context_dict['base_url'])
            else:
                context_dict['disabled_account'] = True
        else:
            context_dict['bad_details'] = True

    return render_to_response('frontend/login.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)

    return redirect(context_dict['base_url'])

@login_required
def profile(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/profile.html', context_dict, context)


##############
# Categories #
##############
@login_required
def categories(request):
    context, context_dict = base_request(request)

    categories = Category.objects.all()

    for category in categories:
        category.url = 'packages/?filter={0}'.format(category.name)
        
        if has_permissions(request.user, 'edit',   'category', category)[0]:
            category.url_edit   = "categories/{0}/edit/".format(category.id)

        if has_permissions(request.user, 'delete', 'category', category)[0]:
            category.url_delete = "categories/{0}/delete/".format(category.id)

    context_dict['list_name'] = 'Categories'
    context_dict['list'] = categories

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def category_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = CategoryFrom(request.POST)

        if form.is_valid():
            form.save()
            redirect(context_dict['base_url'] + 'categories/')
    else:
        form = CategoryForm()

    context_dict['item_name'] = 'Add New Category'
    context_dict['url_post']  = 'categories/add/'
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def category_edit(request, category_id):
    context, context_dict = base_request(request)

    category = get_category(request.user, context_dict, context, category_id, 'edit')

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            redirect(context_dict['base_url'] + 'categories/{0}/'.format(category.id))
    else:
        form = CategoryForm(instance=category)

    context_dict['item_name'] = 'Edit Category'
    context_dict['url_post']  = 'categories/{0}/edit/'.format(category.id)
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def category_delete(request, category_id):
    context, context_dict = base_request(request)

    category = get_category(request.user, context_dict, context, category_id, 'delete')
    category.delete()

    return redirect(context_dict['base_url'] + 'categories/')


############
# Packages #
############
@login_required
def packages(request):
    context, context_dict = base_request(request)

    if request.method == 'GET' and 'filter' in request.GET:
        filterby = request.GET['filter']
        
        category = Category.objects.filter(name=filterby)

        if category:
            packages = Package.objects.filter(category=category)
        else:
            packages = Package.objects.all()
    else:
        packages = Package.objects.all()

    for package in packages:
        package.url = 'packages/{0}/'.format(package.id)

        if has_permissions(request.user, 'edit',   'package', package)[0]:
            package.url_edit   = "{0}edit/".format(package.url)

        if has_permissions(request.user, 'delete', 'package', package)[0]:
            package.url_delete = "{0}delete/".format(package.url)

    context_dict['list_name'] = 'Media Packages'
    context_dict['list'] = packages

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def package_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = PackageForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'packages/')
    else: 
        form = PackageForm()

    context_dict['item_name'] = 'Add New Package'
    context_dict['url_post']  = 'packages/add/'
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def package_view(request, package_id):
    context, context_dict = base_request(request)

    package = get_package(request.user, context_dict, context, package_id, 'view')

    context_dict['item'] = package

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def package_edit(request, package_id):
    context, context_dict = base_request(request)

    package = get_package(request.user, context_dict, context, package_id, 'edit')

    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'packages/{0}/'.format(package.id))
    else:
        form = PackageForm(instance=package)

    context_dict['item_name'] = 'Edit Package'
    context_dict['url_post']  = 'packages/{0}/edit/'.format(package.id)
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

def package_delete(request, package_id):
    context, context_dict = base_request(request)

    package = get_package(request.user, context_dict, context, package_id, 'delete')
    package.delete()

    return redirect(context_dict['base_url'] + 'packages/')


##################
# Client Section #
##################
@login_required
def clients(request):
    context, context_dict = base_request(request)

    clients = Client.objects.all()

    for client in clients:
        client.url  = 'clients/{0}/'.format(client.id)

        if has_permissions(request.user, 'edit',   'client', client)[0]:
            client.url_edit     = "{0}edit/".format(client.url)
            client.url_discover = "{0}discover/".format(client.url)

        if has_permissions(request.user, 'delete', 'client', client)[0]:
            client.url_delete = "{0}delete/".format(client.url)

    context_dict['list_name'] = 'Clients'
    context_dict['list'] = clients

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def client_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = ClientForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'clients/')
    else:
        form = ClientForm()

    context_dict['item_name'] = 'Add New Client'
    context_dict['url_post']  = 'clients/add/'
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def client_view(request, client_id):
    context, context_dict = base_request(request)
    
    client = get_client(request.user, context_dict, context, client_id, 'view')

    context_dict['item_name'] = 'Client'
    context_dict['item']      = client

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def client_edit(request, client_id):
    context, context_dict = base_request(request)

    client = get_client(request.user, context_dict, context, client_id, 'edit')

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'clients/{0}/'.format(client.id))
    else:
        form = ClientForm(instance=client)

    context_dict['item_name'] = 'Edit Client'
    context_dict['url_post']  = 'clients/{0}/edit/'.format(client.id)
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def client_delete(request, client_id):
    context, context_dict = base_request(request)

    client = get_client(request.user, context_dict, context, client_id, 'delete')
    client.delete()

    return redirect(context_dict['base_url'] + 'clients/')

@login_required
def client_discovery(request, client_id):
    context, context_dict = base_request(request)

    client = get_client(request.user, context_dict, context, client_id, 'edit')

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

        if has_permissions(request.user, 'delete', 'job', job)[0]:
            job.url_delete = "{0}/delete/".format(job.url)

    context_dict['list_name'] = 'Your Job Queue'
    context_dict['list'] = jobs

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = JobForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'jobs/')
    else:
        form = JobForm()

    context_dict['item_name'] = 'Add New Job'
    context_dict['url_post']  = 'jobs/add/'
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def job_view(request, job_id):
    context, context_dict = base_request(request)

    job = get_job(request.user, context_dict, context, job_id, 'view')

    context_dict['item_name'] = 'Job'
    context_dict['item'] = job

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def job_delete(request, job_id):
    context, context_dict = base_request(request)

    job = get_job(request.user, context_dict, context, job_id, 'delete')
    job.delete()

    return redirect(context_dict['base_url'] + 'jobs/')

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

    context_dict['list_name'] = 'Your Job History'
    context_dict['list']      = jobs

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_history_client(request, client_id):
    context, context_dict = base_request(request)

    client = get_client(request.user, context_dict, context, client_id, 'view')

    jobs = Job.objects.filter(Q(destination_client=client) | Q(source_client=client)) \
                      .filter(Q(state='COMP') | Q(state='FAIL'))

    for job in jobs:
        job.url = 'jobs/{0}'.format(job.id)
        job.can_edit   = False
        job.can_delete = False

    context_dict['list_name'] = 'Client Job History'
    context_dict['list']      = jobs

    return render_to_response('frontend/list_view.html', context_dict, context)
