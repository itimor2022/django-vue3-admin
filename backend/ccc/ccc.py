import pandas as pd

df = pd.read_csv('btcaddr.txt')
df.to_csv('btcaddr.csv', encoding='utf_8_sig', index=False)
print('btcaddr success')

df = pd.read_csv('ethaddr.txt')
df.to_csv('ethaddr.csv', encoding='utf_8_sig', index=False)
print('ethaddr success')

源码地带