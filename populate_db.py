#!/usr/bin/env python3

import os


def populate():
    super_user = User.objects.get(username='test')
    super_user_token = Token.objects.create(user=super_user)
    print("Super User Token: {0}".format(super_user_token.key))

    test_user_1 = add_user(username='test1', email='test1@test.com', password='test1')
    test_user_1.set_password('test1')
    test_user_1.save()
    test_user_1_token = Token.objects.create(user=test_user_1)
    print("User1 Token: {0}".format(test_user_1_token.key))

    test_user_2 = add_user(username='test2', email='test2@test.com', password='test2')
    test_user_2.set_password('test2')
    test_user_2.save()
    test_user_2_token = Token.objects.create(user=test_user_2)
    print("User2 Token: {0}".format(test_user_2_token.key))

    test_user_3 = add_user(username='test3', email='test3@test.com', password='test3')
    test_user_3.set_password('test3')
    test_user_3.save()
    test_user_3_token = Token.objects.create(user=test_user_3)
    print("User3 Token: {0}".format(test_user_3_token.key))

    test_group_1 = add_group(name='Test Group 1')
    test_group_2 = add_group(name='Test Group 2')
    test_group_3 = add_group(name='Test Group 3')
    test_group_4 = add_group(name='Test Group 4')

    super_user.groups.add(test_group_1, test_group_2, test_group_3, test_group_4)
    test_user_1.groups.add(test_group_1)
    test_user_2.groups.add(test_group_2)
    test_user_3.groups.add(test_group_3)

    # Client population
    test_client_1 = add_client(name='Test Client #1', host_username='test', host_hostname='testhost1', host_port=22,
                               base_path='/data/media/', user=super_user)
    test_client_2 = add_client(name='Test Client #2', host_username='test', host_hostname='testhost2', host_port=22,
                               base_path='/data/media/', user=test_user_1)
    test_client_3 = add_client(name='Test Client #3', host_username='test', host_hostname='testhost3', host_port=22,
                               base_path='/data/media/', user=test_user_1)
    test_client_4 = add_client(name='Test Client #4', host_username='test', host_hostname='testhost4', host_port=22,
                               base_path='/data/media/', user=test_user_2)
    test_client_5 = add_client(name='Test Client #5', host_username='test', host_hostname='testhost5', host_port=22,
                               base_path='/data/media/', user=test_user_3)

    perm_add_client = Permission.objects.get(codename='add_client')
    perm_change_client = Permission.objects.get(codename='change_client')
    perm_delete_client = Permission.objects.get(codename='delete_client')
    perm_view_client = Permission.objects.get(codename='view_client')

    # Category population
    movie_category = add_category('movies', 'Movies', 'movies/')
    tv_category = add_category('tv_episodes', 'TV Episodes', 'tv/')

    perm_add_category = Permission.objects.get(codename='add_category')
    perm_change_category = Permission.objects.get(codename='change_category')
    perm_delete_category = Permission.objects.get(codename='delete_category')
    perm_view_category = Permission.objects.get(codename='view_category')

    # Package population
    movie_package = add_package('Movie #1', 'Movie 1 (2009)/', movie_category, None, False)
    tv_base_package = add_package('TV Show 1 - Base', 'TV Show 1/', tv_category, None, True)
    tv_s1_package = add_package('TV Show 1 - S1', 'Season 1/', tv_category, tv_base_package, False)

    perm_add_package = Permission.objects.get(codename='add_package')
    perm_change_package = Permission.objects.get(codename='change_package')
    perm_delete_package = Permission.objects.get(codename='delete_package')
    perm_view_package = Permission.objects.get(codename='view_package')

    # File population
    movie_file_1 = add_file('Test Movie (2009).mkv', 'sdofys&)NFY0W389PU(*e&TF7SGUdsgfnsdFIYQ3G8721', movie_package)
    movie_file_2 = add_file('Test Movie (2009).nfo', 'asdifu98ertu30q984uyr098MWFU0W&YWE0F7TWE968TF', movie_package)
    tv_base_file_1 = add_file('TV-Base.nfo', '9*sdyuf08&YSD(F&*ts&Df6bSUDfcufysdfasd98sd)(*', tv_base_package)
    tv_base_file_2 = add_file('TV-Base.jpg', 'OSUDytfb76sDr5f8rsb87fSdf^5sdE^$%SDSDFS(&*Df6', tv_base_package)
    tv_s1_file_1 = add_file('TV-S1E1.mkv', 'ODYF(S*&Dtfb976RSD85frS*%Drf%SRDf78SD*F*&S&Df', tv_s1_package)
    tv_s1_file_2 = add_file('TV-S1E2.mkv', 'PSD(*Yf0nS(*Dyf0SD57rfSIDfjLSFNUSDFSD%F#S$0-0', tv_s1_package)

    perm_add_file = Permission.objects.get(codename='add_file')
    perm_change_file = Permission.objects.get(codename='change_file')
    perm_delete_file = Permission.objects.get(codename='delete_file')
    perm_view_file = Permission.objects.get(codename='view_file')

    # Client Package Availability population
    add_clientpackageavailability(test_client_1, movie_package)
    add_clientpackageavailability(test_client_2, tv_base_package)
    add_clientpackageavailability(test_client_2, tv_s1_package)
    add_clientpackageavailability(test_client_3, movie_package)
    add_clientpackageavailability(test_client_4, movie_package)
    add_clientpackageavailability(test_client_5, movie_package)

    perm_add_clientpackage = Permission.objects.get(codename='add_clientpackageavailability')
    perm_change_clientpackage = Permission.objects.get(codename='change_clientpackageavailability')
    perm_delete_clientpackage = Permission.objects.get(codename='delete_clientpackageavailability')
    perm_view_clientpackage = Permission.objects.get(codename='view_clientpackageavailability')

    # Client File Availability population
    add_clientfileavailability(test_client_1, movie_file_1)
    add_clientfileavailability(test_client_1, movie_file_2)
    add_clientfileavailability(test_client_2, tv_base_file_1)
    add_clientfileavailability(test_client_2, tv_base_file_2)
    add_clientfileavailability(test_client_2, tv_s1_file_1)
    add_clientfileavailability(test_client_2, tv_s1_file_2)

    perm_add_clientfile = Permission.objects.get(codename='add_clientfileavailability')
    perm_change_clientfile = Permission.objects.get(codename='change_clientfileavailability')
    perm_delete_clientfile = Permission.objects.get(codename='delete_clientfileavailability')
    perm_view_clientfile = Permission.objects.get(codename='view_clientfileavailability')

    # Job population
    add_job('SYNC', movie_package, test_client_2, test_client_1, super_user)
    add_job('SYNC', movie_package, test_client_1, test_client_2, super_user)
    add_job('SYNC', movie_package, test_client_2, test_client_1, test_user_1)
    add_job('SYNC', movie_package, test_client_2, test_client_1, test_user_2)

    perm_add_job = Permission.objects.get(codename='add_job')
    perm_change_job = Permission.objects.get(codename='change_job')
    perm_delete_job = Permission.objects.get(codename='delete_job')
    perm_view_job = Permission.objects.get(codename='view_job')

    # Permission Assignment
    permission_group_1 = (perm_add_client, perm_change_client, perm_delete_client, perm_view_client, perm_add_category,
                          perm_change_category, perm_delete_category, perm_view_category)
    permission_group_2 = (perm_add_package, perm_change_package, perm_delete_package, perm_view_package, perm_add_file,
                          perm_change_file, perm_delete_file, perm_view_file)
    permission_group_3 = (perm_add_clientpackage, perm_change_clientpackage, perm_delete_clientpackage,
                          perm_view_clientpackage, perm_add_clientfile, perm_change_clientfile, perm_delete_clientfile,
                          perm_view_clientfile)
    permission_group_4 = (perm_add_job, perm_change_job, perm_delete_job, perm_view_job)

    test_group_1.permissions.add(*permission_group_1)
    test_group_2.permissions.add(*permission_group_2)
    test_group_3.permissions.add(*permission_group_3)
    test_group_4.permissions.add(*permission_group_4)


def add_client(name, host_username, host_hostname, host_port, base_path, user):
    c = Client.objects.get_or_create(name=name, host_username=host_username, host_hostname=host_hostname,
                                     host_port=host_port, base_path=base_path, user=user)
    return c[0]


def add_category(name, display_name, relative_path):
    m = Category.objects.get_or_create(name=name, display_name=display_name, relative_path=relative_path)
    return m[0]


def add_package(name, relative_path, category, parent_package, is_base_package):
    p = Package.objects.get_or_create(name=name, relative_path=relative_path, category=category,
                                      parent_package=parent_package, is_base_package=is_base_package)
    return p[0]


def add_file(relative_path, file_hash, package):
    f = File.objects.get_or_create(relative_path=relative_path, file_hash=file_hash, package=package)
    return f[0]


def add_clientpackageavailability(client, package):
    cp = ClientPackageAvailability.objects.get_or_create(client=client, package=package)
    return cp[0]


def add_clientfileavailability(client, package_file):
    cf = ClientFileAvailability.objects.get_or_create(client=client, package_file=package_file)
    return cf[0]


def add_job(action, package, destination_client, source_client, user):
    j = Job.objects.get_or_create(action=action, package=package, destination_client=destination_client,
                                  source_client=source_client, user=user)
    return j[0]


def add_user(username, email=None, password=None):
    u = User.objects.get_or_create(username=username, email=email, password=password)
    return u[0]


def add_group(name):
    g = Group.objects.get_or_create(name=name)
    return g[0]

if __name__ == '__main__':
    db_file = 'db.sqlite3'

    try:
        print('Starting: Deleting old DB')
        os.remove(db_file)
        print('Finished: Deleted old DB')
    except OSError:
        print('WARNING: DB file not found.')
        pass

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend_project.settings')
    from frontend.models import *
    from django.contrib.auth.models import User, Group, Permission
    from rest_framework.authtoken.models import Token
    from django.contrib.auth.management.commands import changepassword
    from django.core import management

    print('Starting: syncdb & superuser')
    management.call_command('syncdb', interactive=False)
    management.call_command('createsuperuser', interactive=False, username='test', email='test@test.com')
    command = changepassword.Command()
    command._get_pass = lambda *args: 'test'
    command.execute('test')
    print('Finished: syncdb & superuser')

    print('Starting: population')
    populate()
    print('Finished: population')

    #print('Starting: collectstatic')
    #management.call_command('collectstatic', interactive=False)
    #print('Finished: collectstatic')
