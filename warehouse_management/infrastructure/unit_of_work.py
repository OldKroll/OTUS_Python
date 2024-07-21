from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:

    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def commit(self):
        self.session.commit()
