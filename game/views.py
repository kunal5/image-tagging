import random
import time
from django.shortcuts import render
from django.db.models import Q
from django.views.generic import CreateView, FormView
from django.http import JsonResponse, HttpResponseRedirect
from account.models import Participants
from game.models import PrimaryImages, SecondaryImages, Game, SharedPair
# from game.forms import SecondaryImageForm

# Create your views here.


class GameView(CreateView):
    template_name = 'game.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/home/login/?valid=0')
        return super(GameView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        Participants.objects.filter(username=request.user.username).update(searching_pair=False)
        Game.objects.filter(Q(player1=request.user) | Q(player2=request.user)).update(is_playing=False)
        SharedPair.objects.filter(Q(sharedplayer1=request.user) | Q(sharedplayer2=request.user)).update(is_pair=False)
        return render(request, self.template_name, {
            'show_game_button': True,
            'user': request.user
        })

    def post(self, request, *args, **kwargs):
        player1 = None
        player2 = None
        available_players = Participants.objects.filter(is_loggedin=True, searching_pair=True).exclude(
            username=request.user.username)
        if available_players.count() >= 1:
            player1 = Participants.objects.get(username=request.user.username)
            player2 = self.generate_random_pair(available_players)
            Participants.objects.filter(username=request.user.username).update(searching_pair=False)
            SharedPair.objects.create(sharedplayer1=player1, sharedplayer2=player2, is_pair=True)
        else:
            Participants.objects.filter(username=request.user.username).update(searching_pair=True)
            while True:
                # available_players = Participants.objects.filter(is_loggedin=True, searching_pair=True).exclude(
                #     username=request.user.username)
                if SharedPair.objects.filter(sharedplayer2=request.user, is_pair=True):
                    player2 = SharedPair.objects.filter(sharedplayer2=request.user, is_pair=True)[0].sharedplayer1
                    player1 = request.user
                    Participants.objects.filter(username=player2.username).update(searching_pair=False)
                    break
                # if available_players.count() >= 1:
                #     # Participants.objects.filter(username=request.user.username).update(searching_pair=False)
                #     break
                # elif Participants.objects.filter(username=request.user.username, searching_pair=False):
                #     break
                else:
                    continue
        print('outside while')
        # if not player2:
        #     player2 = self.generate_random_pair(available_players)
        # Participants.objects.filter(username=request.user.username).update(searching_pair=False)
        data = {
            'player1': player1.username,
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
            print("inside while")
            pIndex = self.generate_random_indexes(available_players_count)
            player2_already_playing, player2 = self.check_if_player_playing(pIndex, available_players)
        return player2

    def generate_random_indexes(self, available_players_count, *args):
        try:
            pIndex = random.randint(0, available_players_count-1)
        except ValueError:
            pIndex = 0
        return pIndex

    def check_if_player_playing(self, pIndex, available_players):
        print(pIndex)
        print(available_players)
        try:
            player2 = available_players[pIndex]
        except IndexError:
            print("inside index error")
            time.sleep(1)
            player2 = available_players[pIndex]
        player2_already_playing = Game.objects.filter(is_playing=True, player1=player2)
        if not player2_already_playing:
            player2_already_playing = Game.objects.filter(is_playing=True, player2=player2)
        return player2_already_playing, player2


class RoundView(FormView):
    template_name = 'game_rounds.html'
    # form_class = SecondaryImageForm

    def get(self, request, *args, **kwargs):
        p1 = request.GET.get('player1')
        p2 = request.GET.get('player2')
        player1 = Participants.objects.get(username=p1)
        player2 = Participants.objects.get(username=p2)
        game = self.get_game(player1, player2)
        sharedpair = self.get_sharedpair(player1, player2)
        primary_indexes, secondary_indexes = self.que_and_ans_in_shared_pair(sharedpair[0], game)

        print(primary_indexes)
        print(secondary_indexes)
        return render(request, self.template_name, {
            'primary_indexes': primary_indexes,
            'secondary_indexes': secondary_indexes,
            'primary_images': request.session.get('primary_images', None),
            'secondary_images': request.session.get('secondary_images', None),
            'gameid': game.pk,
            'player1': p1,
            'player2': p2,
            'user': request.user.username,
        })

    def post(self, request, *args, **kwargs):
        answers = request.POST.get('answers', None)
        user = request.POST.get('user', request.user.username)
        user = Participants.objects.get(username=user)
        gameid = request.POST.get('gameid', None)
        game = Game.objects.get(pk=gameid)
        if not game.is_playing:
            game.is_playing = True
            game.save()
            while True:
                if SharedPair.objects.get(Q(sharedplayer1=user) | Q(sharedplayer2=user), game=game, is_pair=False):
                    break
        else:

        partner = None
        import ipdb; ipdb.set_trace()
        if game.player1 == user:
            partner = game.player2
        else:
            partner = game.player1
        # gameid = request.POST.get('gameid')
        # game = Game.objects.get(pk=gameid)
        # score = request.POST.get('score', 0)
        # game.score = score
        # game.is_playing = False
        # game.save()
        # return render(request, self.template_name, {})

    def setFivePrimaryIndexes(self):
        indexes = []
        while len(indexes) < 5:
            try:
                random_number = str(random.randint(0, 14))
                if random_number not in indexes:
                    indexes.append(random_number)
                # pIndex = random.randint(0, 14)
            except ValueError:
                pass
        return indexes

    def setSecondaryIndexes(self):
        secondary_indexes = []
        for i in range(5):
            indexes = []
            while len(indexes) < 3:
                try:
                    random_number = str(random.randint(0, 2))
                    if random_number not in indexes:
                        indexes.append(random_number)
                    # pIndex = random.randint(0, 14)
                except ValueError:
                    pass
            secondary_indexes.append(','.join(indexes))
        return secondary_indexes

    def que_and_ans_in_shared_pair(self, sharedpair, game):
        # Check if questions and options are set in SharedPair model
        if not sharedpair.question and not sharedpair.options:
            # Set primary images and secondary images for 5 rounds of the game
            primary_indexes = ','.join(self.setFivePrimaryIndexes())
            secondary_indexes = '|'.join(self.setSecondaryIndexes())
            sharedpair.game = game
            sharedpair.question = primary_indexes
            sharedpair.options = secondary_indexes
            sharedpair.save()
        else:
            primary_indexes = sharedpair.question
            secondary_indexes = sharedpair.options
        return primary_indexes, secondary_indexes

    def get_game(self, player1, player2):
        try:
            game = Game.objects.get(player1=player1, player2=player2, is_playing=True)
        except Exception:
            game = None
        if not game:
            try:
                game = Game.objects.get(player1=player2, player2=player1, is_playing=True)
            except Exception:
                game = None
        if not game:
            game = Game.objects.create(player1=player1, player2=player2, score=0, is_playing=True)
        return game

    def get_sharedpair(self, player1, player2):
        sharedpair = SharedPair.objects.filter(sharedplayer1=player1, sharedplayer2=player2,
                                               is_pair=True)
        if not sharedpair:
            sharedpair = SharedPair.objects.filter(sharedplayer1=player2, sharedplayer2=player1,
                                                   is_pair=True)
        return sharedpair
