class FakePool():

    def __init__(self, fake_query):
        self.responce = fake_query

    def getconn(self):
        return FakeConnection(self.responce)

    def putconn(self, connection=None):
        pass


class FakeConnection():

    def __init__(self, fake_query):
        self.responce = fake_query

    def cursor(self, cursor_factory=None):
        return FakeCursor(self.responce)

    def commit(self):
        pass

    def rollback(self):
        pass


class FakeCursor():

    def __init__(self, fake_query):
        self.responce = fake_query

    def execute(self, query, data=None):
        pass

    def close(self):
        pass

    def fetchone(self):
        return self.responce

    def fetchall(self):
        return self.responce
