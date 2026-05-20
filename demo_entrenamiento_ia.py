# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def entrenar_modelos():
    print("="*60)
    print("[IA] INICIANDO ENTRENAMIENTO - ANALISIS TERRITORIAL")
    print("="*60)

    # 1. Carga de Datos
    print("\n[1/5] Cargando dataset de exposicion...")
    try:
        df = pd.read_csv('dataset_exposicion_ia.csv')
        print(f"  >> Datos cargados correctamente. Zonas encontradas: {len(df)}")
    except Exception as e:
        print(f"  >> ERROR al cargar datos: {e}")
        return

    features = [
        'population_density', 'average_income', 'education_level',
        'economic_activity_index', 'commercial_presence_index',
        'tasa_desempleo', 'indice_pobreza_multidimensional'
    ]
    print(f"  >> Caracteristicas (Features) seleccionadas: {len(features)}")
    X = df[features].copy()

    # 2. Preprocesamiento
    print("\n[2/5] Preprocesando y escalando datos (MinMaxScaler 0-1)...")
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    print("  >> Datos escalados correctamente.")

    # 3. Clustering (No Supervisado)
    print("\n[3/5] Entrenando modelo de Clustering (K-Means, 4 clusters)...")
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['cluster_ia'] = kmeans.fit_predict(X_scaled)
    print("  >> Zonas agrupadas en 4 clusters segun similitudes socioeconomicas.")

    # Mostrar centros de clusters
    print("\n  Centros de los clusters (valores escalados):")
    centros = pd.DataFrame(kmeans.cluster_centers_, columns=features)
    for i, row in centros.iterrows():
        ing_prom = row['average_income']
        pob_prom = row['indice_pobreza_multidimensional']
        nivel = "ALTO" if ing_prom > 0.6 else ("MEDIO" if ing_prom > 0.35 else ("BAJO" if ing_prom > 0.15 else "CRITICO"))
        print(f"    Cluster {i} -> Nivel: {nivel:8s} | Ingreso normalizado: {ing_prom:.2f} | Pobreza normalizada: {pob_prom:.2f}")

    # 4. Funcion objetivo
    print("\n[4/5] Calculando Score Territorial objetivo (funcion ponderada)...")
    ingreso_norm  = X['average_income'] / X['average_income'].max()
    edu_norm      = X['education_level'] / X['education_level'].max()
    eco_norm      = X['economic_activity_index'] / X['economic_activity_index'].max()
    desempleo_inv = 1 - (X['tasa_desempleo'] / X['tasa_desempleo'].max())
    pobreza_inv   = 1 - (X['indice_pobreza_multidimensional'] / X['indice_pobreza_multidimensional'].max())

    y_target = (ingreso_norm * 0.25) + (edu_norm * 0.2) + (eco_norm * 0.2) + (desempleo_inv * 0.2) + (pobreza_inv * 0.15)
    y_target = y_target * 100
    print(f"  >> Score min: {y_target.min():.1f} | Score max: {y_target.max():.1f} | Promedio: {y_target.mean():.1f}")

    # 5. Regresion Lineal (Supervisado)
    print("\n[5/5] Entrenando modelo de Regresion Lineal...")
    reg_model = LinearRegression()
    reg_model.fit(X_scaled, y_target)
    df['score_predicho_ia'] = reg_model.predict(X_scaled).round(2)
    print("  >> Modelo de regresion entrenado. Predicciones completadas.")

    # Mostrar coeficientes del modelo
    print("\n  Pesos internos aprendidos por la IA (coeficientes):")
    for feat, coef in zip(features, reg_model.coef_):
        barra = "*" * int(abs(coef) / 2)
        print(f"    {feat:38s}: {coef:+.2f}  {barra}")

    # Resultados
    print("\n" + "="*60)
    print("RESULTADOS DEL ENTRENAMIENTO DE LA IA")
    print("="*60)

    resultados = df[['zone_name', 'cluster_ia', 'score_predicho_ia']].sort_values(
        by='score_predicho_ia', ascending=False
    )

    print("\n  TOP 3 - Mejores Zonas segun la IA:")
    print(f"  {'Zona':<25} {'Cluster':>8} {'Score IA':>10}")
    print(f"  {'-'*25} {'-'*8} {'-'*10}")
    for _, row in resultados.head(3).iterrows():
        print(f"  {row['zone_name']:<25} {int(row['cluster_ia']):>8} {row['score_predicho_ia']:>10.2f}")

    print("\n  BOTTOM 3 - Zonas que requieren atencion urgente:")
    print(f"  {'Zona':<25} {'Cluster':>8} {'Score IA':>10}")
    print(f"  {'-'*25} {'-'*8} {'-'*10}")
    for _, row in resultados.tail(3).iterrows():
        print(f"  {row['zone_name']:<25} {int(row['cluster_ia']):>8} {row['score_predicho_ia']:>10.2f}")

    df.to_csv('resultado_entrenamiento.csv', index=False)
    print("\n  >> Resultados guardados en 'resultado_entrenamiento.csv'")
    print("\n" + "="*60)
    print("  ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    entrenar_modelos()
