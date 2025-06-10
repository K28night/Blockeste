import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from sklearn.preprocessing import StandardScaler

# ✅ Load trained model with error handling
try:
    model = load_model("house_price_model.h5", custom_objects={"mse": MeanSquaredError()})
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# ✅ Load encoders and scaler with error handling
try:
    with open("encoders_scaler.pkl", "rb") as f:
        data_dict = pickle.load(f)

    label_encoders = data_dict["encoders"]
    scaler = data_dict["scaler"]
    print("✅ Encoders and scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading encoders/scaler: {e}")
    exit()

# ✅ Function to preprocess user input
def preprocess_input(user_input):
    categorical_cols = ['State', 'City', 'Locality', 'Property_Type', 'Furnished_Status', 
                        'Facing', 'Owner_Type', 'Availability_Status', 
                        'Public_Transport_Accessibility', 'Parking_Space', 'Security']
    
    # Encode categorical inputs
    for col in categorical_cols:
        if col in user_input:
            if user_input[col] in label_encoders[col].classes_:
                user_input[col] = label_encoders[col].transform([user_input[col]])[0]
            else:
                print(f"⚠ Warning: {user_input[col]} not found in training data. Using default 0.")
                user_input[col] = 0  # Default to 0 if unseen category

    # Convert to NumPy array and reshape
    input_features = np.array([list(user_input.values())], dtype=np.float32)

    # Scale the data
    input_features = scaler.transform(input_features)

    # Reshape for LSTM (batch_size, time_steps, features)
    input_features = input_features.reshape((1, 1, input_features.shape[1]))  

    return input_features

# # ✅ Example user input
# user_input = {
#     "Size_in_SqFt": 3000,
#     "Price_per_SqFt": 0.05,
#     "Year_Built": 2010,
#     "Floor_No": 5,
#     "Total_Floors": 10,
#     "Age_of_Property": 13,
#     "Nearby_Schools": 8,
#     "Nearby_Hospitals": 4,
#     "State": "Tamil Nadu",
#     "City": "Chennai",
#     "Locality": "Locality_84",
#     "Property_Type": "Apartment",
#     "Furnished_Status": "Semi-furnished",
#     "Facing": "East",
#     "Owner_Type": "Owner",
#     "Availability_Status": "Ready_to_Move",
#     "Public_Transport_Accessibility": "High",
#     "Parking_Space": "Yes",
#     "Security": "Yes"
# }

# # ✅ Preprocess and predict
# input_data = preprocess_input(user_input)

# # ✅ Make prediction with error handling
# try:
#     predicted_price = model.predict(input_data)
#     print(f"🏠 Predicted House Price: ₹{predicted_price[0][0]:.2f} Lakhs")
# except Exception as e:
#     print(f"❌ Error during prediction: {e}")
