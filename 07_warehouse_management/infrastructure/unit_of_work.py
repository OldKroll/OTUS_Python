from domain.unit_of_work import UnitOfWork
from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
