import os
import time
import datetime

def populate():
    test_user_1 = add_User(username='test')

    test_client_1 = add_Client(name='Test Client #1', host_username='test', host_hostname='testhost1'
                            , host_port=22, base_path='/data/media/', user=test_user_1)
    test_client_2 = add_Client(name='Test Client #2', host_username='test', host_hostname='testhost2'
                            , host_port=22, base_path='/data/media/', user=test_user_1)

    movie_category = add_Category('Movies', 'movies/')
    tv_category    = add_Category('TV Episodes', 'tv/')

    movie_package   = add_Package('Movie #1', 'Movie 1 (2009)/', movie_category, None)
    tv_base_package = add_Package('TV Show 1 - Base', 'TV Show 1/', tv_category, None)
    tv_s1_package   = add_Package('TV Show 1 - S1'  , 'Season 1/', tv_category, None)

    movie_file_1 = add_File(
                    'Test Movie (2009).mkv'
                    , 'sdofys&)NFY0W389PU(*e&TF7SGUdsgfnsdFIYQ3G8721'
                    , movie_package)

    movie_file_2 = add_File(
                    'Test Movie (2009).nfo'
                    , 'asdifu98ertu30q984uyr098MWFU0W&YWE0F7TWE968TF'
                    , movie_package)

    tv_base_file_1 = add_File(
                    'TV-Base.nfo'
                    , '9*sdyuf08&YSD(F&*ts&Df6bSUDfcufysdfasd98sd)(*'
                    , tv_base_package)

    tv_base_file_2 = add_File(
                    'TV-Base.jpg'
                    , 'OSUDytfb76sDr5f8rsb87fSdf^5sdE^$%SDSDFS(&*Df6'
                    , tv_base_package)

    tv_s1_file_1 = add_File(
                    'TV-S1E1.mkv'
                    , 'ODYF(S*&Dtfb976RSD85frS*%Drf%SRDf78SD*F*&S&Df'
                    , tv_s1_package)

    tv_s1_file_2 = add_File(
                    'TV-S1E2.mkv'
                    , 'PSD(*Yf0nS(*Dyf0SD57rfSIDfjLSFNUSDFSD%F#S$0-0'
                    , tv_s1_package)

    clientpackage_1 = add_ClientPackageAvailability(test_client_1, movie_package)
    clientpackage_2 = add_ClientPackageAvailability(test_client_2, tv_base_package)
    clientpackage_3 = add_ClientPackageAvailability(test_client_2, tv_s1_package)

    sync_job = add_Job('SYNC', movie_package, test_client_2, test_client_1, test_user_1)

def add_Client(name, host_username, host_hostname, host_port, base_path, user):
    c = Client.objects.get_or_create(name=name, host_username=host_username
                        , host_hostname=host_hostname, host_port=host_port, base_path=base_path, user=user)[0]
    return c

def add_Category(name, relative_path):
    m = Category.objects.get_or_create(name=name, relative_path=relative_path)[0]
    return m

def add_Package(name, relative_path, category, parent_package):
    p = Package.objects.get_or_create(name=name, relative_path=relative_path
                        , category=category, parent_package=parent_package)[0]
    return p

def add_File(relative_path, file_hash, package):
    f = File.objects.get_or_create(relative_path=relative_path, file_hash=file_hash
                        , package=package)[0]
    return f

def add_ClientPackageAvailability(client, package):
    c = ClientPackageAvailability.objects.get_or_create(client=client, package=package)[0]
    return c

def add_Job(action, package, destination_client, source_client, user):
    j = Job.objects.get_or_create(action=action, package=package
                        , destination_client=destination_client, source_client=source_client
                        , user=user)[0]
    return j

def add_User(username):
    u = User.objects.get_or_create(username=username)[0]
    return u

if __name__ == '__main__':
    db_file = 'db.sqlite3'

    print('Deleting DB and resyncdb\'ing in 10 seconds')
    print('Please create a superuser with the username \'test\' and password \'test\' when asked.')
    time.sleep(10)

    try:
        print('Starting: Deleting old DB')
        os.remove(db_file)
        print('Finished: Deleted old DB')
    except OSError:
        pass

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend_project.settings')
    from frontend.models import *
    from django.contrib.auth.models import User
    from django.core import management

    print('Starting: syncdb')
    management.call_command('syncdb')
    print('Finished: syncdb')

    print("Starting: population")
    populate()
    print("Finished: population")
