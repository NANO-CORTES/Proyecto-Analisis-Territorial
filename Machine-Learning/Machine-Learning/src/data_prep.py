import pandas as pd
import json
import os

def load_and_clean_data(root_path: str):
    """
    Carga y limpia los datos de los CSV y JSON del proyecto.
    """

    df_edu = pd.read_csv(os.path.join(root_path, 'territorio_educacion.csv'))
    df_socio = pd.read_csv(os.path.join(root_path, 'territorio_socioeconomico.csv'))

    with open(os.path.join(root_path, 'territorio_infraestructura.json'), 'r') as f:
        infra_data = json.load(f)
    df_infra = pd.DataFrame(infra_data)

    with open(os.path.join(root_path, 'territorio_salud.json'), 'r') as f:
        salud_data = json.load(f)
    df_salud = pd.DataFrame(salud_data)

    df_edu['zone_code'] = df_edu['zone_code'].astype(str)
    df_socio['zone_code'] = df_socio['zone_code'].astype(str)
    df_infra['zone_code'] = df_infra['zone_code'].astype(str)
    df_salud['zone_code'] = df_salud['zone_code'].astype(str)

    df_merged = pd.merge(df_edu, df_socio, on=['zone_code', 'zone_name'], how='outer')
    df_merged = pd.merge(df_merged, df_infra, on=['zone_code', 'zone_name'], how='outer')
    df_merged = pd.merge(df_merged, df_salud, on=['zone_code', 'zone_name'], how='outer')

    numeric_cols = df_merged.select_dtypes(include=['number']).columns
    df_merged[numeric_cols] = df_merged[numeric_cols].fillna(df_merged[numeric_cols].median())

    df_merged['zone_name'] = df_merged['zone_name'].str.strip().str.title()

    return df_merged

if __name__ == "__main__":
    root = r'c:\Users\felip\OneDrive\Documents\Proyecto-Analisis-Territorial'
    df = load_and_clean_data(root)
    print("Datos cargados exitosamente:")
    print(df.head())
    print("\nColumnas disponibles:", df.columns.tolist())

    output_path = os.path.join(os.path.dirname(__file__), '..', 'processed_data.csv')
    df.to_csv(output_path, index=False)
    print(f"\nDatos procesados guardados en: {output_path}")
