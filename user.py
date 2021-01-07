class User:
    def __init__(self, userid):
        self.id = userid
        self.name = ""
        self.type = "STUDENT"

    def __str__(self) -> str:
        return self.id + ": " + self.name + ", " + self.type


