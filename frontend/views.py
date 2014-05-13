from django.http      import HttpResponse, HttpResponseRedirect, Http404
from django.template  import RequestContext
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from frontend.models import Client,      Category,      Package,      Job,      File, ClientPackageAvailability, ClientFileAvailability
from frontend.forms  import ClientForm,  CategoryForm,  PackageForm,  JobForm
from frontend.tables import ClientTable, CategoryTable, PackageTable, JobTable

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

def get_object(user, context_dict, context, object_name, object_id, object_class, action):
    obj = get_object_or_404(object_class, id=object_id)

    allowed, message = has_permissions(user, action, object_name, obj)

    if not allowed:
        context_dict['message'] = message
        return render_to_response('frontend/access_denied.html', context_dict, context)

    return obj

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
    
    context_dict['table'] = CategoryTable(categories)
    context_dict['list_name'] = 'Categories'

    context_dict['add_name'] = 'Category'
    context_dict['add_url']  = 'categories/add/'

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

    category = get_object(request.user, context_dict, context, 'category', category_id, Category, 'edit')

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            redirect(context_dict['base_url'] + 'categories/')
    else:
        form = CategoryForm(instance=category)

    context_dict['item_name'] = 'Edit Category'
    context_dict['url_post']  = 'categories/{0}/edit/'.format(category.id)
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def category_delete(request, category_id):
    context, context_dict = base_request(request)

    category = get_object(request.user, context_dict, context, 'category', category_id, Category, 'delete')
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

    context_dict['table'] = PackageTable(packages)
    context_dict['list_name'] = 'Packages'

    context_dict['add_name'] = 'Package'
    context_dict['add_url']  = 'packages/add/'

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

    package = get_object(request.user, context_dict, context, 'package', package_id, Package, 'view')

    context_dict['item'] = package

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def package_edit(request, package_id):
    context, context_dict = base_request(request)

    package = get_object(request.user, context_dict, context, 'package', package_id, Package, 'edit')

    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'packages/')
    else:
        form = PackageForm(instance=package)

    context_dict['item_name'] = 'Edit Package'
    context_dict['url_post']  = 'packages/{0}/edit/'.format(package.id)
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

def package_delete(request, package_id):
    context, context_dict = base_request(request)

    package = get_object(request.user, context_dict, context, 'package', package_id, Package, 'delete')
    package.delete()

    return redirect(context_dict['base_url'] + 'packages/')


##################
# Client Section #
##################
@login_required
def clients(request):
    context, context_dict = base_request(request)

    clients = Client.objects.all()

    context_dict['table'] = ClientTable(clients)
    context_dict['list_name'] = 'Clients'

    context_dict['add_name'] = 'Client'
    context_dict['add_url']  = 'clients/add/'

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
def client_edit(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(request.user, context_dict, context, 'client', client_id, Client, 'edit')

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()
            return redirect(context_dict['base_url'] + 'clients/')
    else:
        form = ClientForm(instance=client)

    context_dict['item_name'] = 'Edit Client'
    context_dict['url_post']  = 'clients/{0}/edit/'.format(client.id)
    context_dict['form']      = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def client_delete(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(request.user, context_dict, context, 'client', client_id, Client, 'delete')
    client.delete()

    return redirect(context_dict['base_url'] + 'clients/')

@login_required
def client_discover(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(request.user, context_dict, context, 'client', client_id, Client, 'edit')

    return render_to_response('frontend/client_discover.html', context_dict, context)

@login_required
def client_history(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(request.user, context_dict, context, 'client', client_id, Client, 'view')

    jobs = Job.objects.filter(Q(destination_client=client) | Q(source_client=client)) \
                      .filter(Q(state='COMP') | Q(state='FAIL'))

    context_dict['table'] = JobTable(jobs)
    context_dict['list_name'] = 'Client Job History'

    return render_to_response('frontend/list_view.html', context_dict, context)


###############
# Job Section #
###############
@login_required
def jobs(request):
    context, context_dict = base_request(request)

    jobs = Job.objects.filter(user=request.user) \
                      .filter(Q(state='PEND') | Q(state='PROG'))

    context_dict['table'] = JobTable(jobs)
    context_dict['list_name'] = 'Job Queue'

    context_dict['add_name'] = 'Job'
    context_dict['add_url']  = 'jobs/add/'

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

def job_view(request, job_id):
    context, context_dict = base_request(request)

    job = get_object(request.user, context_dict, context, 'job', job_id, Job, 'view')

    context_dict['item_name'] = 'Job'
    context_dict['item'] = job

    return render_to_response('frontend/item_view.html', context_dict, context)

def job_delete(request, job_id):
    context, context_dict = base_request(request)

    job = get_object(request.user, context_dict, context, 'job', job_id, Job, 'delete')
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

    context_dict['list_name'] = 'Your Job History'
    context_dict['list']      = jobs

    return render_to_response('frontend/list_view.html', context_dict, context)

