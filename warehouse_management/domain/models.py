from dataclasses import dataclass, field
from typing import List

from domain.enums import OrderStatus


@dataclass
class Product:
    id: int
    name: str
    quantity: int
    price: float


@dataclass
class Order:
    id: int
    status: OrderStatus
    products: List[Product] = field(default_factory=list)

    def add_product(self, product: Product):
        self.products.append(product)


@dataclass
class Manager:
    id: int
    orders: List[Order] = field(default_factory=list)

    def add_order(self, order: Order):
        self.orders.append(order)

    def set_order_status(self, order_id: int, status: OrderStatus):
        index = self.orders.index(lambda ord: ord.id == order_id)
        if index == -1:
            raise ValueError("Not found")
        self.orders[index].status = status
