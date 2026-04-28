import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def log(title="", content="", comment=None, new_line=True, sep="-"):
    print(title + (f" ({comment})" if comment else "") + ": " + f"{'\n' if new_line else ''}{content}")
    if sep:
        print(sep * 50)


data = {
    "Hours_Studied": [1, 2, 3, 4, 5, 6, 7, 8, 2, 5],
    "Attendance": [60, 65, 70, 75, 80, 85, 90, 95, 68, 88],
    "Previous_Score": [50, 55, 60, 65, 70, 75, 80, 85, 58, 78],
    "Sleep_Hours": [5, 6, 6, 7, 7, 8, 8, 8, 6, 7],
    "Final_Score": [52, 57, 63, 68, 72, 78, 84, 90, 60, 80]
}

df = pd.DataFrame(data)

log("Dataframe", df.head())
log("Shape", df.shape, new_line=False)
log("Describe", df.describe())

X = df[["Hours_Studied", "Attendance", "Previous_Score", "Sleep_Hours"]]
y = df["Final_Score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

log("Prediction", list(y_pred), new_line=False, sep="")
log("Actual values", list(y_test), new_line=False)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

log("MAE", mae, "Mean Absolute Error", new_line=False)
log("MSE", mse, "Mean Squared Error", new_line=False)
log("R2 Score", r2, "Coefficient of Determination", new_line=False)

new_student = pd.DataFrame(
    [[6, 85, 76, 7]],
    columns=["Hours_Studied", "Attendance", "Previous_Score", "Sleep_Hours"]
)

log("New Students", new_student.head())

predicted_score = model.predict(new_student)
log("Predicted Final Score", predicted_score[0], new_line=False)
