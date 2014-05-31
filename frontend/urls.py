from django.conf.urls import patterns, url
from frontend import views

urlpatterns = patterns(''
        , url(r'^$', views.index
                   , name='index')
        , url(r'^login/$', views.user_login
                         , name='user_login')
        , url(r'^logout/$', views.user_logout
                          , name='user_logout')
        , url(r'^profile/$', views.user_profile
                           , name='user_profile')

        , url(r'^categories/$', views.categories
                              , name='categories')
        , url(r'^categories/add/$', views.category_add
                                  , name='category_add')
        , url(r'^categories/(?P<category_name>\w+)/change/$', views.category_change
                                                            , name='category_change')
        , url(r'^categories/(?P<category_name>\w+)/delete/$', views.category_delete
                                                            , name='category_delete')

        , url(r'^packages/$', views.packages
                            , name='packages')
        , url(r'^packages/add/$', views.package_add
                                , name='package_add')
        , url(r'^packages/(?P<package_id>\d+)/$', views.package_view
                                                , name='package_view')
        , url(r'^packages/(?P<package_id>\d+)/change/$', views.package_change
                                                       , name='package_change')
        , url(r'^packages/(?P<package_id>\d+)/delete/$', views.package_delete
                                                       , name='package_delete')

        , url(r'^clients/$', views.clients
                           , name='clients')
        , url(r'^clients/add/$', views.client_add
                               , name='client_add')
        , url(r'^clients/(?P<client_id>\d+)/change/$', views.client_change
                                                     , name='client_change')
        , url(r'^clients/(?P<client_id>\d+)/delete/$', views.client_delete
                                                     , name='client_delete')
        , url(r'^clients/(?P<client_id>\d+)/discover/$', views.client_discover
                                                       , name='client_discover')
        , url(r'^clients/(?P<client_id>\d+)/history/$', views.client_history
                                                      , name='client_history')

        , url(r'^jobs/$', views.jobs
                        , name='jobs')
        , url(r'^jobs/add/$', views.job_add
                            , name='job_add')
        , url(r'^jobs/history/$', views.job_history
                                , name='job_history')
        , url(r'^jobs/(?P<job_id>\d+)/$', views.job_view
                                        , name='job_view')
        , url(r'^jobs/(?P<job_id>\d+)/delete/$', views.job_delete
                                               , name='job_delete')
    )

