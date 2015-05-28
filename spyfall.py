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
        "^!spyfall (end)": "end_game",
    }

    usage = [
        "!spyfall join: Join a new game.",
        "!spyfall start: Start game a game with 3+ people.",
        "!spyfall end: End current game.",
    ]

    games = {}
    game_data = {
                    'isStarted': False,
                    'players': {}
                }

    player_data = {
                    'isSpy': False,
                    'role': 'none',
                  }

    def join_game(self, msg, matches):
        chat_id = msg.dest.id
        user_id = msg.src.username
        peer_id = msg.src
        joined_game = "%s has joined the game " % user_id

        print(peer_id)

        def join_game():
            self.games[chat_id]['players'][peer_id] = self.player_data

        if chat_id in self.games:
            # go herea
            if peer_id in self.games[chat_id]:
                return "You've already joined the game!"
            else:
                join_game()
                return joined_game 

        else:
            self.create_game(msg)
            join_game()
            return joined_game

        return

    def create_game(self, msg):
       chat_id = msg.dest.id

       if chat_id in self.games:
           # add user to the chat_id
           # games[chat_id][user] = role
           print("We got here!")
       else:
           self.games[chat_id] = self.game_data

       return "created game" 

    def start_game(self, msg, matches):
        chat_id = msg.dest.id
        
        # get our role

        category = self.get_category(msg)

        for k in self.games[chat_id]['players']:
            role = self.get_role(msg, category)
            self.games[chat_id]['players'][k]['role'] = role

        get_spy = random.sample(self.games[chat_id]['players'].keys(),1)

        for k in self.games[chat_id]['players']:
            if k.id == get_spy:
                self.games[chat_id]['players'][k.id]['isSpy'] = True
                k.send_msg("You're a spy!")
            else:
                role = self.games[chat_id]['players'][k]['role']
                user_data = ("You're a {} \nLocation: {}".format(role, category))
                k.send_msg(user_data)

        return "game started"

    def end_game(self, msg):
        self.games.pop(chat_id, None)
        return "game stopped"

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
