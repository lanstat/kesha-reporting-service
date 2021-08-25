import base64

def money(input):
    if input is not None:
        return '{:,.2f}'.format(input)
    else:
        return '0.00'

def money_int(input):
    if input is not None:
        return '{:,.0f}'.format(input)
    else:
        return '0'

def date(input, format):
    return input.strftime(format)

def svg2data_url(value):
    return "data:image/svg+xml;charset=utf-8;base64," + base64.b64encode(value).decode('utf-8')
