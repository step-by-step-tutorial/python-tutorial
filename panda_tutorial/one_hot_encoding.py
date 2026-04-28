import pandas as pd

data = {'color': ['red', 'green', 'blue', 'red', 'green']}
df = pd.DataFrame(data)

color_one_hot = pd.get_dummies(df['color'], prefix=['color'])

df = pd.concat([df, color_one_hot], axis=1)

df = df.drop('color', axis=1)

print(df)