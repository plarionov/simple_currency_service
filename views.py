import datetime as _dt

import aiohttp
from aiohttp import web

from classes import CandlesResponse
from constants import PAGE_SIZE, INDENT_DAYS, API_URL
from db_managers.interfaces import DbManagerInterface
from utils import transform_to_paginated_response


class SimpleHandler:
    """
    Simple request handler with defined database manager
    """
    def __init__(self, db_manager: DbManagerInterface):
        self.db_manager = db_manager

    async def list_currencies(self, request):
        page_size = int(request.query.get('page_size', PAGE_SIZE))
        page = int(request.query.get('page', 1))
        currencies_data = await self.db_manager.get_currencies_data(
            page=page,
            page_size=page_size
        )
        return web.json_response(
            transform_to_paginated_response(
                url_for=request.match_info.route.url_for,
                request_url=request.url,
                **currencies_data
            )
        )

    async def get_rate_data(self, request):
        currency_id = int(request.match_info.get('currency_id'))
        assert currency_id, 'Currency.id is required'
        boundary_date = _dt.date.today() - _dt.timedelta(days=INDENT_DAYS)
        rate_data = await self.db_manager.get_rate_data(
            currency_id=currency_id,
            boundary_date=boundary_date
        )
        return web.json_response(rate_data)

    async def update_currencies(self, request):
        async with aiohttp.ClientSession() as session:
            currencies_data = await self.db_manager.get_currencies_data(
                paginated=False
            )
            for currency in currencies_data['data']:
                url = f'{API_URL}/candles/trade:1D:{currency["name"]}/hist'
                async with session.get(url) as resp:
                    rows = await resp.json()
                    if rows:
                        try:
                            rows = map(
                                lambda row: CandlesResponse(*row),
                                rows
                            )
                        except Exception as e:
                            raise e
                        await self.db_manager.save_rates(
                            currency_id=currency['id'],
                            rows=rows
                        )
                        print(
                            f"Currency {currency['name']} is updated"
                        )
                    # Ratelimit: 60 req/min
                    # await sleep(1)

        return web.Response(body='Success')
