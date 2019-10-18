import random
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.http import JsonResponse, HttpResponseRedirect
from account.models import Participants
from game.models import PrimaryImages, SecondaryImages, Game
from game.forms import SecondaryImageForm

# Create your views here.


class GameView(CreateView):
    template_name = 'game.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/home/?valid=0')
        return super(GameView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'show_game_button': True,
            'user': request.user
        })

    def post(self, request, *args, **kwargs):
        while True:
            available_players = Participants.objects.filter(is_loggedin=True).exclude(username=request.user.username)
            if available_players.count() > 1:
                break
            else:
                continue

        player2 = self.generate_random_pair(available_players)
        data = {
            'player1': request.user.username,
            'player2': player2.username,
        }
        return JsonResponse(data, safe=False)

    def generate_random_pair(self, available_players):
        available_players_count = available_players.count()
        # Generating player 2 random distinct index for the first time
        pIndex = self.generate_random_indexes(available_players_count)
        player2_already_playing, player2 = self.check_if_player_playing(pIndex, available_players)

        while player2_already_playing:
            # Generating player 2 random distinct index
            pIndex = self.generate_random_indexes(available_players_count)
            player2_already_playing, player2 = self.check_if_player_playing(pIndex, available_players)
        return player2

    def generate_random_indexes(self, available_players_count, *args):
        pIndex = random.randint(0, available_players_count-1)
        return pIndex

    def check_if_player_playing(self, pIndex, available_players):
        player2 = available_players[pIndex]
        player2_already_playing = Game.objects.filter(is_playing=True, player1=player2)
        if not player2_already_playing:
            player2_already_playing = Game.objects.filter(is_playing=True, player2=player2)
        return player2_already_playing, player2


class RoundView(TemplateView):
    template_name = 'game_rounds.html'
    form_class = SecondaryImageForm

    def get(self, request, *args, **kwargs):
        round_number = kwargs.get('round_number')
        primary_images = None
        secondary_images = None
        pIndex = None
        if int(round_number) <= 5:
            primary_images = request.session.get('primary_images', None)
            secondary_images = request.session.get('secondary_images', None)
            pIndex = random.randint(0, len(primary_images)-1)
        return render(request, self.template_name, {
            'primary_image': primary_images[pIndex],
            'secondary_images': secondary_images
        })
