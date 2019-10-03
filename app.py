import aiohttp
from aiohttp import web

from constants import API_URL
from middleware import basic_auth
from views import SimpleHandler


async def update_symbols(db_manager):
    """
    Update currencies

    Requests all currency symbols from the api and saves the missing
    :param db_manager: DbManagerInterface instance
    :return:
    """
    async with aiohttp.ClientSession() as session:
        # endpoint /symbols is not available, so, the hard way
        async with session.get(f'{API_URL}/tickers?symbols=ALL') as resp:
            rows = await resp.json()
            symbols = set()
            if rows:
                # i think 25 is enough for the current task
                symbols = {ticker[0] for ticker in rows[:25]}
            currencies_data = await db_manager.get_currencies_data(
                paginated=False
            )
            existed_symbols = {
                currency['name'] for currency in currencies_data['data']
            }
            symbols -= existed_symbols
            if symbols:
                await db_manager.create_currencies(symbols)


async def create_app(db_manager):
    handler = SimpleHandler(db_manager=db_manager)

    app = web.Application(middlewares=(basic_auth,))
    await update_symbols(db_manager=db_manager)
    app.add_routes([
        web.get('/currencies', handler.list_currencies, name='currencies'),
        web.get(
            r'/rate/{currency_id:[1-9][0-9]*}',
            handler.get_rate_data,
            name='rate'
        ),
        web.get('/update', handler.update_currencies, name='update')
    ])
    return app
