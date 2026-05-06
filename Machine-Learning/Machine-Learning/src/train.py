import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_models():
    
    data_path = os.path.join(os.path.dirname(__file__), '..', 'processed_data.csv')
    if not os.path.exists(data_path):
        print("Error: No se encontró processed_data.csv. Ejecuta data_prep.py primero.")
        return

    df = pd.read_csv(data_path)

    features = [
        'tasa_alfabetismo', 'cobertura_primaria', 'cobertura_secundaria',
        'poblacion_total', 'indice_pobreza', 'tasa_desempleo',
        'acceso_agua_potable', 'acceso_electricidad', 'acceso_internet'
    ]
    
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    y = (
        0.3 * (df['tasa_alfabetismo'] / 100) + 
        0.3 * (1 - df['indice_pobreza'] / 100) + 
        0.2 * (df['acceso_internet'] / 100) +
        0.2 * (1 - df['tasa_desempleo'] / 100)
    )
    
    reg = LinearRegression()
    reg.fit(X_scaled, y)
    
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(kmeans, os.path.join(models_dir, 'clustering_model.joblib'))
    joblib.dump(reg, os.path.join(models_dir, 'regression_model.joblib'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.joblib'))
    
    print("Modelos entrenados y guardados exitosamente en la carpeta /models")

    df['predicted_score'] = reg.predict(X_scaled)
    df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'results_with_ml.csv'), index=False)

if __name__ == "__main__":
    train_models()
