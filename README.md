# findl
Financial (FIN) Data (D) Library (L)

* Installation
```python
  pip install findl
```

* Use

```python
from findl import get_options, load_options

# get_options return a pandas dataframe of live option prices
#
# currently this functionality is available for the Indian option market
# the source of option prices is the NSE website option page
# 
# By iteratively running this script during trading hours,  
# one can get intraday options data
#
# future releases will include US market
df = get_options('NIFTY', src='NSE')

# load_options gets the options dataframe
# it then writes the data to the path provided
#
# same as above, thisfunctionality is available only for the Indian market
# source is NSE website
load_options('NIFTY', path=r'C:\Temp\options.txt', sep='\t', src='NSE')

```
