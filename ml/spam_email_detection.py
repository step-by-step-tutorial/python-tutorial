import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def log(title="", content="", comment=None, new_line=True, sep="-"):
    print(title + (f" ({comment})" if comment else "") + ": " + f"{'\n' if new_line else ''}{content}")
    if sep:
        print(sep * 50)


data = {
    "message": [
        "Win a free lottery ticket now",
        "Call me when you arrive",
        "Congratulations you have won a prize",
        "Let's have lunch tomorrow",
        "Claim your free vacation now",
        "Are you coming to the meeting?",
        "You have been selected for a cash reward",
        "Please send me the report",
        "Exclusive offer just for you",
        "How are you today?"
    ],
    "label": [
        "spam",
        "ham",
        "spam",
        "ham",
        "spam",
        "ham",
        "spam",
        "ham",
        "spam",
        "ham"
    ]
}

df = pd.DataFrame(data)

log("Dataframe", df.head())
log("Grouping", df["label"].value_counts())

X = df["message"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("classifier", MultinomialNB())
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

log("Prediction", list(y_pred), new_line=False, sep="")
log("Actual values", list(y_test), new_line=False)

log("Accuracy", accuracy_score(y_test, y_pred), new_line=False)
log("Classification Report", classification_report(y_test, y_pred))
log("Confusion Matrix", confusion_matrix(y_test, y_pred))

new_messages = [
    "You won a free cash prize",
    "Can we meet tomorrow morning?"
]

predictions = model.predict(new_messages)

for message, prediction in zip(new_messages, predictions):
    log("Message", message, new_line=False, sep="")
    log("Prediction", prediction, new_line=False)
