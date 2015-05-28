import plugintypes
import sys
import os
import random
import json
import sys


class SpyfallPlugin(plugintypes.TelegramPlugin):
    patterns = {
        "^!spyfall (games)": "list_games",
        "^!spyfall (join)": "join_game",
        "^!spyfall (start)": "start_game",
        "^!spyfall (status)": "game_status",
        "^!spyfall (end)": "end_game",
    }

    usage = [
        "!spyfall games: List all the games!",
        "!spyfall join: Join a new game.",
        "!spyfall start: Start game a game with 3+ people.",
        "!spyfall status: Check on the status of a game in the chat room",
        "!spyfall end: End current game.",
    ]

    games = {}
    game_data = {
                    'isStarted': False,
                    'players': {}
                }

    def join_game(self, msg, matches):
        chat_id = msg.dest.id
        user_id = msg.src.username
        peer_id = msg.src
        joined_game = "%s has joined the game " % user_id

        try:

            if chat_id in self.games:
                if self.games[chat_id]['isStarted'] == True:
                    return "Cannot join game, game already started"
                else:
                   # go herea
                   if peer_id in self.games[chat_id]:
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
           # add user to the chat_id
           # games[chat_id][user] = role
       else:
           self.games[chat_id] = self.game_data

       return "created game" 

    def start_game(self, msg, matches):
        chat_id = msg.dest.id

        if self.games[chat_id]['isStarted'] == True:
            return "Game already started"
        else:
            # get our role
            category = self.get_category(msg)
            get_spy = random.choice(list(self.games[chat_id]['players'].keys()))

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

            return "Game started"

    def end_game(self, msg, matches):
        chat_id = msg.dest.id

        try: 
            if any(self.games[chat_id]):
                if self.games[chat_id]['isStarted'] == True:
                   self.games.pop(chat_id, None)
                   return "Game stopped"
                else:
                    return "Game has not started"
        except KeyError:
            return "Game has not started"

    def game_status(self, msg, matches):
        chat_id = msg.dest.id

        try:
            if chat_id in self.games:
                if self.games[chat_id]['isStarted'] == True:
                    return "Game is active."

            else:
                return "There is no game currently."
        except:
            return "There is no game currently."

    def get_role(self, msg, category):

        cwd = os.path.dirname(__file__)
        json_data = os.path.join(cwd, 'spyfall_data.json')
        # load our json
        with open(json_data) as data_file:    
                data = json.load(data_file)

        role = random.choice(list(data[category]))

        return role

    def get_category(self, msg):
        cwd = os.path.dirname(__file__)
        json_data = os.path.join(cwd, 'spyfall_data.json')
        # load our json
        with open(json_data) as data_file:
                data = json.load(data_file)

        category = random.choice(list(data.keys()))
        return category

    def list_games(self, msg, matches):
        game_list = [] 

        for k in self.games.keys():
            game_list.append(str(k))

        if any(self.games):
            #returns the game list
            return "Game: \n".join(game_list)
        else: 
            return "No games"
