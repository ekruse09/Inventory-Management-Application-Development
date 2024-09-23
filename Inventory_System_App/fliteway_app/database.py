# database.py
# Elijah Kruse
# 07/09/2024

'''
Inputs:
- SQLAlchemy database URL
- Definitions for database models (Item, Order, OrderItem, OnHand, Expended, OrderHistory)
- SessionLocal class for handling database sessions
- SQLAlchemy engine for connecting to the SQLite database

Outputs:
- Initialized SQLite database with the specified tables and relationships

Side Effects:
- Creates a SQLite database file (if it doesn't exist) and initializes it with the defined tables
- Provides methods for creating orders, adding items to orders, moving items from ordered to on hand, and decrementing quantities
- Logs all items ever ordered in a read-only OrderHistory table

SQLite is not recommended for heavy multi-user use. We shouldn't have a problem with only a few accessing it at a time.
'''

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func

# SQLite database file path
SQLALCHEMY_DATABASE_URL = "sqlite:///./inventory.db"

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a SessionLocal class for handling sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative ORM models
Base = declarative_base()


# History of all orders
class OrderHistory(Base):
    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    part_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    order_notes = Column(String, nullable=False)
    purchase_link = Column(String, nullable=False)
    order_location = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    ordered_by = Column(String, nullable=False)

    price_per_unit = Column(Float, nullable=False)


# Currently Placed Orders
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    part_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    order_notes = Column(String, nullable=False)
    order_location = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    ordered_by = Column(String, nullable=False)

    purchase_link = Column(String, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    

    # Creating a new order
    def create_order(cls, session, part_number, description, manufacturer, quantity, total_price, ordered_by="", order_date=func.date(func.now()), order_location="", order_notes="", purchase_link=""):
        new_order = cls(
            part_number=part_number,
            description=description,
            manufacturer=manufacturer,
            quantity=quantity,
            total_price=total_price,
            price_per_unit=float(total_price)/int(quantity),
            order_date=order_date,
            order_location=order_location,
            ordered_by=ordered_by,      # Should be account credentials in the future
            order_notes=order_notes,
            purchase_link=purchase_link
        )
        session.add(new_order)
        session.commit()
        return new_order

    # Editing an existing order
    def edit_order(self, session, part_number=None, description=None, manufacturer=None, quantity=None, total_price=None, order_location=None, order_notes=None, purchase_link=None):
        if part_number:
            self.part_number=part_number
        if description:
            self.description=description
        if manufacturer:
            self.manufacturer=manufacturer
        if order_location:
            self.order_location=order_location
        if order_notes:
            self.order_notes=order_notes
        if purchase_link:
            self.purchase_link=purchase_link

        if quantity and total_price:
            self.quantity=quantity
            self.total_price=total_price
            self.price_per_unit=total_price/quantity
        elif total_price:
            self.total_price=total_price
            self.price_per_unit=total_price/self.quantity
        elif quantity:
            self.quantity=quantity
            self.price_per_unit=self.total_price/quantity

        session.commit()

    # Delete an existing order
    def delete_order(self, session):
        session.delete(self)
        session.commit()

    def deliver(self, session, inventory_location, updated_by="", updated_date=func.date(func.now())):
        on_hand_item = session.query(OnHand).filter_by(part_number=self.part_number).first()
        if on_hand_item:
            on_hand_item.quantity += self.quantity
            on_hand_item.updated_by=updated_by    # Should be account credentials in the future
            on_hand_item.updated_date=updated_date
        else:
            on_hand_item = OnHand(
                part_number=self.part_number,
                description=self.description,
                manufacturer=self.manufacturer,
                quantity=self.quantity,
                price_per_unit=self.price_per_unit,
                location=inventory_location,
                updated_on=updated_date,
                updated_by=updated_by      # Should be account credentials in the future
            )
            session.add(on_hand_item)

        order_history_item = OrderHistory(
            part_number=self.part_number,
            description=self.description,
            manufacturer=self.manufacturer,
            quantity=self.quantity,
            total_price=self.total_price,
            price_per_unit=self.price_per_unit,
            order_date=self.order_date,
            order_location=self.order_location,
            ordered_by=self.ordered_by,
            order_notes=self.order_notes,
            purchase_link=self.purchase_link
        )
        session.add(order_history_item)

        session.delete(self)
        
        session.commit()


# Items we currently have
class OnHand(Base):
    __tablename__ = "on_hand"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    part_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    inventory_notes = Column(String, nullable=True)
    updated_on = Column(Date, nullable=False)
    updated_by = Column(String, nullable=False)

    def decrement_quantity(self, session, quantity, updated_by="", usage_date=func.date(func.now()), usage_notes="", project=""):
        if self.quantity < quantity:
            raise ValueError("Not enough quantity on hand to expend")
        
        self.quantity -= quantity
        self.updated_on = func.now()
        self.updated_by = updated_by

        expended_item = Expended(
            part_number=self.part_number,
            description=self.description,
            manufacturer = self.manufacturer,
            quantity=quantity,
            usage_date=usage_date,
            updated_by=updated_by,      # Should be account credentials in the future
            project=project,
            price_per_unit=self.item.price_per_unit,
            total_price=quantity*self.item.price_per_unit,
            usage_notes=usage_notes
        )
        session.add(expended_item)
        session.commit()


# History of all items to pass through the system
class Expended(Base):
    __tablename__ = "expended"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    part_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    project = Column(String, nullable=False)
    usage_notes = Column(String, nullable=False)
    usage_date = Column(Date, nullable=False)
    updated_by = Column(String, nullable=False)
    
    price_per_unit = Column(Float, nullable=False)
    
    

# Create tables in the database
Base.metadata.create_all(bind=engine)
