from typing import List

from domain.enums import OrderStatus
from domain.models import Manager, Order, Product
from domain.repositories import ManagerRepository, OrderRepository, ProductRepository


class WarehouseService:
    def __init__(
        self,
        product_repo: ProductRepository,
        order_repo: OrderRepository,
        manager_repo: ManagerRepository,
    ):
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.manager_repo = manager_repo

    def create_product(self, name: str, quantity: int, price: float) -> Product:
        product = Product(id=None, name=name, quantity=quantity, price=price)
        self.product_repo.add(product)
        return product

    def get_product(self, product_id: int):
        return self.product_repo.get(product_id)

    def create_order(self, products: List[Product]) -> Order:
        order = Order(id=None, status=OrderStatus.CREATED, products=products)
        self.order_repo.add(order)
        return order

    def get_order(self, order_id: int) -> Order:
        return self.order_repo.get(order_id)

    def create_manager(self, orders: List[Order]) -> Manager:
        manager = Manager(id=None, orders=orders)
        self.manager_repo.add(manager)
        return manager

    def get_manager(self, manager_id: int):
        return self.manager_repo.get(manager_id)

    def set_order_status(self, order: Order, status: OrderStatus) -> Order:
        self.order_repo.set_order_status(order.id, status)
        order.status = status
        return order
