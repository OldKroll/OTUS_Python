from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from warehouse_management.domain.models import Product
from warehouse_management.domain.services import WarehouseService
from warehouse_management.infrastructure.database import DATABASE_URL
from warehouse_management.infrastructure.orm import Base, OrderORM, ProductORM
from warehouse_management.infrastructure.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyProductRepository,
)
from warehouse_management.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def main():
    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)

    uow = SqlAlchemyUnitOfWork(session)

    warehouse_service = WarehouseService(product_repo, order_repo)
    with uow:
        new_product = warehouse_service.create_product(
            name="test1", quntity=1, price=100
        )
        uow.commit()
        print(f"create product: {new_product}")
        # todo add some actions


if __name__ == "__main__":
    main()
