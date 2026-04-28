import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import load_iris


def log(title, content, comment=None):
    print(title + ":")
    if comment:
        print(comment)
    print(content)


iris = load_iris()

log("Column Names", iris.keys())
log("Feature Names", iris.feature_names, "It refers to the feature names of the flowers")
log("Target Names", iris.target_names, "It refers to the species of the flowers")

# Create a dataframe from the feature names
df = pd.DataFrame(iris.data, columns=iris.feature_names)
log("Dataframe", df.head())

df["target"] = iris.target
log("New Column", df.head(), "Added a new column to the DataFrame named target")

# Map flower species to target
df["species"] = df["target"].apply(lambda x: iris.target_names[x])
log("New Column", df.head(), "Added a new column to the DataFrame named species")

log("Shape", df.shape)
log("Classifications", df["species"].value_counts(), "Classifications of the flowers")

plt.scatter(df["sepal length (cm)"], df["sepal width (cm)"])
plt.xlabel("Sepal Length")
plt.ylabel("Sepal Width")
plt.title("Sepal Length vs Sepal Width")
plt.show()
