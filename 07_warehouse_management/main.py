from domain.exceptions import ItemNotFoundException
from domain.models import Product
from domain.services import WarehouseService
from infrastructure.database import DATABASE_URL
from infrastructure.orm import Base, OrderORM, ProductORM
from infrastructure.repositories import (
    SqlAlchemyManagerRepository,
    SqlAlchemyOrderRepository,
    SqlAlchemyProductRepository,
)
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def main():
    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    manager_repo = SqlAlchemyManagerRepository(session)

    warehouse_service = WarehouseService(product_repo, order_repo, manager_repo)

    with SqlAlchemyUnitOfWork(session) as unit:
        new_product = warehouse_service.create_product(
            name="test1", quantity=1, price=100
        )
        unit.commit()
        print(f"create product: {new_product}")
        new_order = warehouse_service.create_order([new_product])
        unit.commit()
        print(f"create order: {new_order}")
        new_manager = warehouse_service.create_manager([new_order])
        unit.commit()
        print(f"create manager: {new_manager}")
        updated_order = warehouse_service.set_order_status(new_order, "completed")
        unit.commit()
        print(f"updated order: {updated_order}")
        print(f"get order: {warehouse_service.get_order(new_order.id)}")
        try:
            warehouse_service.get_order(999999)
        except ItemNotFoundException as e:
            print(f"get order expected failure: {str(e)}")

        new_product = warehouse_service.create_product(
            name="test2", quantity=2, price=200
        )
        unit.commit()
        print(f"create product: {new_product}")
        unit.rollback()
        print("rollback")


if __name__ == "__main__":
    main()
