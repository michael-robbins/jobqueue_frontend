from django.http      import HttpResponse, HttpResponseRedirect, Http404
from django.template  import RequestContext
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.core.urlresolvers import reverse

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

def get_object(user, context_dict, context, object_name, object_class, action, attr_id=None, attr_name=None):
    if attr_id:
        obj = get_object_or_404(object_class, id=attr_id)
    elif attr_name:
        obj = get_object_or_404(object_class, name=attr_name)

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
                return redirect(reverse('index'))
            else:
                context_dict['disabled_account'] = True
        else:
            context_dict['bad_details'] = True

    return render_to_response('frontend/login.html', context_dict, context)

@login_required
def user_logout(request):
    context, context_dict = base_request(request)
    logout(request)

    return redirect(reverse('index'))

@login_required
def user_profile(request):
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
        form = CategoryForm(
                    request.POST
                    , form_action = ''
                    , form_title = 'Add New Category')

        if form.is_valid():
            form.save()
            return redirect(reverse('categories'))
    else:
        form = CategoryForm(form_action='', form_title='Add New Category')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def category_edit(request, category_name):
    context, context_dict = base_request(request)

    category = get_object(
                    request.user
                    , context_dict
                    , context
                    , 'category'
                    , Category
                    , 'edit'
                    , attr_name=category_name)

    if request.method == 'POST':
        form = CategoryForm(
                    request.POST
                    , instance=category
                    , form_action=''
                    , form_title='Edit Category')

        if form.is_valid():
            form.save()
            return redirect(reverse('categories'))
    else:
        form = CategoryForm(
                    instance=category
                    , form_action=''
                    , form_title='Edit Category')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def category_delete(request, category_name):
    context, context_dict = base_request(request)

    category = get_object(
                    request.user
                    , context_dict
                    , context
                    , 'category'
                    , Category
                    , 'delete'
                    , attr_name=category_name)
    category.delete()

    return redirect(reverse('categories'))


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
            return redirect(reverse('packages'))
    else: 
        form = PackageForm()

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def package_view(request, package_id):
    context, context_dict = base_request(request)

    package = get_object(
                request.user
                , context_dict
                , context
                , 'package'
                , Package
                , 'view'
                , attr_id=package_id)

    context_dict['item'] = package

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
def package_edit(request, package_id):
    context, context_dict = base_request(request)

    package = get_object(
                request.user
                , context_dict
                , context
                , 'package'
                , Package
                , 'edit'
                , attr_id=package_id)

    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)

        if form.is_valid():
            form.save()
            return redirect(reverse('packages'))
    else:
        form = PackageForm(instance=package)

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

def package_delete(request, package_id):
    context, context_dict = base_request(request)

    package = get_object(
                request.user
                , context_dict
                , context
                , 'package'
                , Package
                , 'delete'
                , attr_id=package_id)
    package.delete()

    return redirect(reverse('packages'))


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
            return redirect(reverse('clients'))
    else:
        form = ClientForm()

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def client_edit(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(
                request.user
                , context_dict
                , context
                , 'client'
                , Client
                , 'edit'
                , attr_id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()
            return redirect(reverse('clients'))
    else:
        form = ClientForm(instance=client)

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

@login_required
def client_delete(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(
                request.user
                , context_dict
                , context
                , 'client'
                , Client
                , 'delete'
                , attr_id=client_id)
    client.delete()

    return redirect(reverse('clients'))

@login_required
def client_discover(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(
                request.user
                , context_dict
                , context
                , 'client'
                , Client
                , 'edit'
                , attr_id=client_id)

    return render_to_response('frontend/client_discover.html', context_dict, context)

@login_required
def client_history(request, client_id):
    context, context_dict = base_request(request)

    client = get_object(
                request.user
                , context_dict
                , context
                , 'client'
                , Client
                , 'view'
                , attr_id=client_id)

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
            return redirect(reverse('jobs'))
    else:
        form = JobForm()

    context_dict['form'] = form

    return render_to_response('frontend/item_add_edit.html', context_dict, context)

def job_view(request, job_id):
    context, context_dict = base_request(request)

    job = get_object(
            request.user
            , context_dict
            , context
            , 'job'
            , Job
            , 'view'
            , attr_id=job_id)

    context_dict['item_name'] = 'Job'
    context_dict['item'] = job

    return render_to_response('frontend/item_view.html', context_dict, context)

def job_delete(request, job_id):
    context, context_dict = base_request(request)

    job = get_object(
            request.user
            , context_dict
            , context
            , 'job'
            , Job
            , 'delete'
            , attr_id=job_id)
    job.delete()

    return redirect(reverse('jobs'))

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

