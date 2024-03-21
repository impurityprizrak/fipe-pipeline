from .database import DBConnectionManager
from .extractor import ExtractionResult
from psycopg2.extras import execute_batch
from typing import Literal
import os


class Exporter:
    def __init__(self, results: ExtractionResult) -> None:
        self.__results = results

        fipe_fields = ['id', 'type', 'value', 'brand', 'model', 'year', 'fuel', 'month_reference', 'fuel_sign']

        fipe_query = f"""
        INSERT INTO fipe ({",".join(fipe_fields)})
        VALUES ({",".join(map(lambda i: f"%({i})s", fipe_fields))})
        ON CONFLICT ON CONSTRAINT fipe_pkey
        DO UPDATE SET ({",".join(fipe_fields)}) = ({",".join(map(lambda i: f"%({i})s", fipe_fields))})
        """

        brands_query = """
        INSERT INTO brands (id, name)
        VALUES (%(id)s, %(name)s)
        ON CONFLICT ON CONSTRAINT brands_pkey
        DO UPDATE SET (id, name) = (%(id)s, %(name)s)
        """

        models_query = """
        INSERT INTO models (id, name)
        VALUES (%(id)s, %(name)s)
        ON CONFLICT ON CONSTRAINT models_pkey
        DO UPDATE SET (id, name) = (%(id)s, %(name)s)
        """

        years_query = """
        INSERT INTO years (id, name)
        VALUES (%(id)s, %(name)s)
        ON CONFLICT ON CONSTRAINT years_pkey
        DO UPDATE SET (id, name) = (%(id)s, %(name)s)
        """

        self.queries = {
            'fipe': fipe_query,
            'brands': brands_query,
            'models': models_query,
            'years': years_query
        }

    def __enter__(self):
        # Abre uma nova conexão com o banco de dados
        self.__db_manager = DBConnectionManager(
            dbname=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT']
        )

        return self
    
    def __exit__(self, *args, **kwargs):
        # Fecha a conexão com o banco de dados ao encerrar a instância
        self.__db_manager.close()

    def export_data(self):
        self.__export('fipe', self.__results['data'])
        self.__export('brands', self.__results['brand'])
        self.__export('models', self.__results['models'])
        self.__export('years', self.__results['years'])

    def __export(self, target: Literal['fipe', 'models', 'years', 'brands'], results: list[dict]):
        # Realiza a exportação dos dados para suas respectivas tabelas
        query = self.queries[target]

        if not self.__db_manager.is_connected:
            self.__db_manager.connect()

        with self.__db_manager.connection.cursor() as cursor:
            try:
                execute_batch(cursor, query, results)
                self.__db_manager.commit()

            except Exception as e:
                print(f"Failed to insert data: {e}")
                self.__db_manager.rollback()

        print(f"Exported {len(results)} for {target} table")