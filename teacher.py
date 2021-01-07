class Teacher:
    def __init__(self, userid):
        self.id = userid
        self.confirmed = False
        self.confirm_code = ""
        self.groups = []
