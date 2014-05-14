from django import forms, template
from django.db.models import Q
from frontend.models import Client, Category, Package, Job, JOB_ACTIONS, JOB_STATES
import datetime
import string

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        widgets = {
              'name':          forms.TextInput(attrs={'placeholder': 'Name of Client'})
            , 'host_username': forms.TextInput(attrs={'placeholder': 'User we are connecting as'})
            , 'host_hostname': forms.TextInput(attrs={'placeholder': 'FQDN of the Host'})
            , 'base_path':     forms.TextInput(attrs={'placeholder': '/path/to/base/media/directory'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        print('clean_name() got called')

        return name

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        widgets = {
              'name':          forms.TextInput(attrs={'placeholder': 'Behind-the-scenes name of the Category'})
            , 'display_name':  forms.TextInput(attrs={'placeholder': 'Name everyone will see'})
            , 'relative_path': forms.TextInput(attrs={'placeholder': 'path/to/category/relative/to/base/path'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if ' ' in name or string.ascii_uppercase in name:
            raise forms.ValidationError('Cannot contain any uppercase characters or spaces!')

        return name

    def clean_display_name(self):
        relative_name = self.cleaned_data['display_name'].strip()

        return relative_name

    def clean_relative_path(self):
        relative_path = self.cleaned_data['relative_path'].strip()

        if relative_path.startswith('/'):
            raise forms.ValidationError('Relative Path cannot start with a \'/\', needs to be relative!')

        return relative_path

class PackageForm(forms.ModelForm):
    category       = forms.ModelChoiceField(Category.objects.all(), required=True)
    parent_package = forms.ModelChoiceField(Package.objects.filter(is_base_package=False).filter(category__name='tv_episodes'), required=False)

    class Meta:
        model = Package
        fields = ('name', 'relative_path', 'category', 'parent_package', 'is_base_package')

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        return name

    def clean_relative_path(self):
        relative_path = self.cleaned_data['relative_path'].strip()

        if relative_path.startswith('/'):
            raise forms.ValidationError('Relative Path cannot start with a \'/\', needs to be relative!')

        return relative_path

    def clean(self):
        # This is called after the individual field clean's are called
        cleaned_data = self.cleaned_data

        category        = cleaned_data['category']
        parent_package  = cleaned_data['parent_package']
        is_base_package = cleaned_data['is_base_package']

        if is_base_package and category != 'tv_episodes':
            raise forms.ValidationError('Only TV Episodes are allowed to be base packages')

        if is_base_package and parent_package != None:
            raise forms.ValidationError('We only allow one level of recursion with TV Episodes (Base -> Season X)')

        return cleaned_data

class JobForm(forms.ModelForm):
    package            = forms.ModelChoiceField(Package.objects.all())
    source_client      = forms.ModelChoiceField(Client.objects.all())
    destination_client = forms.ModelChoiceField(Client.objects.all())

    class Meta:
        model = Job
        fields = ('action', 'package', 'source_client', 'destination_client')

