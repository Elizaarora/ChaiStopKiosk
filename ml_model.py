import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors

# 1️⃣ Dummy data (we’ll replace this with Firebase orders soon)
data = pd.DataFrame([
    {"Base": "Milk", "Flavor": "Masala", "Strength": "Strong", "Sugar": 2, "Masala": "Yes"},
    {"Base": "Almond Milk", "Flavor": "Ginger (Adrak)", "Strength": "Medium", "Sugar": 1, "Masala": "No"},
    {"Base": "Water", "Flavor": "Plain", "Strength": "Light", "Sugar": 0, "Masala": "No"},
    {"Base": "Milk", "Flavor": "Elaichi", "Strength": "Medium", "Sugar": 3, "Masala": "Yes"},
    {"Base": "Milk", "Flavor": "Masala", "Strength": "Medium", "Sugar": 2, "Masala": "Yes"},
])

# 2️⃣ Encode categorical features to numeric
le_base = LabelEncoder()
le_flavor = LabelEncoder()
le_strength = LabelEncoder()
le_masala = LabelEncoder()

data["Base"] = le_base.fit_transform(data["Base"])
data["Flavor"] = le_flavor.fit_transform(data["Flavor"])
data["Strength"] = le_strength.fit_transform(data["Strength"])
data["Masala"] = le_masala.fit_transform(data["Masala"])

# 3️⃣ Fit the KNN model
model = NearestNeighbors(n_neighbors=2, metric='euclidean')
model.fit(data)

# 4️⃣ Function to recommend
def recommend_chai(input_dict):
    input_df = pd.DataFrame([input_dict])
    input_df["Base"] = le_base.transform(input_df["Base"])
    input_df["Flavor"] = le_flavor.transform(input_df["Flavor"])
    input_df["Strength"] = le_strength.transform(input_df["Strength"])
    input_df["Masala"] = le_masala.transform(input_df["Masala"])

    distances, indices = model.kneighbors(input_df)
    recommended_index = indices[0][1]  # Skip self (0), pick next closest
    return recommended_index
