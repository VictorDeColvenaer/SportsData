# import required packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

# import cycling data
cycling_stats = pd.read_csv('/Users/victordecolvenaer/Documents/python_scripts/personal sport data/Activities cycling.csv')
print(cycling_stats)

cycling_stats['Datum'] = pd.to_datetime(cycling_stats['Datum']).dt.to_period('M')
print(cycling_stats)