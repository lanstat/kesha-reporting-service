<h1 align="center">Kesha Reporting Service (KRS)</h1>
<div align="center">
  <img src="logo.png" height="100"/>
</div>
<div align="center">
  <strong>HTML based reporting service</strong>
</div>
<div align="center">
  Service aimed to generate pdf report using html template using <code>weasyprint</code> and <code>jinja</code>.
</div>

<br />

<div align="center">
  <sub>The little framework that could. Built with ❤︎ by
  <a href="https://lanstat.net">Javier Garson</a> and
  <a href="https://github.com/lanstat/kesha-reporting-service/graphs/contributors">
    contributors
  </a>
</div>

## Table of Contents
- [Features](#features)
- [Example](#example)
- [Installation](#installation)
- [TODO](#todo)

## Features
- __html based report:__ `weasyprint` engine gives more flexibility to design reports

## Example
Configuration file example
```json
{
  "pages": [
    "report.html"
  ],
  "sources": [
    {
      "name": "test",
      "type": "csv",
      "data": {
        "file": "csv.csv"
      }
    }
  ],
  "adapters": [],
  "parameters": [
    {
      "name": "var",
      "default": 5
    }
  ]
}
```

## Installation
```sh
$ docker pull lanstat/krs
```

## TODO
- Add support to postgres database
- Add support to mssql database
- Add API documentation
- Add support to web service datasource
- Add complex examples
- Add test cases

## License
[MIT](https://tldrlegal.com/license/mit-license)

