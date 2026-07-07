import pandas as pd

recipes = pd.read_csv("dataset/raw/RAW_interactions.csv")

print(recipes.columns)

print(recipes.head())