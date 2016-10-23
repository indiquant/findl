__author__ = 'indiquant'


from findl import get_options, load_options


def main():
    df = get_options('NIFTY', src='NSE')
    print(df[:100])

    load_options('NIFTY', path=r'C:\Temp\findl.txt', sep='\t', src='NSE')


if __name__ == '__main__':
    main()