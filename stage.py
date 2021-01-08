class Stage:
    def __init__(self, user_id: str, step: str, params: dict = {}) -> None:
        self.user_id = user_id
        self.step = step
        self.params = params

    def __str__(self) -> str:
        return "Stage " + self.step + ", " + str(self.params)

