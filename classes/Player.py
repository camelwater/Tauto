import utils.discord_utils as discord_utils

class Player:
    def __init__(self, id, discord_id, name, rating=None):
        self.id = id
        self.name = name
        self.discord_id = discord_id
        self.rating = rating
    
    def getID(self):
        return self.id
    
    def getDiscordID(self):
        return self.discord_id or 0
    
    def getName(self):
        return self.name
    
    def get_displayName(self, discord=True):
        if not discord: return f"{self.name}"
        return f"{self.name}" + (f" - <@{self.discord_id}>" if self.discord_id else "")
    
    def getRating(self):
        return self.rating or 0

    def get_full_display(self, discord=False):
        return self.__str__(discord=discord)

    def __str__(self, discord=False):
        return f"{self.id}. {self.get_displayName(discord=discord)} (rating={self.rating or 'Unrated'})"

    def __repr__(self):
        return f"Player(id={self.id}, disc_id={self.discord_id}, name={self.name}, rating={self.rating})"
    
    def __hash__(self):
        return hash((self.__class__, self.id))