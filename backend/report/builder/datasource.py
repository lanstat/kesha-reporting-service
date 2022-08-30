import csv
from abc import ABC, abstractmethod
from os.path import join


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


