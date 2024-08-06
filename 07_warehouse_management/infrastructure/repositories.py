from typing import List

from domain.enums import OrderStatus
from domain.exceptions import ItemNotFoundException
from domain.models import Manager, Order, Product
from domain.repositories import ManagerRepository, OrderRepository, ProductRepository
from infrastructure.orm import ManagerORM, OrderORM, ProductORM
from sqlalchemy import exc
from sqlalchemy.orm import Session


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product):
        product_orm = ProductORM(
            name=product.name, quantity=product.quantity, price=product.price
        )
        self.session.add(product_orm)
        self.session.flush()
        product.id = product_orm.id

    def get(self, product_id: int) -> Product:
        try:
            product_orm = self.session.query(ProductORM).filter_by(id=product_id).one()
        except exc.NoResultFound:
            raise ItemNotFoundException(
                message=f"Product with id {product_id} does not exists", error_code=1337
            )
        return Product(
            id=product_orm.id,
            name=product_orm.name,
            quantity=product_orm.quantity,
            price=product_orm.price,
        )

    def list(self) -> List[Product]:
        products_orm = self.session.query(ProductORM).all()
        return [
            Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
            for p in products_orm
        ]


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order):
        order_orm = OrderORM()
        order_orm.products = [
            self.session.query(ProductORM).filter_by(id=p.id).one()
            for p in order.products
        ]
        self.session.add(order_orm)
        self.session.flush()
        order.id = order_orm.id

    def get(self, order_id: int) -> Order:
        try:
            order_orm = self.session.query(OrderORM).filter_by(id=order_id).one()
        except exc.NoResultFound:
            raise ItemNotFoundException(
                message=f"Order with id {order_id} does not exists", error_code=1337
            )
        products = [
            Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
            for p in order_orm.products
        ]
        return Order(id=order_orm.id, status=order_orm.status, products=products)

    def set_order_status(self, order_id: int, status: OrderStatus) -> Order:
        self.session.query(OrderORM).filter_by(id=order_id).update(
            {"status": str(status)}
        )

    def list(self) -> List[Product]:
        orders_orm = self.session.query(OrderORM).all()
        orders = []
        for order_orm in orders_orm:
            products = [
                Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
                for p in order_orm.products
            ]
            orders.append(Order(id=order_orm.id, products=products))
        return orders


class SqlAlchemyManagerRepository(ManagerRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, manager: Manager):
        manager_orm = ManagerORM()
        manager_orm.orders = [
            self.session.query(OrderORM).filter_by(id=p.id).one()
            for p in manager.orders
        ]
        self.session.add(manager_orm)
        self.session.flush()
        manager.id = manager_orm.id

    def get(self, manager_id: int) -> Manager:
        try:
            manager_orm = self.session.query(ManagerORM).filter_by(id=manager_id).one()
        except exc.NoResultFound:
            raise ItemNotFoundException(
                message=f"Manager with id {manager_id} does not exists", error_code=1337
            )
        orders = [
            Order(
                id=o.id,
                status=o.status,
                products=[
                    Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
                    for p in o.products
                ],
            )
            for o in manager_orm.orders
        ]
        return Manager(id=manager_orm.id, orders=orders)

    def list(self) -> List[Manager]:
        managers_orm = self.session.query(ManagerORM).all()
        managers = []
        for manager_orm in managers_orm:
            orders = [
                Manager(
                    id=p.id,
                    orders=[
                        Order(
                            id=o.id,
                            status=o.status,
                            products=[
                                Product(
                                    id=p.id,
                                    name=p.name,
                                    quantity=p.quantity,
                                    price=p.price,
                                )
                                for p in o.products
                            ],
                        )
                        for o in manager_orm.orders
                    ],
                )
                for p in manager_orm.products
            ]
            managers.append(Manager(id=manager_orm.id, orders=orders))
        return managers
