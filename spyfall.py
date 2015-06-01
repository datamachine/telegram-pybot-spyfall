from telegrambot.plugin import TelegramPlugin
from telegrambot.utils.decorators import group_only, pm_only
import sys
import os
import random
import json
import sys


class SpyfallPlugin(TelegramPlugin):
    patterns = {
        "^!spyfall (join)": "join_game",
        "^!spyfall (start)": "start_game",
        "^!spyfall (status)": "game_status",
        "^!spyfall (end)": "end_game",
        "^!spyfall (locations)": "game_locations",

    }

    usage = [
        "!spyfall join: Join a new game.",
        "!spyfall start: Start game a game with 3+ people.",
        "!spyfall status: Check on the status of a game in the chat room",
        "!spyfall end: End current game.",
        "!spyfall locations: Send a list of locations."
    ]

    games = {}

    @group_only
    def join_game(self, msg, matches):
        chat_id = msg.dest.id
        user_id = msg.src.username
        peer_id = msg.src
        joined_game = "%s has joined the game " % user_id

        try:
            if chat_id in self.games:
                if self.games[chat_id]['isStarted'] == True:
                    return "Cannot join game, game already started."
                else:
                   # go herea
                   if peer_id in self.games[chat_id]['players']:
                       return "You've already joined the game!"
                   else:
                       self.games[chat_id]['players'][peer_id] = {}
                       return joined_game
            else:
                self.create_game(msg)
                self.games[chat_id]['players'][peer_id] = {}
                return joined_game

        except KeyError:
            self.create_game(msg)
            self.games[chat_id]['players'][peer_id] = {}
            return joined_game

    def create_game(self, msg):
       chat_id = msg.dest.id

       if chat_id in self.games:
           return "Game already created"
       else:
           self.games[chat_id] = {
                   'isStarted': False,
                   'players': {}
                }
           return "Created Game"

    @group_only
    def start_game(self, msg, matches):
        chat_id = msg.dest.id

        if self.games[chat_id]['isStarted']:
            return "Game already started."
        else:
            # get our role
            category = self.get_category(msg, "random")
            get_spy = random.choice(list(self.games[chat_id]['players'].keys()))
            get_first = random.choice(list(self.games[chat_id]['players'].keys()))

            if len(self.games[chat_id]['players'].keys()) >= 3:
                for k in self.games[chat_id]['players']:

                    if k.id == get_spy.id:
                        self.games[chat_id]['players'][k]['role'] = "spy"
                        k.send_msg("You're a spy!")
                    else:
                        role = self.get_role(msg, category)
                        self.games[chat_id]['players'][k]['role'] = role
                        user_data = ("You're a {} \nLocation: {}".format(role, category))
                        k.send_msg(user_data)


                # set game to started
                self.games[chat_id]['isStarted'] = True
                game_started = ("Game started: First up: {}\nAttention: {}".format(get_first.username,
                    " , ".join(["@{}".format(player.username) for player in self.games[chat_id]['players'].keys()])))

                return game_started
            else:
                players_needed = ("Not enough to start, need {}".format(3 - len(self.games[chat_id]['players'].keys())))
                return players_needed

    @group_only
    def end_game(self, msg, matches):
        chat_id = msg.dest.id

        try:
            if any(self.games[chat_id]):
                if self.games[chat_id]['isStarted']:
                   self.games.pop(chat_id, None)
                   return "Game stopped"
                else:
                    return "Game has not started"
        except KeyError:
            return "Game has not started"

    @group_only
    def game_status(self, msg, matches):
        chat_id = msg.dest.id

        #try:
        if chat_id in self.games:
            current_players = "Current Players {}.\n{}".format(len(self.games[chat_id]['players'].keys()),
                               ", ".join([player.username for player in self.games[chat_id]['players'].keys()]))
            if self.games[chat_id]['isStarted']:
                return "Game is active. {}".format(current_players)
            elif self.games[chat_id]['isStarted'] == False:
                return "Game is not active. {}.".format(current_players)

        else:
            return "There is no game currently"
        #except:
        #    return "There is no game currently."

    def get_role(self, msg, category):

        cwd = os.path.dirname(__file__)
        json_data = os.path.join(cwd, 'spyfall_data.json')
        # load our json
        with open(json_data) as data_file:    
                data = json.load(data_file)

        role = random.choice(list(data[category]))

        return role

    def get_category(self, msg, type):
        cwd = os.path.dirname(__file__)
        json_data = os.path.join(cwd, 'spyfall_data.json')
        category = None

        # load our json
        with open(json_data) as data_file:
                data = json.load(data_file)

        if type == "random":
            category = random.choice(list(data.keys()))
        else:
            category = data.keys()

        return category

    @pm_only
    def game_locations(self, msg, matches):
        msg.src.send_msg("Locations:\n{}".format("\n".join(self.get_category(msg, "all"))))
