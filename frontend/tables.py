import django_tables2 as tables
from frontend.models import Client, Category, Job, Package, File, ClientPackageAvailability

class ClientTable(tables.Table):
    class Meta:
        model = Client
        attrs = {"class": "table table-striped table-hover"}
