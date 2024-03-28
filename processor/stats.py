from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Stats(Base):
    __tablename__ = 'delishery_stats'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    num_of_deliveries = mapped_column(Integer, nullable=False)
    num_of_schedules = mapped_column(Integer, nullable=False)
    total_delivery_items = mapped_column(Integer, nullable=False)
    total_scheduled_deliveries = mapped_column(Integer, nullable=False)
    last_updated = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now())

    def to_dict(self):
        return {
            'id': self.id,
            'num_of_deliveries': self.num_of_deliveries,
            'num_of_schedules': self.num_of_schedules,
            'total_delivery_items': self.total_delivery_items,
            'total_scheduled_deliveries': self.total_scheduled_deliveries,
            'last_updated': self.last_updated
        }
