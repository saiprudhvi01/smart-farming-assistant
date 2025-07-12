import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import pickle
import warnings
warnings.filterwarnings('ignore')

def create_enhanced_dataset():
    """Create enhanced dataset with water resource integration"""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    crops_data = []
    
    # High water requirement crops
    high_water_crops = [
        {'crop': 'rice', 'temp_range': (26, 30), 'humidity_range': (80, 95), 'N_range': (100, 140), 'P_range': (40, 60), 'K_range': (40, 70), 'pH_range': (5.5, 7.0), 'rainfall_range': (1200, 1800)},
        {'crop': 'sugarcane', 'temp_range': (30, 35), 'humidity_range': (70, 90), 'N_range': (120, 160), 'P_range': (30, 50), 'K_range': (60, 100), 'pH_range': (6.0, 7.5), 'rainfall_range': (1000, 1500)}
    ]
    
    # Low water requirement crops
    low_water_crops = [
        {'crop': 'millet', 'temp_range': (32, 38), 'humidity_range': (40, 65), 'N_range': (40, 80), 'P_range': (15, 35), 'K_range': (20, 50), 'pH_range': (5.5, 7.5), 'rainfall_range': (200, 500)},
        {'crop': 'barley', 'temp_range': (15, 22), 'humidity_range': (45, 70), 'N_range': (60, 100), 'P_range': (20, 40), 'K_range': (30, 60), 'pH_range': (6.0, 7.5), 'rainfall_range': (300, 600)}
    ]
    
    # Moderate water requirement crops
    moderate_water_crops = [
        {'crop': 'wheat', 'temp_range': (18, 25), 'humidity_range': (50, 75), 'N_range': (70, 120), 'P_range': (25, 45), 'K_range': (30, 60), 'pH_range': (6.0, 7.5), 'rainfall_range': (400, 800)},
        {'crop': 'maize', 'temp_range': (22, 28), 'humidity_range': (60, 80), 'N_range': (90, 130), 'P_range': (50, 80), 'K_range': (35, 65), 'pH_range': (5.8, 7.2), 'rainfall_range': (600, 1000)},
        {'crop': 'cotton', 'temp_range': (25, 35), 'humidity_range': (55, 80), 'N_range': (120, 180), 'P_range': (25, 45), 'K_range': (100, 150), 'pH_range': (5.8, 8.0), 'rainfall_range': (500, 900)},
        {'crop': 'tomato', 'temp_range': (20, 28), 'humidity_range': (60, 80), 'N_range': (80, 120), 'P_range': (60, 90), 'K_range': (60, 100), 'pH_range': (6.0, 7.0), 'rainfall_range': (400, 700)},
        {'crop': 'potato', 'temp_range': (15, 22), 'humidity_range': (70, 90), 'N_range': (100, 150), 'P_range': (50, 80), 'K_range': (80, 120), 'pH_range': (5.5, 6.5), 'rainfall_range': (400, 600)},
        {'crop': 'onion', 'temp_range': (20, 27), 'humidity_range': (50, 70), 'N_range': (70, 110), 'P_range': (35, 55), 'K_range': (50, 80), 'pH_range': (6.0, 7.5), 'rainfall_range': (600, 900)}
    ]
    
    # Generate data for high water crops
    for crop_info in high_water_crops:
        for i in range(200):  # More samples for better accuracy
            crops_data.append({
                'temperature': np.random.uniform(*crop_info['temp_range']),
                'humidity': np.random.uniform(*crop_info['humidity_range']),
                'N': np.random.uniform(*crop_info['N_range']),
                'P': np.random.uniform(*crop_info['P_range']),
                'K': np.random.uniform(*crop_info['K_range']),
                'pH': np.random.uniform(*crop_info['pH_range']),
                'rainfall': np.random.uniform(*crop_info['rainfall_range']),
                'water_resource': 'high',
                'crop': crop_info['crop']
            })
    
    # Generate data for low water crops
    for crop_info in low_water_crops:
        for i in range(200):
            crops_data.append({
                'temperature': np.random.uniform(*crop_info['temp_range']),
                'humidity': np.random.uniform(*crop_info['humidity_range']),
                'N': np.random.uniform(*crop_info['N_range']),
                'P': np.random.uniform(*crop_info['P_range']),
                'K': np.random.uniform(*crop_info['K_range']),
                'pH': np.random.uniform(*crop_info['pH_range']),
                'rainfall': np.random.uniform(*crop_info['rainfall_range']),
                'water_resource': 'low',
                'crop': crop_info['crop']
            })
    
    # Generate data for moderate water crops (both high and low water scenarios)
    for crop_info in moderate_water_crops:
        for water_type in ['high', 'low']:
            for i in range(100):
                # Adjust rainfall based on water availability
                if water_type == 'high':
                    rainfall_factor = 1.2
                else:
                    rainfall_factor = 0.8
                
                crops_data.append({
                    'temperature': np.random.uniform(*crop_info['temp_range']),
                    'humidity': np.random.uniform(*crop_info['humidity_range']),
                    'N': np.random.uniform(*crop_info['N_range']),
                    'P': np.random.uniform(*crop_info['P_range']),
                    'K': np.random.uniform(*crop_info['K_range']),
                    'pH': np.random.uniform(*crop_info['pH_range']),
                    'rainfall': np.random.uniform(*crop_info['rainfall_range']) * rainfall_factor,
                    'water_resource': water_type,
                    'crop': crop_info['crop']
                })
    
    df = pd.DataFrame(crops_data)
    
    # Ensure all values are within realistic ranges
    df['temperature'] = np.clip(df['temperature'], 10, 45)
    df['humidity'] = np.clip(df['humidity'], 30, 95)
    df['N'] = np.clip(df['N'], 20, 200)
    df['P'] = np.clip(df['P'], 10, 100)
    df['K'] = np.clip(df['K'], 15, 180)
    df['pH'] = np.clip(df['pH'], 5.0, 8.5)
    df['rainfall'] = np.clip(df['rainfall'], 200, 2000)
    
    return df

def train_enhanced_model():
    """Train enhanced model with water resource integration"""
    
    print("Creating enhanced dataset with water resource integration...")
    df = create_enhanced_dataset()
    
    # Save the dataset
    df.to_csv('data/enhanced_crop_data.csv', index=False)
    print("Enhanced dataset saved to data/enhanced_crop_data.csv")
    print(f"Dataset shape: {df.shape}")
    print(f"Unique crops: {df['crop'].nunique()}")
    print(f"Crop distribution:\n{df['crop'].value_counts()}")
    
    # Encode water resource
    le = LabelEncoder()
    df['water_resource_encoded'] = le.fit_transform(df['water_resource'])
    
    # Features and target
    X = df[['temperature', 'humidity', 'N', 'P', 'K', 'pH', 'rainfall', 'water_resource_encoded']]
    y = df['crop']
    
    # Split data with stratification
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train optimized Random Forest
    print("Training Enhanced Random Forest with hyperparameter tuning...")
    rf_model = RandomForestClassifier(
        n_estimators=500,
        max_depth=20,
        min_samples_split=3,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    
    print(f"Enhanced Random Forest Accuracy: {rf_accuracy:.3f}")
    
    # Save the model and encoder
    with open('enhanced_crop_model.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    
    with open('water_resource_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
    
    print("Enhanced model saved as enhanced_crop_model.pkl")
    print("Water resource encoder saved as water_resource_encoder.pkl")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, rf_pred))
    
    # Feature importance
    feature_names = ['temperature', 'humidity', 'N', 'P', 'K', 'pH', 'rainfall', 'water_resource']
    feature_importance = rf_model.feature_importances_
    
    print("\nFeature Importance:")
    for name, importance in zip(feature_names, feature_importance):
        print(f"{name}: {importance:.3f}")
    
    return rf_model, le

if __name__ == "__main__":
    model, encoder = train_enhanced_model()
