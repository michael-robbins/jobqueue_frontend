from django import forms
from frontend.models import Client, MediaType, Package, Job, JOB_ACTIONS, JOB_STATES
import datetime

class ClientForm(forms.ModelForm):
    name          = forms.CharField(max_length=64, help_text='Please enter the Client Name')
    host_username = forms.CharField(max_length=64, help_text='Account Username on the Client machine')
    host_hostname = forms.CharField(max_length=128, help_text='Hostname/IP Address of the Client machine')
    host_port     = forms.IntegerField(initial=22, help_text='SSH Port of the Client machine')
    base_path     = forms.CharField(help_text='Base Path of the Media directory')
    max_download  = forms.IntegerField(initial=0, help_text='Max download in KB/s (0=unlimited)')
    max_upload    = forms.IntegerField(initial=0, help_text='Max upload in KB/s (0=unlimited)')

    class Meta:
        model = Client

class MediaTypeForm(forms.ModelForm):
    name          = forms.CharField(max_length=32, help_text='Name of the Media Type')
    relative_path = forms.CharField(help_text='Realtive to a Client\'s Base Path')

    class Meta:
        model = MediaType

class PackageForm(forms.ModelForm):
    name           = forms.CharField(max_length=128, help_text='Name of the Package')
    relative_path  = forms.CharField(help_text='Relative to a Media Type\'s Path')
    media_type     = forms.ModelChoiceField(MediaType.objects.all(), help_text='Packages Media Type')
    parent_package = forms.ModelChoiceField(Package.objects.filter(media_type__name='tv'), help_text='Usually the Base Season of the TV Series')

    class Meta:
        model = Package
        fields = ('name', 'relative_path', 'media_type', 'parent_package')

class JobForm(forms.ModelForm):
    action  = forms.ChoiceField(choices=JOB_ACTIONS, help_text='Action that we want to perform')
    package = forms.ModelChoiceField(Package.objects.all(), help_text='Package we want to perform our Action on')
    source_client      = forms.ModelChoiceField(Client.objects.all(), help_text='We need this field if the Action is SYNC')
    destination_client = forms.ModelChoiceField(Client.objects.all(), help_text='Client we want to perform our Action on')

    class Meta:
        model = Job
        fields = ('action', 'package', 'source_client', 'destination_client')
