from django import forms
from django.db.models import Q

from frontend.models import Client, Category, Package, Job, JOB_ACTIONS, JOB_STATES

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div
from crispy_forms.bootstrap import FormActions

import datetime
import string

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        form_title = kwargs.pop('form_title')

        super(ClientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = 'id-ClientForm'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.help_text_inline = True
        self.helper.error_text_inline = True
        self.helper.html5_required = True

        self.helper.layout = Layout(
            Fieldset(
                '<h2>{0}</h2>'.format(form_title)
                , 'name'
                , 'host_username'
                , 'host_hostname'
                , 'host_port'
                , 'base_path'
                , 'max_download'
                , 'max_upload'
                , 'user'
            ),
            FormActions(Submit('submit', 'Submit'))
        )

    class Meta:
        model = Client

        name = {'placeholder': 'Name of the Client'}
        host_username = {'placeholder': 'User we are connecting as'}
        host_hostname = {'placeholder': 'FQDN of the host'}
        base_path = {'placeholder': '/path/to/base/dir/for/media'}

        widgets = {
              'name': forms.TextInput(attrs=name)
            , 'host_username': forms.TextInput(attrs=host_username)
            , 'host_hostname': forms.TextInput(attrs=host_hostname)
            , 'base_path': forms.TextInput(attrs=base_path)
        }

    def clean_name(self): return self.cleaned_data['name'].strip()

class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        form_title = kwargs.pop('form_title')

        super(CategoryForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = 'id-CategoryForm'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.help_text_inline = True
        self.helper.error_text_inline = True
        self.helper.html5_required = True

        self.helper.layout = Layout(
            Fieldset(
                '<h2>{0}</h2>'.format(form_title)
                , 'name'
                , 'display_name'
                , 'relative_path'
            ),
            FormActions(Submit('submit', 'Submit'))
        )

    class Meta:
        model = Category

        name = {'placeholder': 'Behind-the-scenes name of the Category'}
        display_name = {'placeholder': 'Name everyone will see'}
        relative_path = {'placeholder': 'path/to/category'}

        widgets = {
              'name': forms.TextInput(attrs=name)
            , 'display_name': forms.TextInput(attrs=display_name)
            , 'relative_path': forms.TextInput(attrs=relative_path)
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if ' ' in name or string.ascii_uppercase in name:
            message = 'Cannot contain any uppercase characters or spaces!'
            raise forms.ValidationError(message)

        return name

    def clean_display_name(self): return self.cleaned_data['display_name'].strip()

    def clean_relative_path(self):
        relative_path = self.cleaned_data['relative_path'].strip()

        if relative_path.startswith('/'):
            message = 'Relative path cannot start with a \'/\', needs to be relative!'
            raise forms.validationerror(message)

        return relative_path

class PackageForm(forms.ModelForm):
    category = forms.ModelChoiceField(Category.objects.all(), required=True)
    parent_package = forms.ModelChoiceField(Package.objects.filter(is_base_package=True)
                                            .filter(category__name='tv_episodes')
                                            , required=False)

    def __init__(self, *args, **kwargs):
        form_title = kwargs.pop('form_title')

        super(PackageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = 'id-PackageForm'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.help_text_inline = True
        self.helper.error_text_inline = True
        self.helper.html5_required = True

        self.helper.layout = Layout(
            Fieldset(
                '<h2>{0}</h2>'.format(form_title)
                , 'name'
                , 'relative_path'
                , 'category'
                , 'parent_package'
                , 'is_base_package'
            ),
            FormActions(Submit('submit', 'Submit'))
        )

    class Meta:
        model = Package

        fields = ('name', 'relative_path', 'category', 'parent_package', 'is_base_package')

    def clean_name(self): return self.cleaned_data['name'].strip()

    def clean_relative_path(self):
        relative_path = self.cleaned_data['relative_path'].strip()

        if relative_path.startswith('/'):
            message = 'Relative Path cannot start with a \'/\', needs to be relative!'
            raise forms.ValidationError(message)

        return relative_path

    def clean(self):
        # This is called after the individual field clean's are called
        cleaned_data = self.cleaned_data

        category = cleaned_data['category']
        parent_package = cleaned_data['parent_package']
        is_base_package = cleaned_data['is_base_package']

        tv_category = Category.objects.get(name='tv_episodes')

        if is_base_package:
            if category != tv_category:
                message = 'Only TV Episodes are allowed to be Base Packages'
                raise forms.ValidationError(message)
            elif parent_package != None:
                message = 'We only allow one level of recursion with TV Eps (Base -> S1)'
                raise forms.ValidationError(message)

        return cleaned_data

class JobForm(forms.ModelForm):
    package = forms.ModelChoiceField(Package.objects.all())
    source_client = forms.ModelChoiceField(Client.objects.all())
    destination_client = forms.ModelChoiceField(Client.objects.all())
    
    def __init__(self, *args, **kwargs):
        form_title = kwargs.pop('form_title')

        super(JobForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = 'id-JobForm'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.help_text_inline = True
        self.helper.error_text_inline = True
        self.helper.html5_required  = True

        self.helper.layout = Layout(
            Fieldset(
                '<h2>{0}</h2>'.format(form_title)
                , 'action'
                , 'package'
                , 'source_client'
                , 'destination_client'
            ),
            FormActions(Submit('submit', 'Submit'))
        )

    class Meta:
        model = Job

        fields = ('action', 'package', 'source_client', 'destination_client')

