import json

from db_conn import DBConnection
from stage import Stage


class StageRepository:
    def __init__(self, conn: DBConnection) -> None:
        self.conn = conn

    def get_stage(self, user_id: str) -> Stage:
        c = self.conn.conn().cursor()
        c.execute("select user_id, step, params from stage where user_id = :id", {"id": user_id})
        results = c.fetchone()
        c.close()
        if results is None:
            return None
        params = json.loads(results[2])
        stage = Stage(results[0], results[1], params)
        return stage

    def set_stage(self, stage: Stage) -> Stage:
        existing = self.get_stage(stage.user_id)
        params_str = json.dumps(stage.params)
        if existing is None:
            c = self.conn.conn().cursor()
            c.execute("insert into stage(user_id, step, params) values(:id, :step, :params)",
                      {"id": stage.user_id, "step": stage.step, "params": params_str})
            c.close()
            self.conn.conn().commit()
        else:
            c = self.conn.conn().cursor()
            c.execute("update stage set step = :step, params = :params where user_id = :id",
                      {"id": stage.user_id, "step": stage.step, "params": params_str})
            c.close()
            self.conn.conn().commit()

    def set_stage_data(self, user_id: str, step: str, params: dict = {}):
        self.set_stage(Stage(user_id, step, params))

    def delete_stage(self, stage_id):
        c = self.conn.conn().cursor()
        c.execute("delete from stage where user_id = :id",
                  {"id": stage_id})
        c.close()
        self.conn.conn().commit()
