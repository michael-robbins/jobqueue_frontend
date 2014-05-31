# Bare minimum Django obejcts required
from django.http      import Http404
from django.template  import RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.shortcuts import get_object_or_404, get_list_or_404

# Django auth model and functions
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required

# Allows SQL-esque OR & AND statements in model filters
from django.db.models import Q

# Reverse URL Discover
from django.core.urlresolvers import reverse

# Client
from frontend.models import Client
from frontend.forms  import ClientForm
from frontend.tables import ClientTable

# Category
from frontend.models import Category
from frontend.forms  import CategoryForm
from frontend.tables import CategoryTable

# Package
from frontend.models import Package
from frontend.forms  import PackageForm
from frontend.tables import PackageTable

# File
from frontend.models import File

# ClientPackageAvailability
from frontend.models import ClientPackageAvailability

# ClientFileAvailability
from frontend.models import ClientFileAvailability

# Job
from frontend.models import Job
from frontend.forms  import JobForm
from frontend.tables import JobTable


####################
# Helper Functions #
####################


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
        category.url = 'packages/?category={0}'.format(category.name)

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
                return redirect(request.GET.get('next', reverse('index')))
            else:
                context_dict['disabled_account'] = True
        else:
            context_dict['bad_details'] = True

    # Keep the next hop incase they fail to login
    next_hop = request.GET.get('next', None)

    if next_hop:
        context_dict['next_url'] = '?next={0}'.format(next_hop)

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
@permission_required('frontend.view_category', raise_exception=True)
def categories(request):
    context, context_dict = base_request(request)

    categories = Category.objects.all()

    if request.method == 'GET':
        sort = request.GET.get('sort', 'display_name')
        if sort.lstrip('-') in [ field.name for field in Category._meta.fields ]:
            categories = categories.order_by(sort)

    context_dict['table'] = CategoryTable(categories)
    context_dict['list_name'] = 'Categories'

    context_dict['add_name'] = 'Category'
    context_dict['add_url']  = 'categories/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
@permission_required('frontend.add_category', raise_exception=True)
def category_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST, form_title = 'Add New Category')

        if form.is_valid():
            form.save()
            return redirect(reverse('categories'))
    else:
        form = CategoryForm(form_title='Add New Category')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.change_category', raise_exception=True)
def category_change(request, category_name):
    context, context_dict = base_request(request)

    category = get_object_or_404(Category, name=category_name)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, form_title='Edit Category')

        if form.is_valid():
            form.save()
            return redirect(reverse('categories'))
    else:
        form = CategoryForm(
                    instance=category, form_title='Edit Category')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.delete_category', raise_exception=True)
def category_delete(request, category_name):
    context, context_dict = base_request(request)

    category = get_object_or_404(Category, name=category_name)
    category.delete()

    return redirect(reverse('categories'))


############
# Packages #
############
@login_required
@permission_required('frontend.view_package', raise_exception=True)
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
    
    if request.method == 'GET':
        sort = request.GET.get('sort', 'name')
        if sort.lstrip('-') in [ field.name for field in Package._meta.fields ]:
            packages = packages.order_by(sort)

    context_dict['table'] = PackageTable(packages)
    context_dict['list_name'] = 'Packages'

    context_dict['add_name'] = 'Package'
    context_dict['add_url']  = 'packages/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
@permission_required('frontend.add_package', raise_exception=True)
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

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.view_package', raise_exception=True)
def package_view(request, package_id):
    context, context_dict = base_request(request)

    package = get_object_or_404(Package, id=package_id)
    context_dict['item'] = package

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
@permission_required('frontend.change_package', raise_exception=True)
def package_change(request, package_id):
    context, context_dict = base_request(request)

    package = get_object_or_404(Package, id=package_id)

    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)

        if form.is_valid():
            form.save()
            return redirect(reverse('packages'))
    else:
        form = PackageForm(instance=package)

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.delete_package', raise_exception=True)
def package_delete(request, package_id):
    context, context_dict = base_request(request)

    package = get_object_or_404(Package, id=package_id)
    package.delete()

    return redirect(reverse('packages'))


##################
# Client Section #
##################
@login_required
@permission_required('frontend.view_client', raise_exception=True)
def clients(request):
    context, context_dict = base_request(request)

    clients = Client.objects.all()

    if request.method == 'GET':
        sort = request.GET.get('sort', 'name')
        if sort.lstrip('-') in [ field.name for field in Client._meta.fields ]:
            clients = clients.order_by(sort)

    context_dict['table'] = ClientTable(clients)
    context_dict['list_name'] = 'Clients'

    context_dict['add_name'] = 'Client'
    context_dict['add_url']  = 'clients/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
@permission_required('frontend.add_client', raise_exception=True)
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

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.change_client', raise_exception=True)
def client_change(request, client_id):
    context, context_dict = base_request(request)

    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()
            return redirect(reverse('clients'))
    else:
        form = ClientForm(instance=client)

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.delete_client', raise_exception=True)
def client_delete(request, client_id):
    context, context_dict = base_request(request)

    client = get_object_or_404(Client, id=client_id)
    client.delete()

    return redirect(reverse('clients'))

@login_required
@permission_required('frontend.discover_client', raise_exception=True)
def client_discover(request, client_id):
    context, context_dict = base_request(request)

    client = get_object_or_404(Client, id=client_id)

    return render_to_response('frontend/client_discover.html', context_dict, context)

@login_required
@permission_required('frontend.view_client', raise_exception=True)
def client_history(request, client_id):
    context, context_dict = base_request(request)

    client = get_object_or_404(Client, id=client_id)

    jobs = Job.objects.filter(Q(destination_client=client) | Q(source_client=client)) \
                      .filter(Q(state='COMP') | Q(state='FAIL'))

    context_dict['table'] = JobTable(jobs)
    context_dict['list_name'] = 'Client Job History'

    return render_to_response('frontend/list_view.html', context_dict, context)


###############
# Job Section #
###############
@login_required
@permission_required('frontend.view_job', raise_exception=True)
def jobs(request):
    context, context_dict = base_request(request)

    jobs = Job.objects.filter(user=request.user) \
                      .filter(Q(state='PEND') | Q(state='PROG'))

    if request.method == 'GET':
        sort = request.GET.get('sort', 'package')
        if sort.lstrip('-') in [ field.name for field in Job._meta.fields ]:
            jobs = jobs.order_by(sort)

    context_dict['table'] = JobTable(jobs)
    context_dict['list_name'] = 'Job Queue'

    context_dict['add_name'] = 'Job'
    context_dict['add_url']  = 'jobs/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
@permission_required('frontend.add_job', raise_exception=True)
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

    return render_to_response('frontend/item_add_change.html', context_dict, context)

@login_required
@permission_required('frontend.view_job', raise_exception=True)
def job_view(request, job_id):
    context, context_dict = base_request(request)

    job = get_object_or_404(Job, id=job_id)

    context_dict['item_name'] = 'Job'
    context_dict['item'] = job

    return render_to_response('frontend/item_view.html', context_dict, context)

@login_required
@permission_required('frontend.delete_job', raise_exception=True)
def job_delete(request, job_id):
    context, context_dict = base_request(request)

    job = get_object_or_404(Job, id=job_id)
    job.delete()

    return redirect(reverse('jobs'))

@login_required
@permission_required('frontend.view_job', raise_exception=True)
def job_history(request):
    context, context_dict = base_request(request)

    jobs = Job.objects.filter(user=request.user) \
                      .filter(Q(state='COMP') | Q(state='FAIL'))
    
    if request.method == 'GET':
        sort = request.GET.get('sort', 'package')
        if sort.lstrip('-') in [ field.name for field in Job._meta.fields ]:
            jobs = jobs.order_by(sort)

    for job in jobs:
        job.url = 'jobs/{0}'.format(job.id)

    context_dict['list_name'] = 'Your Job History'
    context_dict['list']      = jobs

    return render_to_response('frontend/list_view.html', context_dict, context)

