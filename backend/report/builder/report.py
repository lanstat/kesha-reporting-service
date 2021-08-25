from report.builder.datasource import CSVSource, MysqlSource
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from django.conf import settings
from django.http import HttpResponse
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
        with io.open(join(self._base_dir, 'report.html'), mode='r', encoding='utf-8') as f:
            self.html = f.read()
        self._parse()
        self.__env = None
        self._variables = {}
        self._default_vars = {}
        self._set_default_variables()
        # locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    def _parse(self):
        base_path = self._base_dir

        def replace_image(match):
            try:
                encoded_string = file_to_url_image(base_path + match[1])
                tmp = 'src="' + encoded_string + '"'
            except:
                tmp = 'src=""'
            return tmp
        self.html = re.sub(r'img-src="((\w|/|\.)+)"', replace_image, self.html)

    def set_variables(self, variables):
        self._variables = variables

    def render_report(self):
        loader = jinja2.FileSystemLoader('/tmp')
        self.__env = jinja2.Environment(autoescape=False, loader=loader)
        self._set_filters()
        self._load_external_filter()
        temp = self.__env.from_string(self.html)

        variables = {**self._default_vars, **self._variables}
        self._parse_config(variables)

        self.html = temp.render(**variables)

    def _set_filters(self):
        m1 = importlib.import_module('report.builder.filters')
        for name, callback in getmembers(m1, isfunction):
            self.__env.filters[name] = callback

    def _load_external_filter(self):
        m1 = importlib.import_module('media.' + self._report_id + '.custom')
        for name, callback in getmembers(m1, isfunction):
            if not name.startswith('core__'):
                self.__env.filters[name] = callback

    def _set_default_variables(self):
        self._default_vars = {
            'now': datetime.date.today()
        }

    def _parse_config(self, variables):
        with io.open(join(self._base_dir, 'config.json'), mode='r', encoding='utf-8') as f:
            config = json.loads(f.read())
        adapters = {}
        parameters = {'var': 0}
        for dt in config['sources']:
            if dt['type'] == 'csv':
                tmp = CSVSource(self._base_dir, dt)
                adapters |= tmp.process(config['adapters'], parameters)
            elif dt['type'] == 'mysql':
                tmp = MysqlSource(self._base_dir, dt)
                adapters |= tmp.process(config['adapters'], parameters)
        variables |= adapters

    def __get_stylesheets(self):
        listing = []
        for file in listdir(self._base_dir):
            path = join(self._base_dir, file)
            if os.path.isfile(path) and file.endswith('.css'):
                listing.append(CSS(path))
        return listing

    def generate(self, filename):
        self.render_report()
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename='+filename+'.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        font_config = FontConfiguration()
        HTML(string=self.html).write_pdf(
            response,
            font_config=font_config,
            stylesheets=self.__get_stylesheets()
        )
        return response

    def generate_stream(self):
        self.render_report()
        font_config = FontConfiguration()
        pdf = HTML(string=self.html).render(
            font_config=font_config,
            stylesheets=self.__get_stylesheets()
        )

        return pdf

    def generate_file(self, filename):
        self.render_report()
        font_config = FontConfiguration()
        pdf = HTML(string=self.html).write_pdf(
            font_config=font_config,
            stylesheets=self.__get_stylesheets()
        )

        media_dir = '/tmp/'
        if os.path.exists(media_dir):
            f = open(os.path.join(media_dir, filename + '.pdf'), 'wb')
            f.write(pdf)

        return filename + '.pdf'


def merge_report(reports):
    pages = []
    current_pdf = None
    for report in reports:
        pdf = report.generate_stream()
        if current_pdf is None:
            current_pdf = pdf
        for p in pdf.pages:
            pages.append(p)
    pdf = current_pdf.copy(pages).write_pdf()
    return pdf


def file_to_url_image(file_path):
    if file_path is not None and os.path.exists(file_path):
        mime = 'jpeg'
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            if file_path.endswith('.png'):
                mime = 'png'
        tmp = 'data:image/' + mime + ';base64,' + encoded_string.decode('utf-8')
        return tmp
    else:
        return ''
