import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class AsDictMixin:
    """
    Adds asdict method, which returns instance converted to dictionary
    """
    def asdict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }


class Currency(AsDictMixin, Base):
    __tablename__ = 'currency'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class Rate(AsDictMixin, Base):
    __tablename__ = 'rate'
    id = sa.Column(sa.Integer, primary_key=True)
    currency_id = sa.Column(None, sa.ForeignKey('currency.id'))
    date = sa.Column(sa.Date)
    rate = sa.Column(sa.Float)
    volume = sa.Column(sa.Float)


def create_tables(engine):
    Base.metadata.create_all(engine)
