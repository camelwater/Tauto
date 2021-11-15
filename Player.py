
class Player:
    def __init__(self, id, name, rating=None):
        self.id = id
        self.name = name
        self.rating = rating
    
    def getID(self):
        return self.id
    
    def getName(self):
        return self.name
    
    def getRating(self):
        return self.rating or 0

    def __str__(self):
        return f"{self.id}. {self.name} (rating={self.rating or 'Unrated'})"

    def __repr__(self):
        return f"Player(id={self.id}, name={self.name}, rating={self.rating})"
    
    def __hash__(self):
        return hash((self.__class__, self.id))