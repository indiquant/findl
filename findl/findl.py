__author__ = 'indiquant'


from weblib.nse import get_options_nse, load_options_nse


def get_options(undl, src='NSE'):

    if src == 'NSE':
        return get_options_nse(undl)


def load_options(undl, path=r'C:\Temp\findl.txt', sep='\t', src='NSE'):

    if src == 'NSE':
        return load_options_nse(undl, path, sep)