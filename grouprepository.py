from db_conn import DBConnection
from group import Group


class GroupRepository:
    def __init__(self, conn: DBConnection) -> None:
        self.conn = conn

    def find_group(self, groupid) -> Group:
        c = self.conn.conn().cursor()
        c.execute("select id, name from groups where id = :id", {"id": groupid})
        results = c.fetchone()
        # print(results)
        c.close()
        if results is None:
            return None
        group = Group(results[0], results[1])
        return group

    def create_group(self, group: Group):
        c = self.conn.conn().cursor()
        c.execute("insert into groups(id, name) values(:id, :name)",
                  {"id": group.id, "name": group.name})
        c.close()
        self.conn.conn().commit()

    def list_group(self):
        c = self.conn.conn().cursor()
        c.execute("select g.id, g.name from groups g "
                  "order by g.name", {})
        results = c.fetchall()
        groups = []
        for i in results:
            groups.append(Group(i[0], i[1]))
        c.close()
        return groups
