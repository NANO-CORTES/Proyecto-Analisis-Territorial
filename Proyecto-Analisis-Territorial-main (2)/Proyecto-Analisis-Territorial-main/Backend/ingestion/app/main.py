from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <--- 1. IMPORTACIÓN NUEVA
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.core.security import get_current_user
from app.models.dataset import DatasetLoad
import pandas as pd
import io
from sqlalchemy import text

# --- Mantenemos tu configuración de esquema ---
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS ingestion"))
    con.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ingestion Service")

# <--- 2. BLOQUE NUEVO: ESTO ARREGLA EL 'FAILED TO FETCH' --->
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service_name": "ms-ingestion"}

# --- Endpoint mejorado para cumplir el Sprint 1 ---
@app.post("/api/v1/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validación de extensión (Requisito HU-01)
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .csv")

    try:
        # Leer el contenido del archivo
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # 2. Validación de columnas obligatorias (Requisito HU-02)
        required_columns = ['zone_code', 'zone_name']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Estructura inválida. Faltan columnas: {required_columns}"
            )

        # 3. Validación de calidad: Máximo 30% de nulos (Requisito HU-02)
        max_null_ratio = df.isnull().mean().max()
        if max_null_ratio > 0.30:
            raise HTTPException(
                status_code=400, 
                detail=f"Calidad de datos baja. Una columna supera el 30% de nulos ({max_null_ratio:.2%})"
            )

        # 4. Guardar metadatos
        new_dataset = DatasetLoad(
            user_id=current_user["username"],
            file_name=file.filename,
        )
        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)

        return {
            "success": True,
            "message": "Dataset validado y cargado con éxito",
            "info": {
                "rows_processed": len(df),
                "null_ratio": f"{max_null_ratio:.2%}"
            },
            "data": {
                "dataset_id": new_dataset.id,
                "file_name": new_dataset.file_name,
                "uploaded_by": current_user["username"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {str(e)}")