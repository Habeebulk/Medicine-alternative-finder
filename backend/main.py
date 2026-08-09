from fastapi import FastAPI, HTTPException
from fastapi import Query

from predict import find_alternatives
from predict import clean_df

from schemas import MedicineRequest

app = FastAPI(
    title="Medicine Price Predictor",
    version="1.0.0"
)

@app.get("/")
def home():

    return {
        "message": "Medicine Price Predictor API"
    }

@app.post("/predict")
def predict(request: MedicineRequest):

    result = find_alternatives(
        request.medicine_name
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    return result

@app.get("/search")
def search_medicine(query: str = Query(..., min_length=1)):

    query = query.strip().lower()
    query = " ".join(query.split())

    matches = clean_df[
        clean_df["brand_name"]
        .str.lower()
        .str.startswith(query)
    ]["brand_name"]

    return (
        matches
        .drop_duplicates()
        .sort_values()
        .head(10)
        .tolist()
    )