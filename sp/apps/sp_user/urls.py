from django.conf.urls import url

from sp_user.views import (RegisterView,
                           LoginView,
                           CenterView,
                           InfoView,
                           center,
                           sendMsg)

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^center/$', CenterView.as_view(), name='center'),
    # url(r'^center/$', center, name='center'),
    url(r'^info/$', InfoView.as_view(), name='info'),
    url(r'^sendMsg/$', sendMsg, name='sendMsg'),
]
