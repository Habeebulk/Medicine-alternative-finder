# Medicine Alternative Finder

A full-stack Machine Learning application that predicts the expected market price of a medicine based on its characteristics and recommends cheaper medicines with the same active ingredients.

---

## Features

- Search medicines with autocomplete
- Predict the expected market price using a LightGBM regression model
- Find cheaper alternatives with the same active ingredients
- Compare prices using an interactive chart
- FastAPI backend with REST API
- Streamlit frontend

---

## Tech Stack

### Machine Learning
- Python
- Pandas
- NumPy
- Scikit-learn
- LightGBM

### Backend
- FastAPI
- Pydantic

### Frontend
- Streamlit
- Plotly

---

## Dataset

The dataset contains information about medicines including:

- Brand Name
- Manufacturer
- Active Ingredients
- Dosage Form
- Strength
- Pack Size
- Therapeutic Class
- Price

The data was cleaned and preprocessed before training the model.

---

## Machine Learning Pipeline

1. Data Cleaning
2. Feature Engineering
3. One-Hot Encoding
4. Multi-Label Binarization of Ingredients
5. Composition Price Encoding
6. LightGBM Regression Model
7. Model Evaluation

---

## Model Performance

| Metric | Score |
|--------|------:|
| MAE | 111.17 |
| RMSE | 3109.66 |
| R² (Original price scale) Score | 0.1150 |
| Train R² (log-transformed target) Score | 0.8831 |
| Test R² (log-transformed target) Score | 0.8200 |

---

## Project Structure

```
Medicine-alternative-finder/

├── backend/
│   ├── main.py
│   ├── predict.py
│   └── schemas.py
│
├── frontend/
│   └── app.py
│
├── data/
├── models/
├── notebooks/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/Habeebulk/Medicine-alternative-finder.git
```

Move into the project

```bash
cd Medicine-alternative-finder
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Backend

```bash
cd backend

uvicorn main:app --reload
```

---

## Running the Frontend

```bash
cd frontend

streamlit run app.py
```

---

## API Endpoints

### Search Medicines

```
GET /search?query=cro
```

Returns medicine suggestions.

### Predict Price & Alternatives

```
POST /predict
```

Example request

```json
{
    "medicine_name": "Dolo 1000mg Tablet"
}
```

Returns

- Predicted Price
- Actual Price
- Alternative Medicines
- Price Comparison

---

## Future Improvements

- Better medicine search using semantic matching
- Medicine image support
- Drug interaction checker
- Pharmacy price comparison
- Deployment on cloud

---

## License

This project is intended for educational purposes.