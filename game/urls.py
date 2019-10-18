from django.conf.urls import url
from game.views import GameView, RoundView
from home.views import HomeLogOutView
urlpatterns = [
    url(r'^$', GameView.as_view(), name='game'),
    url(r'^round-(?P<round_number>\w+)/$', RoundView.as_view()),
]
