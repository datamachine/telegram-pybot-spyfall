from telex.plugin import TelexPlugin
from telex.utils.decorators import group_only, pm_only
import sys, os
import random
import json
from datetime import datetime
import math


class SpyfallGame:
    game_data = {}

    def __init__(self, chat):
        self.chat = chat
        self.players = {}
        self.votes = {}
        self.start_time = None
        self.started = False
        self.spy = None
        self.location = None

    def start_game(self):
        if len(self.players) < 3:
            return "Cannot start with less than 3 players!"

        self.start_time = datetime.now()
        self.chat.send_msg("Attention {} !".format(" @".join([player.username for player in self.players.keys()])))
        self.chat.send_msg("Starting game with {} players! Majority is {} votes.".format(
                           len(self.players), self.majority))

        self._assign_roles()
        self.started = True

    def add_player(self, player):
        if self.started:
            return "Cannot join game, game already started."

        if player in self.players:
            return "{} is already in the game".format(player.username)

        if not player.username:
            return "Username required to play, check your telegram settings!"

        self.players[player] = {}
        return "{} has joined the game!".format(player.username)

    def del_player(self, player, username=None):
        if self.started:
            return "Cannot remove players from an active game"
        if username != None:
            kicked_player = next(p for p in self.players if p.username.lower() == username.lower())
            if kicked_player:
                self.players.pop(kicked_player, None)
                return "@{} has kicked @{} from the current game.".format(player.username, username)
            else:
                return "No player in game found with the username {}.".format(username)
        else:
            if player not in self.players:
                return "You're not in the game!"
            self.players.pop(player, None)
            return "Removed @{} from the game!".format(player.username)

    def vote_player(self, player, username):
        if not self.started:
            return "Cannot vote when no game is active!"

        self.unvote(player) # Unvote if necessary.

        voted = next(p for p in self.players if p.username.lower() == username.lower())
        if voted:
            try:
                self.votes[voted].append(votes)
            except KeyError:
                self.votes[voted] = []
                self.votes[voted].append(votes)
            voted_msg = "@{} has voted for @{} ".format(player.username, voted.username)
            if len(self.votes[voted]) >= majority:
                if voted is self.spy:
                    return "{}\nThey were the spy! Quick @{}, where are we!?".format(voted_msg, voted.username)
                else:
                    return "{}\nBah! They were not the spy! Everyone but @{} loses!".format(voted_msg, voted.username)
            return "@{} has voted for @{} (That makes {} votes! {} more until majority)".format(player.username, voted.username,
                len(self.votes[voted]), (self.majority - len(self.votes[voted])))

    def get_votes(self):
        if not self.started:
            return "Game not started, cannot get votes"

        text = "Current Votes (Majority is {}):\n".format(self.majority)
        for player in sorted(self.votes.keys(), key=lambda x:len(self.votes[x]), reversed=True):
            if len(self.votes[player]) > 0:
                text += "{} ({}): {}\n".format(player.username, len(self.votes[player]),
                                               ",".join([p.username for p in self.votes[player]]))
        return text

    def unvote(self, player):
        if not self.started:
            return "Cannot unvote when no game is active!"

        current_vote = None
        for voted in self.votes.keys():
            try:
                idx = self.votes[voted].index(player)
                self.votes[voted].pop(idx)
                current_vote = voted
                break
            except ValueError:
                pass

        if current_vote:
            return "@{} is no longer voting for @{}".format(player.username, current_vote.username)
        else:
            return "Cannot unvote, @{} are not voting for anyone".format(player.username)

    def status(self):
        current_players = "Current Players {}.\n{}".format(len(self.players),
                          ", ".join([player.username for player in self.players.keys()]))
        if self.started:
            return "Game is active. {}".format(current_players)
        else:
            return "Game is not active. {}".format(current_players)

    def _assign_roles(self):
        gamedata= SpyfallGame.game_data
        self.location = random.choice(gamedata.keys())
        self.spy = random.choice(self.players.keys())
        for player in self.players.keys():
            if player is not self.spy:
                role = random.choice(gamedata[self.location])
                self.players[player]["role"] = role
                player.send_msg("Location: {}\nRole: {}\nTo get the full list of locations send me: !spyfall locations".format(
                                self.location, role))
            else:
                self.players[player]["role"] = "spy"
                player.send_msg("You are the spy!\nTo get the full list of locations send me: !spyfall locations")

    @property
    def majority(self):
        return math.floor(len(self.players)/2)+1

    @staticmethod
    def load_game_data(data):
        with open(data) as data_file:
            SpyfallGame.game_data = json.load(data_file)

    @staticmethod
    def get_locations():
        return "Locations:\n{}".format("\n".join(SpyfallGame.game_data.keys()))


class SpyfallPlugin(TelexPlugin):
    patterns = {
        "^!spyfall (join)": "join_game",
        "^!spyfall (leave)": "leave_game",
        "^!spyfall (start)": "start_game",
        "^!spyfall (status)": "game_status",
        "^!spyfall (vote) @?(.+)": "vote_player",
        "^!spyfall (unvote)": "unvote",
        "^!spyfall (votes)": "get_votes",
        "^!spyfall (kick) @?(.+)": "kick_player",
        "^!spyfall (end)": "end_game",
        "^!spyfall (locations)": "game_locations",

    }

    usage = [
        "!spyfall join: Join a new game.",
        "!spyfall leave: Leave current game.",
        "!spyfall start: Start game a game with 3+ people.",
        "!spyfall kick @username: Kick player from forming game, useful if they are AFK for a long time.",
        "!spyfall vote @username: Vote for player as spy! Careful, at majority the round ends immediately",
        "!spyfall unvote: Remove your current vote",
        "!spyfall votes: List vote count on players with votes",
        "!spyfall status: Check on the status of a game in the chat room",
        "!spyfall end: End current game.",
        "!spyfall locations: Send a list of locations."
    ]

    games = {}

    def __init__(self):
        self.games = {}

        cwd = os.path.dirname(__file__)
        json_data = os.path.join(cwd, 'spyfall_data.json')
        SpyfallGame.load_game_data(json_data)

    @group_only
    def join_game(self, msg, matches):
        chat = msg.dest
        user = msg.src

        try:
            return self.games[chat].add_player(user)
        except KeyError:

            self.games[chat] = SpyfallGame(chat)
            return self.games[chat].add_player(user)

    @group_only
    def leave_game(self, msg, matches):
        chat = msg.dest
        user = msg.src

        if chat not in self.games:
            return "There is no game currently starting!"
        else:
            return self.games[chat].del_player(user)

    @group_only
    def unvote(self, msg, matches):
        chat = msg.dest
        user = msg.src

        if chat not in self.games:
            return "There is no game currently running!"
        else:
            return self.games[chat].unvote(player)


    @group_only
    def get_votes(self, msg, matches):
        chat = msg.dest
        user = msg.src

        if chat not in self.games:
            return "There is no game currently running!"
        else:
            return self.games[chat].get_votes()

    @group_only
    def kick_player(self, msg, matches):
        chat = msg.dest
        user = msg.src

        if chat not in self.games:
            return "There is no game currently starting!"
        else:
            return self.games[chat].del_player(user, username=matches.group(2))

    @group_only
    def vote_player(self, msg, matches):
        chat = msg.dest
        user = msg.src

        if chat not in self.games:
            return "There is no game currently starting!"
        else:
            return self.games[chat].vote_player(user, username=matches.group(2))

    @group_only
    def start_game(self, msg, matches):
        chat = msg.dest
        return self.games[chat].start_game()

    @group_only
    def end_game(self, msg, matches):
        chat = msg.dest

        if chat in self.games:
            self.games.pop(chat, None)
            return "Game ended!"
        else:
            return "Game has not started!"

    @group_only
    def game_status(self, msg, matches):
        chat = msg.dest

        if chat in self.games:
            return self.games[chat].status()
        else:
            return "There is no game currently"

    @pm_only
    def game_locations(self, msg, matches):
        return SpyfallGame.get_locations()
