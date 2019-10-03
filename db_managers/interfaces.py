import datetime as _dt
import typing as _t

from classes import CandlesResponse


class DbManagerInterface:
    """
    Database Manager class Interface

    Contains public methods for database manipulations.
    """

    async def create_currencies(self, names: _t.Iterable[str]):
        """
        Create Currency record for given names

        :param names: Iterable with currency names
        :return: None
        """
        raise NotImplementedError

    async def get_currencies_data(
            self,
            paginated: bool = True,
            page: int = 0,
            page_size: int = 0) -> dict:
        """
        Return currencies data with pagination.

        :param paginated: activate pagination
        :param page: page number
        :param page_size: page size (query size limit)
        :return: dict
        """
        raise NotImplementedError

    async def get_rate_data(
            self,
            currency_id: int,
            boundary_date: _dt.date) -> dict:
        """
        Return the last currency rate and average trading volume
        from the boundary date

        :param currency_id: currency id
        :param boundary_date: start date for calculations
        :return: list
        """
        raise NotImplementedError

    async def save_rates(
            self,
            currency_id: int,
            rows: _t.Iterable[CandlesResponse]) -> None:
        """
        Save given currency rates

        :param currency_id: Currency.id
        :param rows: list with data
        :return: None
        """
        raise NotImplementedError
