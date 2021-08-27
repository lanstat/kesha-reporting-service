from report.builder.datasource import CSVSource, MysqlSource
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from django.conf import settings
import re
import base64
import datetime
from os import listdir
import os.path
from os.path import join
import jinja2
import locale
import importlib
import io
import json
from inspect import getmembers, isfunction


class Report:
    def __init__(self, name):
        self._report_id = name
        self._base_dir = join(settings.BASE_DIR, 'media', name)
        with io.open(join(self._base_dir, 'config.json'),
                     mode='r',
                     encoding='utf-8') as f:
            self._config = json.loads(f.read())
        loader = jinja2.FileSystemLoader('/tmp')
        self.__env = jinja2.Environment(autoescape=False, loader=loader)
        self._variables = {}
        self._default_vars = {}
        self._parameters = {}

        self._prerender_hook = None
        self._set_default_variables()
        self._set_filters()
        self._load_external_filter()
        # locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    def set_variables(self, variables):
        self._variables = variables

    def _render_page(self, page, variables):
        with io.open(join(self._base_dir, page), mode='r',
                     encoding='utf-8') as f:
            html = f.read()
        temp = self.__env.from_string(self._parse_page(html))

        return temp.render(**variables)

    def _parse_page(self, html):
        base_path = self._base_dir

        def replace_image(match):
            try:
                encoded_string = file_to_url_image(base_path + match[1])
                tmp = 'src="' + encoded_string + '"'
            except:
                tmp = 'src=""'
            return tmp

        return re.sub(r'img-src="((\w|/|\.)+)"', replace_image, html)

    def _set_filters(self):
        m1 = importlib.import_module('report.builder.filters')
        for name, callback in getmembers(m1, isfunction):
            self.__env.filters[name] = callback

    def _load_external_filter(self):
        m1 = importlib.import_module('media.' + self._report_id + '.custom')
        for name, callback in getmembers(m1, isfunction):
            if not name.startswith('core__'):
                self.__env.filters[name] = callback
            else:
                if name == 'core__prerender':
                    self._prerender_hook = callback

    def _set_default_variables(self):
        self._default_vars = {'now': datetime.date.today()}

    def _parse_config(self):
        adapters = {}
        for dt in self._config['sources']:
            if dt['type'] == 'csv':
                tmp = CSVSource(self._base_dir, dt)
                adapters |= tmp.process(self._config['adapters'],
                                        self._parameters)
            elif dt['type'] == 'mysql':
                tmp = MysqlSource(self._base_dir, dt)
                adapters |= tmp.process(self._config['adapters'],
                                        self._parameters)

        if self._prerender_hook is not None:
            self._prerender_hook(adapters)
        return adapters

    def __get_stylesheets(self):
        listing = []
        for file in listdir(self._base_dir):
            path = join(self._base_dir, file)
            if os.path.isfile(path) and file.endswith('.css'):
                listing.append(CSS(path))
        return listing

    def set_parameters(self, data):
        for p in self._config['parameters']:
            name = p['name']
            if name in data:
                self._parameters[name] = data[name]
            elif 'default' in p:
                self._parameters[name] = p['default']
            else:
                raise Exception('report parameter not defined')

    def generate(self):
        variables = {**self._default_vars, **self._variables}
        variables |= self._parse_config()

        font_config = FontConfiguration()
        stylesheets = self.__get_stylesheets()
        pages = []

        document = None
        for page in self._config['pages']:
            html = self._render_page(page, variables)
            pdf = HTML(string=html).render(font_config=font_config,
                                           stylesheets=stylesheets)
            if document is None:
                document = pdf
            for p in pdf.pages:
                pages.append(p)
        return document.copy(pages).write_pdf()

    @staticmethod
    def validate_config(path):
        config_path = join(path, 'config.json')
        if not os.path.exists(config_path):
            return False

        with io.open(config_path,
                     mode='r',
                     encoding='utf-8') as f:
            config = json.loads(f.read())
        if not 'adapters' in config:
            return False
        if not 'sources' in config:
            return False
        if not 'pages' in config:
            return False
        elif len(config['pages']) == 0:
            return False
        if not 'parameters' in config:
            return False

        return True


def file_to_url_image(file_path):
    if file_path is not None and os.path.exists(file_path):
        mime = 'jpeg'
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            if file_path.endswith('.png'):
                mime = 'png'
        tmp = 'data:image/' + mime + ';base64,' + encoded_string.decode(
            'utf-8')
        return tmp
    else:
        return ''
