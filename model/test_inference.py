from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from datetime import datetime

app = FastAPI()

# Load the saved model, scaler, and label encoders
model = tf.keras.models.load_model('mlp_model.h5')
scaler = joblib.load('scaler.pkl')
label_encoders = joblib.load('label_encoders.pkl')

class Item(BaseModel):
    category_list: str
    funding_total_usd: str
    status: str
    country_code: str
    state_code: str
    region: str
    city: str
    funding_rounds: int
    founded_at: str
    first_funding_at: str
    last_funding_at: str

def preprocess_input(data):
    # Convert input data to DataFrame
    df = pd.DataFrame([data.dict()])

    # Encode categorical columns
    for column in ['category_list', 'country_code', 'state_code', 'region', 'city', 'first_funding_at', 'last_funding_at', 'founded_at']:
        le = label_encoders[column]
        df[column] = df[column].astype(str)
        df[column] = df[column].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)

    # Handle 'funding_total_usd' column (convert '-' to 0 and convert to float)
    df['funding_total_usd'] = df['funding_total_usd'].replace('-', 0).astype(float)

    # Standardize the features
    X = scaler.transform(df.drop(columns=['status']))

    return X

@app.post('/predict')
async def predict(item: Item):
    try:
        # Preprocess the input data
        X = preprocess_input(item)

        # Make predictions
        predictions = model.predict(X)

        # Convert predictions to class labels
        predictions = (predictions > 0.9).astype(int)

        return {'prediction': int(predictions[0][0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
