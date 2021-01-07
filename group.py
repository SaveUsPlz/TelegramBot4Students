class Group:
    def __init__(self, groupid: str, name: str):
        self.id = groupid
        self.name = name

    def __str__(self) -> str:
        return self.id + ": " + self.name

    def __repr__(self):
        return str(self)
