# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import os

# Load dataset
df = pd.read_csv('./dataset_transformed.csv')

# Drop rows with missing values in critical columns
df.dropna(subset=['status', 'funding_total_usd', 'country_code'], inplace=True)

# Encode categorical columns
label_encoders = {}
for column in ['category_list', 'country_code', 'state_code', 'region', 'city', 'first_funding_at', 'last_funding_at', 'founded_at']:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column].astype(str))
    label_encoders[column] = le

# Convert 'status' to binary classification (1 for operating, 0 for closed)
df['status'] = df['status'].apply(lambda x: 0 if x == 'closed' else 1)

# Handle 'funding_total_usd' column (convert '-' to 0 and convert to float)
df['funding_total_usd'] = df['funding_total_usd'].replace('-', 0).astype(float)

# Features and target
X = df.drop(columns=['status'])
y = df['status']

# Standardize the features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Save the scaler and label encoders
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')

# Define the MLP model
def build_mlp_model(input_dim):
    model = Sequential()
    model.add(Dense(20, activation='relu', input_dim=input_dim))
    model.add(Dropout(0.5))
    model.add(Dense(25, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Split the data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Build and train the MLP model
mlp_model = build_mlp_model(X_train.shape[1])

# Define callbacks for early stopping and model checkpointing
checkpoint_path = "./mlp_model_checkpoint.weights.h5"
os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
checkpoint = ModelCheckpoint(checkpoint_path, monitor='val_loss', save_best_only=True, save_weights_only=True)
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model
history = mlp_model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2, verbose=1, callbacks=[checkpoint, early_stopping])

# Evaluate the model on the test set
test_loss, test_accuracy = mlp_model.evaluate(X_test, y_test, verbose=0)

print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")

# Save the final model
mlp_model.save('mlp_model.h5')
print("MLP model training complete and saved.")
