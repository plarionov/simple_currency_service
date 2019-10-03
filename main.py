import os

from aiohttp import web

from app import create_app
from db_managers.classes import DbManagerFactory
from db_managers.constants import SQL_ALCHEMY

db_manager = os.environ.get('DB_MANAGER', SQL_ALCHEMY)
db_connection_str = os.environ.get('DB_CONNECTION_STR')
db_impl = DbManagerFactory.get_engine(
    db_manager=db_manager,
    connection_str=db_connection_str
)

if __name__ == '__main__':
    app = create_app(db_impl)
    web.run_app(app, host='0.0.0.0', port=1234)
