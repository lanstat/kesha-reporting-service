from datasource import DataSource
import psycopg2


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
