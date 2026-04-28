import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def log(title="", content="", comment=None, new_line=True, sep="-"):
    line_break = "\n" if new_line else ""
    print(title + (f" ({comment})" if comment else "") + ": " + f"{line_break}{content}")
    if sep:
        print(sep * 50)


def name_segment(center):
    if center["annual_income_k"] >= 90 and center["spending_score"] <= 30:
        return "Premium savers"
    if center["spending_score"] >= 65:
        return "High spenders"
    if center["annual_income_k"] >= 70 and center["spending_score"] <= 30:
        return "Established savers"
    if center["annual_income_k"] <= 35:
        return "Young value seekers"
    return "Balanced shoppers"


data = {
    "customer_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    "age": [22, 25, 24, 27, 45, 46, 43, 48, 35, 36, 34, 38, 52, 54, 50, 57],
    "annual_income_k": [22, 25, 24, 28, 75, 78, 72, 80, 48, 50, 46, 52, 95, 100, 92, 105],
    "spending_score": [80, 76, 82, 74, 20, 18, 22, 19, 55, 58, 52, 60, 10, 8, 12, 9]
}

df = pd.DataFrame(data)

log("Customer Segmentation with K-Means", "Group customers by similar behavior without using labels.")
log("Dataframe", df)
log("Shape", df.shape, new_line=False)

features = ["age", "annual_income_k", "spending_score"]
X = df[features]

# K-Means uses distance, so scaling keeps income from dominating age and score.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["segment"] = kmeans.fit_predict(X_scaled)

centers = pd.DataFrame(
    scaler.inverse_transform(kmeans.cluster_centers_),
    columns=features
).round(2)
centers["segment"] = centers.index
centers["segment_name"] = centers.apply(name_segment, axis=1)

segment_names = centers.set_index("segment")["segment_name"].to_dict()
df["segment_name"] = df["segment"].map(segment_names)

log("Cluster Centers", centers)
log(
    "Segmented Customers",
    df[["customer_id", "age", "annual_income_k", "spending_score", "segment", "segment_name"]]
)

segment_summary = df.groupby(["segment", "segment_name"])[features].mean().round(2)
log("Segment Summary (mean values)", segment_summary)

score = silhouette_score(X_scaled, df["segment"])
log("Silhouette Score", round(score, 3), "Closer to 1 means clusters are better separated", new_line=False)

for segment, group in df.groupby("segment"):
    plt.scatter(
        group["annual_income_k"],
        group["spending_score"],
        label=segment_names[segment],
        s=90
    )

for _, customer in df.iterrows():
    plt.text(
        customer["annual_income_k"] + 0.7,
        customer["spending_score"] + 0.7,
        str(customer["customer_id"]),
        fontsize=8
    )

plt.xlabel("Annual Income (k USD)")
plt.ylabel("Spending Score")
plt.title("Customer Segmentation with K-Means")
plt.legend()
plt.tight_layout()
plt.show()
