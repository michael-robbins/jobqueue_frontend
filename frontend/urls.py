from django.conf.urls import patterns, url
from frontend import views

urlpatterns = patterns(''
        , url(r'^$', views.index)
        , url(r'^login/$', views.user_login)
        , url(r'^logout/$', views.user_logout)
        , url(r'^profile/$', views.profile)

        , url(r'^categories/$', views.categories)
        , url(r'^categories/add/$', views.category_add)
        , url(r'^categories/(?P<category_id>\d+)/edit/$', views.category_edit)
        , url(r'^categories/(?P<category_id>\d+)/delete/$', views.category_delete)

        , url(r'^packages/$', views.packages)
        , url(r'^packages/add/$', views.package_add)
        , url(r'^packages/(?P<package_id>\d+)/$', views.package_view)
        , url(r'^packages/(?P<package_id>\d+)/edit/$', views.package_edit)
        , url(r'^packages/(?P<package_id>\d+)/delete/$', views.package_delete)

        , url(r'^clients/$', views.clients)
        , url(r'^clients/add/$', views.client_add)
        , url(r'^clients/(?P<client_id>\d+)/$', views.client_view)
        , url(r'^clients/(?P<client_id>\d+)/edit/$', views.client_edit)
        , url(r'^clients/(?P<client_id>\d+)/delete/$', views.client_delete)
        , url(r'^clients/(?P<client_id>\d+)/discover/$', views.client_discover)

        , url(r'^jobs/$', views.jobs)
        , url(r'^jobs/add/$', views.job_add)
        , url(r'^jobs/(?P<job_id>\d+)/$', views.job_view)
        , url(r'^jobs/(?P<job_id>\d+)/delete/$', views.job_delete)

        , url(r'^jobs/history/$', views.job_history)
        , url(r'^jobs/history/(?P<client_id>\d+)/$', views.job_history_client)
    )

