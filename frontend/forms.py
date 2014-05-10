from django import forms
from frontend.models import Client, Category, Package, Job, JOB_ACTIONS, JOB_STATES
import datetime

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category

class PackageForm(forms.ModelForm):
    category       = forms.ModelChoiceField(Category.objects.all())
    parent_package = forms.ModelChoiceField(Package.objects.filter(category__name='tv'))

    class Meta:
        model = Package
        fields = ('name', 'relative_path', 'category', 'parent_package')

class JobForm(forms.ModelForm):
    source_client      = forms.ModelChoiceField(Client.objects.all())
    destination_client = forms.ModelChoiceField(Client.objects.all())

    class Meta:
        model = Job
        fields = ('action', 'package', 'source_client', 'destination_client')
