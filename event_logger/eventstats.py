from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class EventStats(Base):
    __tablename__ = 'event_log_stats'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    message = mapped_column(String(250), nullable=False)
    code = mapped_column(String(4), nullable=False) # message code
    date_created = mapped_column(DateTime, nullable=False, default=lambda: datetime.now())

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'code': self.code, # i.e., "0001", "0002", "0003", "0004"
            'date_created': self.date_created
        }
