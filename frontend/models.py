from django.db import models
from django.contrib.auth.models import User

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

class Client(models.Model):
    name          = models.CharField(max_length=64,  blank=False, unique=True)
    host_username = models.CharField(max_length=64,  blank=False)
    host_hostname = models.CharField(max_length=128, blank=False)
    host_port     = models.IntegerField(blank=False, default=22)
    base_path     = models.CharField(max_length=256, blank=False)
    max_download  = models.IntegerField(blank=False, default=0)
    max_upload    = models.IntegerField(blank=False, default=0)

    def __str__(self):
        return self.name

class MediaType(models.Model):
    name          = models.CharField(max_length=32,  blank=False)
    relative_path = models.CharField(max_length=256, blank=False)

    def __str__(self):
        return self.name

class Package(models.Model):
    name          = models.CharField(max_length=128, blank=False)
    relative_path = models.CharField(max_length=256, blank=False)
    date_created  = models.DateTimeField(auto_now_add=True)
    metadata      = models.TextField(blank=False, default='')

    media_type     = models.ForeignKey(MediaType)
    parent_package = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.name

class File(models.Model):
    relative_path = models.CharField(max_length=256, blank=False)
    file_hash     = models.CharField(max_length=128, blank=False)
    package       = models.ForeignKey(Package)

    def __str__(self):
        return self.relative_path

class ClientPackageAvailability(models.Model):
    availability = models.BooleanField(blank=False, default=True)
    last_index   = models.DateTimeField(auto_now_add=True)
    client       = models.ForeignKey(Client)
    package      = models.ForeignKey(Package)

    def __str__(self):
        return self.availability

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

