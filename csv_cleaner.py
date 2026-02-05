import pandas as pd

df = pd.read_csv("dirty_cafe_sales.csv")
pd.set_option("display.max_columns",None)
print(df.info())