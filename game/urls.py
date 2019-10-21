from django.conf.urls import url
from game.views import GameView, RoundView
from home.views import HomeLogOutView
urlpatterns = [
    url(r'^$', GameView.as_view(), name='game'),
    url(r'^round/$', RoundView.as_view()),
]
