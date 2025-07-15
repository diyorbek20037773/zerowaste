import pandas as pd
import random

# Read the CSV file into a DataFrame
df = pd.read_csv("D:\\Dasturlash\\VS code\\Hakhathon\\Navruz\\ZeroWaste\\enhanced_store_data.csv")

# Modify 'location_long' to random floats between 69.1 and 69.4 (Tashkent longitude)
df['location_long'] = [random.uniform(69.1, 69.4) for _ in range(len(df))]

# Modify 'location_lat' to random floats between 41.2 and 41.4 (Tashkent latitude)
df['location_lat'] = [random.uniform(41.2, 41.4) for _ in range(len(df))]

# Save the modified DataFrame back to the original CSV (overwriting it)
df.to_csv("D:\\Dasturlash\\VS code\\Hakhathon\\Navruz\\ZeroWaste\\enhanced_store_data.csv", index=False)

# Display the first few rows to verify
print(df.head())