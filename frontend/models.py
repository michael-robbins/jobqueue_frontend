from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import string

JOB_ACTIONS = (
    ('SYNC','Sync')
    , ('INDX','Index')
    , ('DEL','Delete')
    )

JOB_STATES = (
    ('PEND','Pending')
    , ('PROG','In Progress')
    , ('COMP','Completed')
    , ('FAIL','Failed')
)

class Category(models.Model):
    name          = models.CharField(max_length=32,  blank=False)
    display_name  = models.CharField(max_length=32,  blank=False)
    relative_path = models.CharField(max_length=256, blank=False)

    def __str__(self):
        return self.display_name

    class Meta:
        permissions = (('view_category', 'Can view Category'),)

class Package(models.Model):
    name          = models.CharField(max_length=128, blank=False, unique=True)
    relative_path = models.CharField(max_length=256, blank=False)
    date_created  = models.DateTimeField(auto_now_add=True)
    metadata      = models.TextField(blank=False, default='')

    category        = models.ForeignKey(Category)
    parent_package  = models.ForeignKey('self', null=True)
    is_base_package = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (('view_package', 'Can view Package'),)

class File(models.Model):
    relative_path = models.CharField(max_length=256, blank=False)
    file_hash     = models.CharField(max_length=128, blank=False)
    package       = models.ForeignKey(Package)

    def __str__(self):
        return self.relative_path

    class Meta:
        permissions = (('view_file', 'Can view File'),)

class Client(models.Model):
    name          = models.CharField(max_length=64,  blank=False, unique=True)
    host_username = models.CharField(max_length=64,  blank=False)
    host_hostname = models.CharField(max_length=128, blank=False)
    host_port     = models.IntegerField(blank=False, default=22)
    base_path     = models.CharField(max_length=256, blank=False)
    max_download  = models.IntegerField(blank=False, default=0)
    max_upload    = models.IntegerField(blank=False, default=0)
    user          = models.ForeignKey(User)

    packages      = models.ManyToManyField(Package, through='ClientPackageAvailability')
    package_files = models.ManyToManyField(File,    through='ClientFileAvailability')

    def __str__(self):
        return self.name

    class Meta:
        permissions = (('view_client', 'Can view Client'),)

class ClientPackageAvailability(models.Model):
    client       = models.ForeignKey(Client)
    package      = models.ForeignKey(Package)
    availability = models.BooleanField(blank=False, default=False)
    last_index   = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __str__(self):
        return self.availability

    class Meta:
        permissions = (('view_clientpackageavailability', 'Can view Client File Availability'),)

class ClientFileAvailability(models.Model):
    client       = models.ForeignKey(Client)
    package_file = models.ForeignKey(File)
    availability = models.BooleanField(blank=False, default=False)
    last_index   = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __str__(self):
        return self.availability

    class Meta:
        permissions = (('view_clientfileavailability', 'Can view Client File Availability'),)

class Job(models.Model):
    state  = models.CharField(max_length=4, blank=False, choices=JOB_STATES, default=JOB_STATES[0][0])
    action = models.CharField(max_length=4, blank=False, choices=JOB_ACTIONS)

    package            = models.ForeignKey(Package)
    destination_client = models.ForeignKey(Client, related_name='+')
    source_client      = models.ForeignKey(Client, related_name='+')
    user               = models.ForeignKey(User)

    def __str__(self):
        state  = [ i[1] for i in JOB_STATES if i[0] == self.state ][0]
        action = [ i[1] for i in JOB_ACTIONS if i[0] == self.action ][0]

        return "{0} - {1} - {2} - {3} -> {4}".format(
                    state
                    , action
                    , self.package
                    , self.source_client
                    , self.destination_client)

    class Meta:
        permissions = (('view_job', 'Can view Job'),)

