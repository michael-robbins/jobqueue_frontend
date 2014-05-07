from django.conf.urls import patterns, url
from frontend import views

urlpatterns = patterns(''
        , url(r'^$', views.index, name='index')
        , url(r'^login/$', views.user_login, name='login')
        , url(r'^logout/$', views.user_logout, name='logout')
        , url(r'^profile/$', views.profile, name='profile')

        , url(r'^media/$', views.media, name='media')
        , url(r'^media/types/$', views.media_types, name='media_types')
        , url(r'^media/types/add/$', views.media_type_add, name='media_type_add')
        , url(r'^media/types/(?P<media_type_id>\d+)/$', views.media_type_view, name='media_type_view')
        , url(r'^media/types/(?P<media_type_id>\d+)/edit/$', views.media_type_edit, name='media_type_edit')
        , url(r'^media/discover/$', views.media_discover, name='media_discover')
        , url(r'^media/discover/(?P<client_id>\d+)/$', views.media_discover_client, name='media_discover_client')
        , url(r'^media/packages/$', views.media_packages, name='media_packages')
        , url(r'^media/packages/add/$', views.media_package_add, name='media_package_add')
        , url(r'^media/packages/(?P<package_id>\d+)/$', views.media_package_view, name='media_package_view')
        , url(r'^media/packages/(?P<package_id>\d+)/edit/$', views.media_package_edit, name='media_package_edit')

        , url(r'^clients/$', views.clients, name='clients')
        , url(r'^clients/add/$', views.client_add, name='client_add')
        , url(r'^clients/(?P<client_id>\d+)/$', views.client_view, name='client_view')
        , url(r'^clients/(?P<client_id>\d+)/edit/$', views.client_edit, name='client_edit')

        , url(r'^jobs/$', views.jobs, name='jobs')
        , url(r'^jobs/(?P<job_id>\d+)/$', views.job_view, name='jobs')
        , url(r'^jobs/add/$', views.job_add, name='job_add')
        , url(r'^jobs/history/$', views.job_history, name='job_history')
        , url(r'^jobs/history/(?P<client_id>\d+)/$', views.job_history_client, name='job_history_client')
    )

