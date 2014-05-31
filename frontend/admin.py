from django.contrib import admin

from frontend.models import Category, Package, File, Client, Job

admin.site.register(Category)
admin.site.register(Package)
admin.site.register(File)
admin.site.register(Client)
admin.site.register(Job)
