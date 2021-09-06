import csv
import MySQLdb
from abc import ABC, abstractmethod
from os.path import join
import psycopg2


class DataSource(ABC):
    def __init__(self, base_dir, data) -> None:
        self._base_dir = base_dir
        self._data = data['data']
        self._source = data

    @abstractmethod
    def process(self, adapters, parameters):
        pass


class CSVSource(DataSource):
    def __init__(self, base_dir, data) -> None:
        super().__init__(base_dir, data)

    def process(self, adapters, parameters):
        filename = join(self._base_dir, self._data['file'])
        rows = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for r in reader:
                rows.append(r)
        response = {}
        response['_' + self._source['name']] = rows
        return response


class MysqlSource(DataSource):
    def __init__(self, base_dir, data) -> None:
        super().__init__(base_dir, data)

    def process(self, adapters, parameters):
        response = {}

        db = MySQLdb.connect(host=self._data['host'],
                             user=self._data['username'],
                             passwd=self._data['password'],
                             database=self._data['database'])

        cursor = db.cursor()

        for ad in adapters:
            if ad['source'] != self._source['name']:
                continue
            query = ad['data']['query']

            for name, value in parameters.items():
                query = query.replace('{{' + name + '}}', str(value))

            cursor.execute(query)
            columns = cursor.description
            if 'single-row' in ad['data'] and ad['data']['single-row']:
                result = {
                    columns[index][0]: column
                    for index, column in enumerate(cursor.fetchone())
                }
            else:
                result = [{
                    columns[index][0]: column
                    for index, column in enumerate(value)
                } for value in cursor.fetchall()]
            response['_' + ad['name']] = result
        cursor.close()
        db.close()

        return response


class PostgresSource(DataSource):
    def __init__(self, base_dir, data) -> None:
        super().__init__(base_dir, data)

    def process(self, adapters, parameters):
        response = {}

        db = psycopg2.connect(host=self._data['host'],
                             user=self._data['username'],
                             password=self._data['password'],
                             database=self._data['database'])

        cursor = db.cursor()

        for ad in adapters:
            if ad['source'] != self._source['name']:
                continue
            query = ad['data']['query']

            for name, value in parameters.items():
                query = query.replace('{{' + name + '}}', str(value))

            cursor.execute(query)
            columns = cursor.description
            if 'single-row' in ad['data'] and ad['data']['single-row']:
                result = {
                    columns[index][0]: column
                    for index, column in enumerate(cursor.fetchone())
                }
            else:
                result = [{
                    columns[index][0]: column
                    for index, column in enumerate(value)
                } for value in cursor.fetchall()]
            response['_' + ad['name']] = result
        cursor.close()
        db.close()

        return response
