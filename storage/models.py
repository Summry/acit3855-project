from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class Delivery(Base):
    __tablename__ = 'delivery_report'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    delivery_id = mapped_column(String(250), nullable=False)
    user_id = mapped_column(String(250), nullable=False)
    item_quantity = mapped_column(Integer, nullable=False)
    requested_date = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now())
    trace_id = mapped_column(String(250), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'delivery_id': self.delivery_id,
            'user_id': self.user_id,
            'item_quantity': self.item_quantity,
            'requested_date': self.requested_date,
            'trace_id': self.trace_id
        }


class Schedule(Base):
    __tablename__ = 'schedule_report'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_id = mapped_column(String(250), nullable=False)
    user_id = mapped_column(String(250), nullable=False)
    number_of_deliveries = mapped_column(Integer, nullable=False)
    created_date = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now())
    trace_id = mapped_column(String(250), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'user_id': self.user_id,
            'number_of_deliveries': self.number_of_deliveries,
            'created_date': self.created_date,
            'trace_id': self.trace_id
        }
