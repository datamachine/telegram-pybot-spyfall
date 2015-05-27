import plugintypes


class SpyfallPlugin(plugintypes.TelegramPlugin):
    patterns = [
        "^!spyfall (join)", "join_game",
        "^!spyfall (start)", "start_game",
        "^!spyfall (end)", "end_game",

    ]

    usage = [
        "!spyfall join: Join a new game.",
        "!spyfall start: Start game a game with 3+ people.",
        "!spyfall end: End current game.",
    ]

    def join_game(self, msg, matches):
        pass

    def start_game(self, msg, matches):
        pass

    def end_game(self, msg, matches):
        pass
