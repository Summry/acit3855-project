from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class Anomaly(Base):
    """ Anomaly """

    __tablename__ = "anomaly"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id = mapped_column(String(250), nullable=False)
    trace_id = mapped_column(String(250), nullable=False)
    event_type = mapped_column(String(100), nullable=False)
    anomaly_type = mapped_column(String(100), nullable=False)
    description = mapped_column(String(250), nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=lambda: datetime.now())

    def to_dict(self):
        """ Dictionary Representation of an anomaly """
        dict = {}
        dict['id'] = self.id
        dict['event_id'] = self.event_id
        dict['trace_id'] = self.trace_id
        dict['event_type'] = self.event_type
        dict['anomaly_type'] = self.anomaly_type
        dict['description'] = self.description

        return dict