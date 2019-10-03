import os

from aiohttp import BasicAuth
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from app import create_app
from constants import PAGE_SIZE
from db_managers.classes import DbManagerFactory
from db_managers.constants import SQL_ALCHEMY


class MyAppTestCase(AioHTTPTestCase):

    auth_headers = {
        'Authorization': BasicAuth(
            login='admin', password='12345'
        ).encode(),
    }

    async def get_application(self):
        db_manager = os.environ.get('DB_MANAGER', SQL_ALCHEMY)
        db_connection_str = 'sqlite:///test.db'
        db_impl = DbManagerFactory.get_engine(
            db_manager=db_manager,
            connection_str=db_connection_str
        )
        return await create_app(db_impl)

    @unittest_run_loop
    async def test_auth(self):
        url = self.app.router['currencies'].url_for()
        resp = await self.client.get(url)
        self.assertEqual(resp.status, 401)

        resp = await self.client.get(url, headers=self.auth_headers)
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_aupdate(self):
        url = self.app.router['update'].url_for()
        resp = await self.client.get(url, headers=self.auth_headers)
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_currencies(self):
        url = self.app.router['currencies'].url_for()
        resp = await self.client.get(url, headers=self.auth_headers)
        self.assertEqual(resp.status, 200)

        result = await resp.json()
        self.assertEqual(len(result['data']), PAGE_SIZE)

    @unittest_run_loop
    async def test_currencies_pagination(self):
        page = 2
        page_size = 7
        url = self.app.router['currencies'].url_for()
        page_1 = url.with_query(page_size=page_size)
        page_2 = url.with_query(page=page, page_size=page_size)

        page_1_resp = await self.client.get(page_1, headers=self.auth_headers)
        page_2_resp = await self.client.get(page_2, headers=self.auth_headers)
        self.assertEqual(page_1_resp.status, 200)
        self.assertEqual(page_2_resp.status, 200)

        page_1_result = await page_1_resp.json()
        page_2_result = await page_2_resp.json()
        self.assertEqual(len(page_1_result['data']), page_size)
        self.assertEqual(len(page_2_result['data']), page_size)
        self.assertLess(
            page_1_result['meta']['page'],
            page_2_result['meta']['page']
        )
        self.assertNotEqual(
            page_1_result['data'],
            page_2_result['data']
        )

    @unittest_run_loop
    async def test_rate(self):
        currencies_url = self.app.router['currencies'].url_for().with_query(
            page_size=1
        )
        resp = await self.client.get(currencies_url, headers=self.auth_headers)
        result = await resp.json()
        currency_id = result['data'][0]['id']
        rate_url = self.app.router['rate'].url_for(currency_id=str(currency_id))

        resp = await self.client.get(rate_url, headers=self.auth_headers)
        self.assertEqual(resp.status, 200)

        result = await resp.json()

        self.assertIsNotNone(result['last_rate'])
        self.assertIsNotNone(result['average'])
