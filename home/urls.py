from django.conf.urls import url
from home.views import HomeView, HomeLogOutView
urlpatterns = [
    url(r'^login/$', HomeView.as_view(), name='login'),
    url(r'logout/', HomeLogOutView.as_view(), name='logout'),
]
