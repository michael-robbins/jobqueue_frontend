from rest_framework import serializers

from django.contrib.auth.models import User
from frontend.models import Category, Package, File, Client, Job
from frontend.models import ClientPackageAvailability, ClientFileAvailability

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        depth = 1

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        depth = 1

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        depth = 1
        exclude = ('user',)

class ClientPackageAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPackageAvailability

class ClientFileAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFileAvailability

