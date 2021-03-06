from rest_framework import serializers

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
    user = serializers.SlugRelatedField(slug_field='username')

    class Meta:
        model = Client
        exclude = ('packages', 'package_files')


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

