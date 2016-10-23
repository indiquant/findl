__author__ = 'indiquant'


import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
from enum import Enum
import pandas as pd
import logging
logging.basicConfig(format='%(levelname)s %(asctime)s:%(message)s', level=logging.DEBUG)


def get_options_nse(undl):

    try:
        undltype = _undltypes[undl]

    except KeyError:
        undltype = 'stock'

    df = None

    for exp in _nse_options_expiries:
        pg = get_option_page(undl, exp, undltype)
        sp = BeautifulSoup(pg)
        t, s = get_live(sp.body)
        opts = parse_options_body(sp.body)

        if df is None:
            df = get_sql_df(undl, t, s, exp, opts, undltype)

        else:
            df = df.append(get_sql_df(undl, t, s, exp, opts, undltype))

    return df


def load_options_nse(undl, path, sep):
    df = get_options_nse(undl)
    df.to_csv(path, index=False, sep=sep)


_nse_options_expiries = [
    '2016-10-27',
    '2016-11-24',
    '2016-12-29',
    '2017-03-30'
]


_undltypes = {
    'NIFTY': 'index'
}


_months = {'JAN': 1,
           'FEB': 2,
           'MAR': 3,
           'APR': 4,
           'MAY': 5,
           'JUN': 6,
           'JUL': 7,
           'AUG': 8,
           'SEP': 9,
           'OCT': 10,
           'NOV': 11,
           'DEC': 12}


class EnumNseOptionTable(Enum):
    c_chart = 1
    c_oi = 2
    c_chng_oi = 3
    c_volume = 4
    c_iv = 5
    c_lastpx = 6
    c_chng = 7
    c_bidqty = 8
    c_bidpx = 9
    c_askpx = 10
    c_askqty = 11
    k = 12
    p_bidqty = 13
    p_bidpx = 14
    p_askpx = 15
    p_askqty = 16
    p_chng = 17
    p_lastpx = 18
    p_iv = 19
    p_volume = 20
    p_chng_oi = 21
    p_oi = 22
    p_chart = 23


class EnumOptionTable(Enum):
    undl = 1
    undl_type = 2
    spot = 3
    opt_type = 4
    exc_type = 5
    expiry = 6
    strike = 7
    recdate = 8
    rectime = 9
    bidpx = 10
    bidqty = 11
    askpx = 12
    askqty = 13
    lastpx = 14
    volume = 15


def month_number(mmm):
    """
    :type mmm: basestring
    """
    return _months[mmm.upper()]


def yyyymmdd(d):
    """
    :type d: datetime
    """
    return int(d.strftime('%Y%m%d'))


def hhmmss(d):
    """
    :type d: datetime
    """
    return int(d.strftime('%H%M%S'))


get_text = lambda x: x.getText()


future_site = 'http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuoteFO.jsp?' \
              + 'underlying=&lt;symbol&gt;&amp;instrument=&lt;imnt_type&gt;'
option_site = 'https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?' \
              + 'segmentLink=17&instrument={instrument}&symbol={symbol}&date={expiry}'


fut_imnt_type = {'stock': 'FUTSTK', 'index': 'FUTIDX'}
opt_instrument_type = {'stock': 'OPTSTK', 'index': 'OPTIDX'}


def get_option_page(symbol, exp='-', undltype='index'):
    """
    :type exp: basestring
    """

    if exp == '-':
        site = option_site.format(symbol=symbol, instrument=opt_instrument_type[undltype], expiry='-')

    else:
        site = option_site.format(symbol=symbol, instrument=opt_instrument_type[undltype],
                                  expiry=datetime.strptime(exp, '%Y-%m-%d').strftime('%d%b%Y').upper())

    print(site)

    try:

        logging.debug("Getting data from:" + site)

        hdr = {'User-Agent': 'Web-Scraping',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

        req = urllib2.Request(site, headers=hdr)

        page = urllib2.urlopen(req).read()

        return page

    except:
        logging.debug("Check the site: " + str(site))
        raise


def get_time(opt):
    """
    :type opt: BeautifulSoup
    """
    children = opt.find_all('span')

    for ch in children:
        print ch

        txt = ch.text.replace(',', '').lower()

        if txt[:5] == 'as on':
            _, _, mth, dd, yyyy, hhmmss, _ = txt.strip().split(' ')

            hh, mm, ss = hhmmss.split(":")

            return datetime(int(yyyy), month_number(mth), int(dd), int(hh), int(mm), int(ss))

    return None


def get_live(opt):
    """
    :type opt: BeautifulSoup
    """
    children = opt.find_all('span')

    t, s = None, None

    for ch in children:
        print ch

        txt = ch.text.replace(',', '').lower()

        if txt.split(' ')[:2] == ['as', 'on']:
            _, _, mth, dd, yyyy, hms, _ = txt.strip().split(' ')

            hh, mm, ss = hms.split(":")

            t = datetime(int(yyyy), month_number(mth), int(dd), int(hh), int(mm), int(ss))

        elif txt.split(':')[0] in ('underlying stock', 'underlying index'):

            s = float(txt.split(':')[1].strip(' ').split(' ')[1])

    return t, s


def get_expiries(body):
    """
    :type body: BeautifulSoup
    """

    _ex = body.find_all('select', {'id': 'date', 'name': 'date'})

    ex = []

    for ch in _ex:
        print ch.text

        for _e in ch:
            try:
                ex.append(datetime.strptime(_e.text, '%d%b%Y').date())

            except ValueError:
                pass

            except AttributeError:
                pass

    return ex


def parse_options_body(opt_body):

    opt_tbl = opt_body.find('table', {'id': 'octable'})

    cols = []
    rows = []

    for r in opt_tbl.find_all('tr'):

        if r.text.find('CALLS') >= 0 and r.text.find('PUTS') >= 0:

            print('row-1')

        else:

            drow = r.find_all('td')

            if not drow:
                head = r.find_all('th')
                for col in head:
                    cols.append(str(col.contents[0]))

            else:
                _r = ()
                for d in drow:
                    _r += (process_cell(d),)

                rows.append(_r)

    return rows


def get_sql_df(undl, tm, spot, exp, optrows, undltype='index'):

    d = [(EnumOptionTable.undl.name,
          EnumOptionTable.undl_type.name,
          EnumOptionTable.spot.name,
          EnumOptionTable.opt_type.name,
          EnumOptionTable.exc_type.name,
          EnumOptionTable.expiry.name,
          EnumOptionTable.strike.name,
          EnumOptionTable.recdate.name,
          EnumOptionTable.rectime.name,
          EnumOptionTable.bidpx.name,
          EnumOptionTable.bidqty.name,
          EnumOptionTable.askpx.name,
          EnumOptionTable.askqty.name,
          EnumOptionTable.lastpx.name,
          EnumOptionTable.volume.name)]

    for r in optrows:
        try:
            c_row = (undl,
                     undltype,
                     spot,
                     'C',
                     'E',
                     yyyymmdd(datetime.strptime(exp, '%Y-%m-%d')),
                     r[EnumNseOptionTable.k.value - 1],
                     yyyymmdd(tm),
                     hhmmss(tm),
                     r[EnumNseOptionTable.c_bidpx.value - 1],
                     r[EnumNseOptionTable.c_bidqty.value - 1],
                     r[EnumNseOptionTable.c_askpx.value - 1],
                     r[EnumNseOptionTable.c_askqty.value - 1],
                     r[EnumNseOptionTable.c_lastpx.value - 1],
                     r[EnumNseOptionTable.c_volume.value - 1])
            
            p_row = (undl,
                     undltype,
                     spot,
                     'P',
                     'E',
                     yyyymmdd(datetime.strptime(exp, '%Y-%m-%d')),
                     r[EnumNseOptionTable.k.value - 1],
                     yyyymmdd(tm),
                     hhmmss(tm),
                     r[EnumNseOptionTable.p_bidpx.value - 1],
                     r[EnumNseOptionTable.p_bidqty.value - 1],
                     r[EnumNseOptionTable.p_askpx.value - 1],
                     r[EnumNseOptionTable.p_askqty.value - 1],
                     r[EnumNseOptionTable.p_lastpx.value - 1],
                     r[EnumNseOptionTable.p_volume.value - 1])
            
            d.append(c_row)
            d.append(p_row)
            
        except:
            pass
        
    return pd.DataFrame(d[1:], columns=d[0])


def process_cell(d):

    try:

        if d.a:
            if d.a.b:
                if d.a.b.contents[0].strip() == u'-':
                    return None

                else:
                    return float(d.a.b.contents[0].strip().replace(',', ''))

            else:
                if d.a.contents[0].strip() == u'-':
                    return None

                else:
                    return float(d.a.contents[0].strip().replace(',', ''))

        else:
            if d.contents[0].strip() == '-':
                return None

            else:
                return float(d.contents[0].strip().replace(',', ''))

    except TypeError:
        return None

    except IndexError:
        return None
    