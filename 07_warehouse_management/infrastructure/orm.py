from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class ProductORM(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)


class OrderORM(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    status = Column(String)


class ManagerORM(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True)


order_product_assocoations = Table(
    "order_product_assocoations",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id")),
    Column("product_id", ForeignKey("products.id")),
)

manager_order_assocoations = Table(
    "manager_order_assocoations",
    Base.metadata,
    Column("manager_id", ForeignKey("managers.id")),
    Column("order_id", ForeignKey("orders.id")),
)

OrderORM.products = relationship("ProductORM", secondary=order_product_assocoations)
ManagerORM.ordser = relationship("OrderORM", secondary=manager_order_assocoations)
