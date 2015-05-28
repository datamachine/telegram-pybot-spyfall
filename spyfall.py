import plugintypes
import sys
import os
import random
import json
import sys



class SpyfallPlugin(plugintypes.TelegramPlugin):
    patterns = [
        "^!spyfall$",
        "^!spyfall (join)", "join_game",
        "^!spyfall (start)", "start_game",
        "^!spyfall (end)", "end_game",
    ]

    usage = [
        "!spyfall join: Join a new game.",
        "!spyfall start: Start game a game with 3+ people.",
        "!spyfall end: End current game.",
    ]

    games = {}
    game_data = {
                    'isStarted': 'false',
                    'players': {}
                }

    player_data = {
                    'isSpy': 'false',
                    'role': 'none',
                  }

    def run(self, msg, matches):

        if matches.group(0) == "!spyfall":
            return self.list_games(msg)

        command = matches.group(1)

        if command == "join":
            return self.join_game(msg)

        if command == "start":
            return self.start_game(msg)

        if command == "end":
            return self.end_game(msg)

    def join_game(self, msg):
        chat_id = msg.dest.id
        user_id = msg.src.username
        joined_game = u"%s has joined the game " % user_id

        def join_game():
            self.games[chat_id]['players'][user_id] = self.player_data

        if chat_id in self.games:
            # go herea
            if user_id in self.games[chat_id]:
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
           print("We created a game?")

       return "created game" 

    def start_game(self, msg):
        chat_id = msg.dest.id
        
        # get our role
        role = self.get_role(msg)

        print(role)
        
        for k in self.games[chat_id]['players']:
            print(k)
            # append the role of the user
            # create a spy

        return "game started"

    def end_game(self, msg):
        self.games.pop(chat_id, None)
        return "game stopped"

    def get_role(self, msg):

        cwd = os.path.dirname(__file__)
        json_data = os.path.join(cwd, 'spyfall_data.json')
        # load our json
        with open(json_data) as data_file:    
                data = json.load(data_file)

        category = random.choice(list(data.keys()))
        role = random.choice(list(data[category]))

        return role 

    def list_games(self, msg):
        game_list = [] 

        for k in self.games.keys():
            game_list.append(str(k))

        if any(self.games):
            #returns the game list
            return "Game: \n".join(game_list)
        else: 
            return "No games"
