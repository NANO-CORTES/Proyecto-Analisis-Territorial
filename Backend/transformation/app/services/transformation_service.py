import os
import json
import uuid
import logging
from typing import Dict, List, Any, Tuple

import numpy as np
import pandas as pd

from app.core.config import settings
from app.core.exceptions import DomainException
from app.models.models import TransformationRun, TransformedRecord
from app.interfaces.transformation_repo import ITransformationRepository

logger = logging.getLogger("TransformationService")


def loadDatasetFile(fileName: str) -> pd.DataFrame:
    filePath = os.path.join(settings.STORAGE_PATH, fileName)

    if not os.path.exists(filePath):
        raise DomainException(f"Archivo '{fileName}' no encontrado en storage.", status_code=404)

    ext = os.path.splitext(fileName)[1].lower()

    if ext == ".csv":
        try:
            df = pd.read_csv(filePath)
        except Exception:
            df = pd.read_csv(filePath, sep=";")
    elif ext == ".json":
        with open(filePath, "r", encoding="utf-8") as f:
            parsed = json.load(f)
        df = pd.DataFrame(parsed)
    else:
        raise DomainException(f"Extensión '{ext}' no soportada.", status_code=400)

    if df.empty:
        raise DomainException("El archivo está vacío o no contiene registros.", status_code=400)

    df.columns = [str(c).lower().strip() for c in df.columns]
    return df


def cleanDataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    nonKeyCols = [c for c in df.columns if c not in ("zone_code", "zone_name")]
    for col in nonKeyCols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    numericCols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numericCols:
        medianVal = df[col].median()
        if pd.notna(medianVal):
            df[col] = df[col].fillna(medianVal)

    if "zone_code" in df.columns:
        df = df.drop_duplicates(subset=["zone_code"], keep="last")

    if "zone_name" in df.columns:
        df["zone_name"] = df["zone_name"].astype(str).str.strip().str.title()

    df = df.reset_index(drop=True)
    return df


def detectAndWinsorizeOutliers(
    df: pd.DataFrame,
    numericCols: List[str],
    zThreshold: float = 3.0,
    lowerPercentile: float = 0.01,
    upperPercentile: float = 0.99,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    df = df.copy()
    outliersCount: Dict[str, int] = {}

    for col in numericCols:
        series = df[col]
        mean = series.mean()
        std = series.std()

        if std == 0 or pd.isna(std):
            outliersCount[col] = 0
            continue

        isOutlier = (series - mean).abs() > (zThreshold * std)
        count = int(isOutlier.sum())
        outliersCount[col] = count

        if count > 0:
            lowerBound = series.quantile(lowerPercentile)
            upperBound = series.quantile(upperPercentile)
            df[col] = series.clip(lower=lowerBound, upper=upperBound)

    return df, outliersCount


def normalizeMinmax(df: pd.DataFrame, numericCols: List[str]) -> pd.DataFrame:
    df = df.copy()
    for col in numericCols:
        colMin = df[col].min()
        colMax = df[col].max()
        if colMax - colMin == 0:
            df[col] = 0.0
        else:
            df[col] = (df[col] - colMin) / (colMax - colMin)
    return df


def normalizeZscore(df: pd.DataFrame, numericCols: List[str]) -> pd.DataFrame:
    df = df.copy()
    for col in numericCols:
        mean = df[col].mean()
        std = df[col].std()
        if std == 0 or pd.isna(std):
            df[col] = 0.0
        else:
            df[col] = (df[col] - mean) / std
    return df


def generateStatsReport(
    df: pd.DataFrame,
    numericCols: List[str],
    nullCounts: Dict[str, int],
    outliersCounts: Dict[str, int],
) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    for col in numericCols:
        report[col] = {
            "min": round(float(df[col].min()), 6),
            "max": round(float(df[col].max()), 6),
            "mean": round(float(df[col].mean()), 6),
            "std": round(float(df[col].std()), 6),
            "null_count": nullCounts.get(col, 0),
            "outliers_count": outliersCounts.get(col, 0),
        }
    return report


def processAdvancedTransformation(
    repo: ITransformationRepository,
    datasetLoadId: str,
    method: str = "minmax",
) -> TransformationRun:
    datasetInfo = repo.getDatasetInfo(datasetLoadId)
    if datasetInfo is None:
        raise DomainException(f"Dataset con ID '{datasetLoadId}' no encontrado.", status_code=404)

    if datasetInfo["status"] != "VALID":
        raise DomainException(f"Solo se pueden transformar datasets con estado 'VALID'.", status_code=400)

    fileName = datasetInfo["file_name"]
    dfRaw = loadDatasetFromStorage(fileName)
    recordsInput = len(dfRaw)

    nonKeyCols = [c for c in dfRaw.columns if c not in ("zone_code", "zone_name")]
    for col in nonKeyCols:
        dfRaw[col] = pd.to_numeric(dfRaw[col], errors="coerce")
    numericCols = dfRaw.select_dtypes(include=[np.number]).columns.tolist()
    nullCounts = {col: int(dfRaw[col].isnull().sum()) for col in numericCols}

    dfClean = cleanDataframe(dfRaw)
    numericCols = dfClean.select_dtypes(include=[np.number]).columns.tolist()

    dfWinsorized, outliersCounts = detectAndWinsorizeOutliers(dfClean, numericCols)

    if method == "minmax":
        dfNormalized = normalizeMinmax(dfWinsorized, numericCols)
    elif method == "zscore":
        dfNormalized = normalizeZscore(dfWinsorized, numericCols)
    else:
        raise DomainException(f"Método '{method}' no soportado.", status_code=400)

    recordsOutput = len(dfNormalized)

    statsReport = generateStatsReport(dfNormalized, numericCols, nullCounts, outliersCounts)

    report = {
        "method": method,
        "total_columns_processed": len(numericCols),
        "columns_processed": numericCols,
        "statistics": statsReport,
    }

    run = TransformationRun(
        id=str(uuid.uuid4()),
        dataset_load_id=datasetLoadId,
        method=method,
        status="COMPLETED",
        rules_applied=report,
        records_input=recordsInput,
        records_output=recordsOutput,
    )

    transformedRecords = []
    for _, row in dfNormalized.iterrows():
        zoneCode = str(row.get("zone_code", ""))
        zoneName = str(row.get("zone_name", ""))
        for col in numericCols:
            originalVal = dfWinsorized.loc[dfWinsorized["zone_code"].astype(str) == zoneCode, col]
            orig = float(originalVal.iloc[0]) if len(originalVal) > 0 else None

            transformedRecords.append(TransformedRecord(
                id=str(uuid.uuid4()),
                run_id=run.id,
                zone_code=zoneCode,
                zone_name=zoneName,
                column_name=col,
                original_value=orig,
                normalized_value=float(row[col]) if pd.notna(row[col]) else None,
            ))

    run = repo.createRun(run, transformedRecords)

    logger.info(
        f"Transformación completada: run_id={run.id}, method={method}, "
        f"records_in={recordsInput}, records_out={recordsOutput}"
    )

    return run


def loadDatasetFromStorage(originalFileName: str) -> pd.DataFrame:
    storagePath = settings.STORAGE_PATH

    if not os.path.exists(storagePath):
        raise DomainException(f"Directorio de storage '{storagePath}' no existe.", status_code=500)

    originalPath = os.path.join(storagePath, originalFileName)
    if os.path.exists(originalPath):
        return loadDatasetFile(originalFileName)

    ext = os.path.splitext(originalFileName)[1].lower()
    files = [
        f for f in os.listdir(storagePath)
        if f.endswith(ext) and os.path.isfile(os.path.join(storagePath, f))
    ]

    if not files:
        raise DomainException(f"No se encontraron archivos en storage para '{originalFileName}'.", status_code=404)

    files.sort(key=lambda f: os.path.getmtime(os.path.join(storagePath, f)), reverse=True)
    return loadDatasetFile(files[0])
