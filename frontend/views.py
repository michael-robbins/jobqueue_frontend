from django.http      import HttpResponse, HttpResponseRedirect
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
def has_permissions(user):
    """
    Think about how I am going to implement permissions
    * Has someone online got a good method?
    * What levels of permissions?
        * Superuser
            * Not Restricted
        * User
            * Has Content Restriction
            * Has Job Queue Restriction
            * Has Media Package Restriction
    """
    return True


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

    user = User.objects.get(username=request.user)

    context_dict['user_job_queue']   = Job.objects.filter(user=user) \
                                                  .filter(Q(state='PEND') | Q(state='PROG'))

    context_dict['user_job_history'] = Job.objects.filter(user=user) \
                                                  .filter(Q(state='COMP') | Q(state='FAIL'))[:5]

    return render_to_response('frontend/index.html', context_dict, context)

@login_required
def about(request):
    context, context_dict = base_request(request)
    
    return render_to_response('frontend/about.html', context_dict, context)

def user_login(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return index(request)
            else:
                context_dict['disabled_account'] = True
        else:
            context_dict['bad_details'] = True

    return render_to_response('frontend/login.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/frontend/')

@login_required
def profile(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/profile.html', context_dict, context)

#################
# Media Section #
#################
@login_required
def media(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def media_types(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_types.html', context_dict, context)

@login_required
def media_type_add(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_type_add.html', context_dict, context)

@login_required
def media_type_view(request, media_type_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_type_view.html', context_dict, context)

@login_required
def media_type_edit(request, media_type_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_type_edit.html', context_dict, context)

@login_required
def media_discover(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_discover.html', context_dict, context)

@login_required
def media_discover_client(request, client_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_discover_client.html', context_dict, context)

@login_required
def media_packages(request):
    context, context_dict = base_request(request)

    if request.method == 'POST':
        filterby = request.POST['filterby']
        # Sanitize user input
        media_type = MediaType.objects.filter(name=filterby)    
        packages = Package.objects.filter(media_type=media_type)
    else:
        packages = Package.objects.all()

    if packages:
        for package in packages:
            package.url  = 'media/packages/' + str(package.id)

    context_dict['list'] = packages

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def media_package_add(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_package_add.html', context_dict, context)

@login_required
def media_package_view(request, package_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_package_view.html', context_dict, context)

@login_required
def media_package_edit(request, package_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/media_package_edit.html', context_dict, context)

##################
# Client Section #
##################
@login_required
def clients(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/clients.html', context_dict, context)

@login_required
def client_add(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/client_add.html', context_dict, context)

@login_required
def client_view(request, client_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/client_view.html', context_dict, context)

@login_required
def client_edit(request, client_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/client_edit.html', context_dict, context)

###############
# Job Section #
###############
@login_required
def jobs(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/jobs.html', context_dict, context)

@login_required
def job_add(request):
    context, context_dict = base_request(request)

    return render_to_response('frontend/job_add.html', context_dict, context)

@login_required
def job_view(request, job_id):
    context, context_dict = base_request(request)

    user = User.objects.get(username=request.user)

    context_dict['user_job_queue'] = Job.objects.filter(user=user) \
                                                .filter(Q(state='PEND') | Q(state='PROG'))

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_history(request):
    context, context_dict = base_request(request)

    user = User.objects.get(username=request.user)

    context_dict['user_job_queue'] = Job.objects.filter(user=user) \
                                                .filter(Q(state='COMP') | Q(state='FAIL'))

    return render_to_response('frontend/list_view.html', context_dict, context)

@login_required
def job_history_client(request, client_id):
    context, context_dict = base_request(request)

    return render_to_response('frontend/job_history_client.html', context_dict, context)

