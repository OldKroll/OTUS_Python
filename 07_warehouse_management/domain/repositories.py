from abc import ABC, abstractmethod
from typing import List

from domain.enums import OrderStatus
from domain.models import Manager, Order, Product


class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        pass

    @abstractmethod
    def get(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def list(self) -> List[Product]:
        pass


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order):
        pass

    @abstractmethod
    def get(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def set_order_status(self, order_id: int, status: OrderStatus) -> Order:
        pass

    @abstractmethod
    def list(self) -> List[Order]:
        pass


class ManagerRepository(ABC):
    @abstractmethod
    def add(self, manager: Manager):
        pass

    @abstractmethod
    def get(self, manager_id: int) -> Manager:
        pass

    @abstractmethod
    def list(self) -> List[Manager]:
        pass
