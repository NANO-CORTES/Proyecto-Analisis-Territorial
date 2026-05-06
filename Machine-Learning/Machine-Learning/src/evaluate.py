import pandas as pd
from sklearn.metrics import silhouette_score, mean_squared_error, r2_score
import joblib
import os

def evaluate():
    results_path = os.path.join(os.path.dirname(__file__), '..', 'results_with_ml.csv')
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    
    if not os.path.exists(results_path):
        print("Error: No se encontró results_with_ml.csv. Ejecuta train.py primero.")
        return

    df = pd.read_csv(results_path)
    scaler = joblib.load(os.path.join(models_dir, 'scaler.joblib'))
    
    features = [
        'tasa_alfabetismo', 'cobertura_primaria', 'cobertura_secundaria',
        'poblacion_total', 'indice_pobreza', 'tasa_desempleo',
        'acceso_agua_potable', 'acceso_electricidad', 'acceso_internet'
    ]
    X_scaled = scaler.transform(df[features])

    sil_score = silhouette_score(X_scaled, df['cluster'])
    print(f"--- Evaluación de Clustering ---")
    print(f"Silhouette Score: {sil_score:.4f} (Ideal cercano a 1)")
    
    y_true = (
        0.3 * (df['tasa_alfabetismo'] / 100) + 
        0.3 * (1 - df['indice_pobreza'] / 100) + 
        0.2 * (df['acceso_internet'] / 100) +
        0.2 * (1 - df['tasa_desempleo'] / 100)
    )
    y_pred = df['predicted_score']
    
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    print(f"\n--- Evaluación de Regresión ---")
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")

    print(f"\n--- Resumen por Cluster ---")
    print(df.groupby('cluster')[['predicted_score', 'indice_pobreza', 'acceso_internet']].mean())

if __name__ == "__main__":
    evaluate()
