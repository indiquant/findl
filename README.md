# findl
Financial (FIN) Data (D) Library (L)

* Installation
```python
  pip install findl
```

* Use

```python
from findl import get_options, load_options

#
# get_options return a pandas dataframe of option prices
# 
df = get_options('NIFTY', src='NSE')

#
# load_options gets the options dataframe
# it then writes the data to the path provided
#
load_options('NIFTY', path=r'C:\Temp\options.txt', sep='\t', src='NSE')

```
