import django_tables2 as tables

from frontend.models import Client, Category, Job, Package, File, ClientFileAvailability

BASE_ICON     = '<i class="glyphicon glyphicon-{0}">'
CHANGE_ICON   = BASE_ICON.format('edit')
DELETE_ICON   = BASE_ICON.format('remove')
DISCOVER_ICON = BASE_ICON.format('search')
HISTORY_ICON  = BASE_ICON.format('book')

TEMPLATE_DICT = dict()
TEMPLATE_DICT['link'] = '<a href="{{% url "{0}" {1} %}}">{2}</a>'

TABLE_CLASS = dict()
TABLE_CLASS['class'] = "table table-striped table-hover"

class ClientTable(tables.Table):
    conn_template = 'ssh -p{{record.host_port}} {{record.host_username}}@{{record.host_hostname}}'
    conn_string   = tables.TemplateColumn(conn_template, orderable=False)

    discover    = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_discover'
                    , 'client_id=record.id'
                    , DISCOVER_ICON), orderable=False)

    history     = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_history'
                    , 'client_id=record.id'
                    , HISTORY_ICON), orderable=False)

    change      = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_change'
                    , 'client_id=record.id'
                    , CHANGE_ICON), orderable=False)

    delete      = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.client_delete'
                    , 'client_id=record.id'
                    , DELETE_ICON), orderable=False)

    class Meta:
        model   = Client
        attrs   = TABLE_CLASS
        fields  = ('name', 'conn_string', 'base_path', 'max_download', 'max_upload', 'user',
                   'discover', 'history', 'change', 'delete')

class CategoryTable(tables.Table):
    change   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.category_change'
                    , 'category_name=record.name'
                    , CHANGE_ICON), orderable=False)

    delete   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.category_delete'
                    , 'category_name=record.name'
                    , DELETE_ICON), orderable=False)

    class Meta:
        model   = Category
        attrs   = TABLE_CLASS
        exclude = ('id', 'name')

class PackageTable(tables.Table):
    change   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.package_change'
                    , 'package_id=record.id'
                    , CHANGE_ICON), orderable=False)

    delete   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.package_delete'
                    , 'package_id=record.id'
                    , DELETE_ICON), orderable=False)

    class Meta:
        model   = Package
        attrs   = TABLE_CLASS
        fields  = ('name', 'relative_path', 'category', 'parent_package',
                   'is_base_package', 'date_created')

class JobTable(tables.Table):
    view     = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.job_view'
                    , 'job_id=record.id'
                    , DISCOVER_ICON), orderable=False)

    delete   = tables.TemplateColumn(TEMPLATE_DICT['link'].format(
                    'frontend.views.job_delete'
                    , 'job_id=record.id'
                    , DELETE_ICON), orderable=False)

    class Meta:
        model   = Job
        attrs   = TABLE_CLASS
        exclude = ('id', )

class ClientFileAvailabilityTable(tables.Table):
    class Meta:
        model = ClientFileAvailability
        attrs = TABLE_CLASS
