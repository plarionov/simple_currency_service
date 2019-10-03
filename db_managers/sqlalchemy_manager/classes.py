import datetime as _dt
import typing as _t

from sqlalchemy import and_, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy_pagination import paginate, Page
from sqlalchemy_utils import database_exists, create_database

from classes import CandlesResponse
from constants import INDENT_DAYS
from db_managers.interfaces import DbManagerInterface
from db_managers.sqlalchemy_manager.models import create_tables, \
    Currency, Rate


class SqlAlchemyDbManagerImp(DbManagerInterface):
    """
    SqlAlchemy implementation
    """

    def __init__(self, db_engine):
        self._engine = db_engine
        if not database_exists(self._engine.url):
            create_database(self._engine.url)
        self.conn = self._engine.connect()
        self._Session = sessionmaker(bind=db_engine)
        try:
            create_tables(db_engine)
        except (exc.ArgumentError, exc.OperationalError) as e:
            raise e

    async def create_currencies(self, names: _t.Iterable[str]):
        session = self._Session()

        try:
            session.add_all((
                Currency(name=name) for name in names
            ))
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    async def get_currencies_data(
            self,
            paginated: bool = True,
            page: int = 1,
            page_size: int = 1) -> dict:
        session = self._Session()
        try:
            query = session.query(Currency).order_by(Currency.id)
            if paginated:
                result = paginate(query, page, page_size)
            else:
                items = query.all()
                total = query.order_by(None).count()
                result = Page(items, 1, total or 1, total)
        except Exception as e:
            raise e
        finally:
            session.close()

        return {
            'data': [item.asdict() for item in result.items],
            'page': page,
            'page_size': page_size,
            'total_pages': result.pages,
            'total_items': result.total,
            'has_next': result.has_next,
            'has_prev': result.has_previous
        }

    async def _get_last_rate(self, currency_id: int) -> _t.Optional[float]:
        """
        Return the last rate for given Currency.id

        :param currency_id: Currency.id
        :return: Rate.rate or None
        """
        session = self._Session()
        try:
            result = session.query(
                Rate.rate
            ).filter(
                Rate.currency_id == currency_id
            ).order_by(
                Rate.date.desc()
            ).limit(
                1
            ).scalar()
        except Exception as e:
            raise e
        finally:
            session.close()

        return result or None

    async def _get_avg_volume(
            self,
            currency_id: int,
            boundary_date: _dt.date) -> _t.Optional[float]:
        """
        Return average trading volume from given date

        :param currency_id: Currency.id
        :param boundary_date: start date for average calculation
        :return: Avg(Rate.volume) or None
        """
        session = self._Session()
        try:
            result = session.query(
                func.avg(Rate.volume)
            ).filter(
                and_(
                    Rate.currency_id == currency_id,
                    Rate.date >= boundary_date
                )
            ).scalar()
        except Exception as e:
            raise e
        finally:
            session.close()

        return result or None

    async def get_rate_data(
            self,
            currency_id: int,
            boundary_date: _dt.date) -> dict:
        last_rate = await self._get_last_rate(currency_id)
        average = await self._get_avg_volume(currency_id, boundary_date)
        return {
            'last_rate': last_rate,
            'average': average
        }

    async def save_rates(
            self,
            currency_id: int,
            rows: _t.Iterable[CandlesResponse]) -> None:
        session = self._Session()
        try:
            boundary_date = (
                _dt.date.today() - _dt.timedelta(days=INDENT_DAYS - 1)
            )
            new_rates = []
            for row in rows:
                row_mts = _dt.datetime.fromtimestamp(row.mts / 1000)
                if row_mts.date() >= boundary_date:
                    new_rates.append(
                        Rate(
                            currency_id=currency_id,
                            date=row_mts.date(),
                            rate=row.close,
                            volume=row.volume
                        )
                    )
            session.add_all(new_rates)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
