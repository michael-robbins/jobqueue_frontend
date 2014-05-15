import django_tables2 as tables
from frontend.models import Client, Category, Job, Package, File, ClientPackageAvailability

EDIT_ICON     = '<i class="glyphicon glyphicon-edit">'
DELETE_ICON   = '<i class="glyphicon glyphicon-remove">'
DISCOVER_ICON = '<i class="glyphicon glyphicon-search">'
HISTORY_ICON  = '<i class="glyphicon glyphicon-book">'

TEMPLATE_DICT = dict()
TEMPLATE_DICT['link'] = '<a href="{{% url "{0}" {1} %}}">{2}</a>'

TABLE_CLASS = dict()
TABLE_CLASS['class'] = "table table-striped table-hover"

class ClientTable(tables.Table):
    conn_string = tables.TemplateColumn('ssh -p{{record.host_port}} {{record.host_username}}@{{record.host_hostname}}')

    discover    = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_discover'
                    , 'client_id=record.id'
                    , DISCOVER_ICON))

    history     = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_history'
                    , 'client_id=record.id'
                    , HISTORY_ICON))

    edit        = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_edit'
                    , 'client_id=record.id'
                    , EDIT_ICON))

    delete      = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_delete'
                    , 'client_id=record.id'
                    , DELETE_ICON))

    class Meta:
        model   = Client
        attrs   = TABLE_CLASS
        fields  = ('name', 'conn_string', 'base_path', 'max_download', 'max_upload', 'user', 'discover', 'history', 'edit', 'delete')

class CategoryTable(tables.Table):
    edit     = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.category_edit'
                    , 'category_name=record.name'
                    , EDIT_ICON))

    delete   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.category_delete'
                    , 'category_name=record.name'
                    , DELETE_ICON))

    class Meta:
        model   = Category
        attrs   = TABLE_CLASS
        exclude = ('id', )

class PackageTable(tables.Table):
    edit     = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.package_edit'
                    , 'package_id=record.id'
                    , EDIT_ICON))

    delete   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.package_delete'
                    , 'package_id=record.id'
                    , DELETE_ICON))

    class Meta:
        model   = Package
        attrs   = TABLE_CLASS
        exclude = ('id', 'metadata')

class JobTable(tables.Table):
    delete   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.job_delete'
                    , 'job_id=record.id'
                    , DELETE_ICON))

    class Meta:
        model   = Job
        attrs   = TABLE_CLASS
        exclude = ('id', )

