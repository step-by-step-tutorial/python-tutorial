import pandas as pd
import category_encoders as ce

data = {'color': ['red', 'green', 'blue', 'red', 'green']}
df = pd.DataFrame(data)

binary_encoder = ce.BinaryEncoder(cols=['color'])
binary_encoder.fit(df['color'])

encoded_data = binary_encoder.transform(df['color'])

df = pd.concat([df, encoded_data], axis=1)

print(df)