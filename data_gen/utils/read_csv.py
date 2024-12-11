import pandas as pd

# Read the CSV file
df = pd.read_csv('../resources/pre_curriculum.csv')

# Display the data
print(list(df.iterrows())[5])