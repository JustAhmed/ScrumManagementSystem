from django.conf.urls import url
from django.contrib import admin
from backlog import views
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/$', views.home, name='home'),
    url(r'^backlogs/new/$', views.new_backlog, name='new_backlog'),
    url(r'^backlogs/(?P<pk>\d+)/$', views.backlog_sprints, name='backlog_sprints'),
    url(r'^backlogs/(?P<pk>\d+)/sprints/(?P<spk>\d+)/$', views.sprint_tasks, name='sprint_tasks'),
    url(r'^backlogs/(?P<pk>\d+)/sprints/(?P<spk>\d+)/control/$', views.modify_task, name='modify_task'),
    url(r'^backlogs/(?P<pk>\d+)/sprints/(?P<spk>\d+)/new$', views.new_task, name='new_task'),
    url(r'^backlogs/(?P<pk>\d+)/new/$', views.new_sprint, name='new_sprint'),
    #url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    url(r'^about/$', views.AboutPage.as_view(),name="about"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^signup/$', views.signup, name='signup'),

]
