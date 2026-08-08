import ast
import re
import joblib
import numpy as np
import pandas as pd

model = joblib.load("../models/medicine_price_model.pkl")

encoder = joblib.load("../models/onehot_encoder.pkl")

mlb = joblib.load("../models/multilabel_binarizer.pkl")

model_columns = joblib.load("../models/model_columns.pkl")

medians = joblib.load("../models/medians.pkl")

composition_price = joblib.load("../models/composition_price.pkl")

top_manufacturers = joblib.load("../models/top_manufacturers.pkl")

clean_df = joblib.load("../data/cleaned_df.pkl")


categorical_features = [
    "manufacturer",
    "dosage_form",
    "pack_unit",
    "therapeutic_class"
]

numerical_features = [
    "pack_size",
    "num_active_ingredients",
    "composition_price",
]

def extract_strength(value):
    if pd.isna(value):
        return None

    value = str(value)

    match = re.search(r"\d+\.?\d*", value)

    if match:
        return float(match.group())

    return None

def normalize_strength(value):
    if not value:
        return ""

    value = value.strip().lower()

    match = re.match(r"([\d.]+)\s*(mg|g|gm|ml)", value)

    if not match:
        return value

    number = float(match.group(1))
    unit = match.group(2)

    if unit in ("g", "gm"):
        return f"{number * 1000:.0f}mg"

    return value

def create_cleaned_composition(value):
    if pd.isna(value):
        return None

    ingredients = ast.literal_eval(value)

    composition = []

    for item in ingredients:
        name = (item.get("name") or "").strip().lower()
        strength = normalize_strength(item.get("strength"))

        if strength:
            composition.append(f"{name} {strength}")
        else:
            composition.append(name)

    composition.sort()

    return " | ".join(composition)

def get_medicine(medicine_name):

    medicine_name = medicine_name.strip().lower()

    matches = clean_df[
        clean_df["brand_name"]
        .str.lower()
        == medicine_name
    ]

    if matches.empty:
        return None

    return matches.iloc[0]

def preprocess_row(row):
    # Convert Series to DataFrame
    df = pd.DataFrame([row])

    # -----------------------------
    # Extract strength
    # -----------------------------
    df["primary_strength_value"] = (
    df["primary_strength"]
        .apply(extract_strength)
    )

    df["primary_strength_value"] = pd.to_numeric(
        df["primary_strength_value"],
        errors="coerce"
    )

    df["primary_strength_value"] = (
        df["primary_strength_value"]
        .fillna(float(medians["primary_strength_value"]))
    )

    df["primary_strength_value"] = (
        df["primary_strength_value"]
        .astype(np.float64)
    )
    # -----------------------------
    # Fill missing values
    # -----------------------------
    df["pack_size"] = (
        df["pack_size"]
        .fillna(medians["pack_size"])
    )

    # -----------------------------
    # Composition median encoding
    # -----------------------------
    global_price = composition_price.median()

    df["composition_price"] = (
        df["cleaned_composition"]
        .map(composition_price)
        .fillna(global_price)
    )

    # -----------------------------
    # Manufacturer grouping
    # -----------------------------
    df["manufacturer"] = df["manufacturer"].where(
        df["manufacturer"].isin(top_manufacturers),
        "Other"
    )

    # -----------------------------
    # OneHot Encoding
    # -----------------------------
    encoded = encoder.transform(
        df[categorical_features]
    )

    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out(
            categorical_features
        ),
        index=df.index
    )

    # -----------------------------
    # MultiLabel Encoding
    # -----------------------------
    ingredient_matrix = mlb.transform(
        df["ingredient_names"]
    )

    ingredient_df = pd.DataFrame(
        ingredient_matrix,
        columns=mlb.classes_,
        index=df.index
    )

    # -----------------------------
    # Final feature matrix
    # -----------------------------
    X = pd.concat(
        [
            df[numerical_features],
            df["primary_strength_value"].to_frame(),
            encoded_df,
            ingredient_df
        ],
        axis=1
    )

    X = X.reindex(
        columns=model_columns,
        fill_value=0
    )

    return X

def predict_price(medicine_name):

    row = get_medicine(medicine_name)

    if row is None:
        return None

    X = preprocess_row(row)

    prediction = model.predict(X)

    prediction = np.expm1(prediction)

    return round(float(prediction[0]), 2)

def find_alternatives(medicine_name, top_n=5):

    medicine = get_medicine(medicine_name)

    if medicine is None:
        return None

    composition = medicine["cleaned_composition"]

    alternatives = clean_df[
        clean_df["cleaned_composition"] == composition
    ].copy()

    alternatives = alternatives[
        alternatives["brand_name"].str.lower()
        != medicine_name.lower()
    ]

    alternatives = alternatives.sort_values("price_inr")
    alternatives = alternatives.drop_duplicates(
        subset="brand_name",
        keep="first"
    )

    results = []

    for _, row in alternatives.head(top_n).iterrows():

        predicted_price = model.predict(preprocess_row(row))
        predicted_price = round(float(np.expm1(predicted_price[0])), 2)

        results.append({

            "medicine": row["brand_name"],

            "manufacturer": row["manufacturer"],

            "actual_price": round(float(row["price_inr"]), 2),

            "predicted_price": round(predicted_price, 2)

        })

    return {

        "searched_medicine": {

            "name": medicine["brand_name"],

            "manufacturer": medicine["manufacturer"],

            "actual_price": round(float(medicine["price_inr"]), 2),

            "predicted_price": predict_price(medicine["brand_name"]),

            "composition": medicine["cleaned_composition"]

        },

        "alternatives": results

    }