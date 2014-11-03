# Bare minimum Django objects required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.shortcuts import get_object_or_404, get_list_or_404

# Django auth model and functions
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required

# Allows SQL-esque OR & AND statements in model filters
from django.db.models import Q

# Reverse URL Discover
from django.core.urlresolvers import reverse

# Rest Framework
from rest_framework import viewsets

## Models
# Client
from frontend.models import Client
from frontend.forms import ClientForm
from frontend.tables import ClientTable
from frontend.serializers import ClientSerializer

# Category
from frontend.models import Category
from frontend.forms import CategoryForm
from frontend.tables import CategoryTable
from frontend.serializers import CategorySerializer

# Package
from frontend.models import Package
from frontend.forms import PackageForm
from frontend.tables import PackageTable
from frontend.serializers import PackageSerializer

# File
from frontend.models import File
from frontend.serializers import FileSerializer

# ClientPackageAvailability
from frontend.models import ClientPackageAvailability
from frontend.serializers import ClientPackageAvailabilitySerializer

# ClientFileAvailability
from frontend.models import ClientFileAvailability
from frontend.tables import ClientFileAvailabilityTable
from frontend.serializers import ClientFileAvailabilitySerializer

# Job
from frontend.models import Job
from frontend.forms import JobForm
from frontend.tables import JobTable
from frontend.serializers import JobSerializer


#################
# Generic Views #
#################
def base_request(request):
    context = RequestContext(request)
    context_dict = dict()

    context_dict['base_url'] = '/frontend/'

    # TODO: Cache this shit...
    temp_categories = Category.objects.all()

    for category in temp_categories:
        category.url = 'packages/?category={0}'.format(category.name)

    context_dict['categories'] = temp_categories

    return context, context_dict


@login_required
def index(request):
    context, context_dict = base_request(request)

    context_dict['user_job_queue'] = Job.objects.filter(user=request.user) \
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

    # Keep the next hop in-case they fail to login
    next_hop = request.GET.get('next', None)

    if next_hop:
        context_dict['next_url'] = '?next={0}'.format(next_hop)

    return render_to_response('frontend/login.html', context_dict, context)


@login_required
def user_logout(request):
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

    temp_categories = Category.objects.all()

    if request.method == 'GET':
        sort = request.GET.get('sort', 'display_name')
        if sort.lstrip('-') in [field.name for field in Category._meta.fields]:
            temp_categories = temp_categories.order_by(sort)

    context_dict['table_name'] = 'Categories'
    context_dict['table'] = CategoryTable(temp_categories)

    context_dict['add_name'] = 'Category'
    context_dict['add_url'] = 'categories/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)


@login_required
@permission_required('frontend.add_category', raise_exception=True)
def category_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST, form_title='Add New Category')

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
        form = CategoryForm(instance=category, form_title='Edit Category')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)


@login_required
@permission_required('frontend.delete_category', raise_exception=True)
def category_delete(request, category_name):
    _, _ = base_request(request)

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
            temp_packages = Package.objects.filter(category=category)
        else:
            temp_packages = Package.objects.all()
    else:
        temp_packages = Package.objects.all()
    
    if request.method == 'GET':
        sort = request.GET.get('sort', 'name')
        if sort.lstrip('-') in [field.name for field in Package._meta.fields]:
            temp_packages = temp_packages.order_by(sort)

    context_dict['table_name'] = 'Packages'
    context_dict['table'] = PackageTable(temp_packages)

    context_dict['add_name'] = 'Package'
    context_dict['add_url'] = 'packages/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)


@login_required
@permission_required('frontend.add_package', raise_exception=True)
def package_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = PackageForm(request.POST, form_title='Add New Package')

        if form.is_valid():
            form.save()
            return redirect(reverse('packages'))
    else: 
        form = PackageForm(form_title='Add New Package')

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
        form = PackageForm(request.POST, instance=package, form_title='Edit Package')

        if form.is_valid():
            form.save()
            return redirect(reverse('packages'))
    else:
        form = PackageForm(instance=package, form_title='Edit Package')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)


@login_required
@permission_required('frontend.delete_package', raise_exception=True)
def package_delete(request, package_id):
    _, _ = base_request(request)

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

    temp_clients = Client.objects.all()

    if request.method == 'GET':
        sort = request.GET.get('sort', 'name')
        if sort.lstrip('-') in [field.name for field in Client._meta.fields]:
            temp_clients = temp_clients.order_by(sort)

    context_dict['table_name'] = 'Clients'
    context_dict['table'] = ClientTable(temp_clients)

    context_dict['add_name'] = 'Client'
    context_dict['add_url'] = 'clients/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)


@login_required
@permission_required('frontend.add_client', raise_exception=True)
def client_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = ClientForm(request.POST, form_title='Add New Client')

        if form.is_valid():
            form.save()
            return redirect(reverse('clients'))
    else:
        form = ClientForm(form_title='Add New Client')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)


@login_required
@permission_required('frontend.change_client', raise_exception=True)
def client_change(request, client_id):
    context, context_dict = base_request(request)

    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        print('POST detected')
        form = ClientForm(request.POST, instance=client, form_title='Edit Client')

        print(dir(form))
        print(form.non_field_errors)
        print(form.errors)
        print(form)

        if form.is_valid():
            print('Client change detected')
            form.save()
            return redirect(reverse('clients'))
    else:
        form = ClientForm(instance=client, form_title='Edit Client')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)


@login_required
@permission_required('frontend.delete_client', raise_exception=True)
def client_delete(request, client_id):
    _, _ = base_request(request)

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

    temp_jobs = Job.objects.filter(Q(destination_client=client) |
                                   Q(source_client=client)).filter(Q(state='COMP') | Q(state='FAIL'))

    context_dict['table_name'] = 'Client Job History'
    context_dict['table'] = JobTable(temp_jobs)

    return render_to_response('frontend/list_view.html', context_dict, context)


###############
# Job Section #
###############
@login_required
@permission_required('frontend.view_job', raise_exception=True)
def jobs(request):
    context, context_dict = base_request(request)

    temp_jobs = Job.objects.filter(user=request.user) \
                           .filter(Q(state='PEND') | Q(state='PROG'))

    if request.method == 'GET':
        sort = request.GET.get('sort', 'package')
        if sort.lstrip('-') in [field.name for field in Job._meta.fields]:
            temp_jobs = temp_jobs.order_by(sort)

    context_dict['table_name'] = 'Job Queue'
    context_dict['table'] = JobTable(temp_jobs)

    context_dict['add_name'] = 'Job'
    context_dict['add_url'] = 'jobs/add/'

    return render_to_response('frontend/list_view.html', context_dict, context)


@login_required
@permission_required('frontend.add_job', raise_exception=True)
def job_add(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        form = JobForm(request.POST, form_title='Add New Job')

        if form.is_valid():
            form.save()
            return redirect(reverse('jobs'))
    else:
        form = JobForm(form_title='Add New Job')

    context_dict['form'] = form

    return render_to_response('frontend/item_add_change.html', context_dict, context)


@login_required
@permission_required('frontend.view_job', raise_exception=True)
def job_view(request, job_id):
    context, context_dict = base_request(request)

    job = get_list_or_404(Job, id=job_id)

    files = ClientFileAvailability.objects.filter(client=job[0].destination_client) \
                                          .filter(package_file__package=job[0].package)

    if request.method == 'GET':
        sort = request.GET.get('sort', 'package_file')
        if sort.lstrip('-') in [field.name for field in ClientFileAvailability._meta.fields]:
            files = files.order_by(sort)

    context_dict['job'] = JobTable(job)
    context_dict['files'] = ClientFileAvailabilityTable(files)

    return render_to_response('frontend/job_view.html', context_dict, context)


@login_required
@permission_required('frontend.delete_job', raise_exception=True)
def job_delete(request, job_id):
    _, _ = base_request(request)

    job = get_object_or_404(Job, id=job_id)
    job.delete()

    return redirect(reverse('jobs'))


@login_required
@permission_required('frontend.view_job', raise_exception=True)
def job_history(request):
    context, context_dict = base_request(request)

    temp_jobs = Job.objects.filter(user=request.user) \
                      .filter(Q(state='COMP') | Q(state='FAIL'))
    
    if request.method == 'GET':
        sort = request.GET.get('sort', 'package')
        if sort.lstrip('-') in [field.name for field in Job._meta.fields]:
            temp_jobs = temp_jobs.order_by(sort)

    for job in temp_jobs:
        job.url = 'jobs/{0}'.format(job.id)

    context_dict['table_name'] = 'Your Job History'
    context_dict['table'] = JobTable(temp_jobs)

    return render_to_response('frontend/list_view.html', context_dict, context)


#######
# API #
#######
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_fields = ('package',)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class ClientPackageAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = ClientPackageAvailability.objects.all()
    serializer_class = ClientPackageAvailabilitySerializer
    filter_fields = ('client', 'package')


class ClientFileAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = ClientFileAvailability.objects.all()
    serializer_class = ClientFileAvailabilitySerializer
    filter_fields = ('client', 'package_file')
