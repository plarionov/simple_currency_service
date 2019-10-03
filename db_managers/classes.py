import sqlalchemy

from db_managers.constants import SQL_ALCHEMY
from db_managers.interfaces import DbManagerInterface
from db_managers.sqlalchemy_manager.classes import \
    SqlAlchemyDbManagerImp


class DbManagerFactory:
    """
    Database manager factory
    """
    @staticmethod
    def get_engine(db_manager: str, connection_str: str) -> DbManagerInterface:
        """
        Returns db manager implementation instance

        :param db_manager: database engine code
        :param connection_str: database connection string
        :return: DbManagerInterface implementation instance
        """
        if db_manager == SQL_ALCHEMY:
            db_manager = sqlalchemy.create_engine(connection_str)
            return SqlAlchemyDbManagerImp(db_engine=db_manager)
        raise NotImplementedError
