import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import fetch_california_housing

def log(title, content, comment=None):
    print(title + ":")
    if comment:
        print(comment)
    print(content)

housing = fetch_california_housing()

log("Column Names", housing.keys())
log("Feature Names", housing.feature_names, "It refers to the feature names of the houses")
log("Target Names", housing.target_names, "It refers to the species of the houses")

# Create a dataframe from the feature names
df = pd.DataFrame(housing.data, columns=housing.feature_names)
log("Dataframe", df.head())


df["Price"] = housing.target
log("New Column", df.head(), "Added a new column to the DataFrame named Price")

log("Shape", df.shape)
log("Missing Values", df.isnull().sum())

plt.scatter(df["MedInc"], df["Price"])
plt.xlabel("Median Income")
plt.ylabel("House Price")
plt.title("Median Income vs House Price")
plt.show()