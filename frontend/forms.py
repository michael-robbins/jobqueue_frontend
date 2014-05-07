from django import forms
from frontend.models import Client, MediaType, Package, Job, JOB_ACTIONS, JOB_STATES
import datetime

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client

class MediaTypeForm(forms.ModelForm):
    class Meta:
        model = MediaType

class PackageForm(forms.ModelForm):
    media_type     = forms.ModelChoiceField(MediaType.objects.all())
    parent_package = forms.ModelChoiceField(Package.objects.filter(media_type__name='tv'))

    class Meta:
        model = Package
        fields = ('name', 'relative_path', 'media_type', 'parent_package')

class JobForm(forms.ModelForm):
    source_client      = forms.ModelChoiceField(Client.objects.all())
    destination_client = forms.ModelChoiceField(Client.objects.all())

    class Meta:
        model = Job
        fields = ('action', 'package', 'source_client', 'destination_client')
