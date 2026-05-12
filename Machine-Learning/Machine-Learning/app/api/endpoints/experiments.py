from fastapi import APIRouter, Depends, HTTPException
from typing import List
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.models.ml import MLExperiment, TrainedModel
from app.schemas.ml import ExperimentCreate, ExperimentResponse
from app.interfaces.experiment_repository import IExperimentRepository
from app.api.deps import get_experiment_repo

router = APIRouter()

MODELS_DIR = "/app/storage/models"


@router.post("/", response_model=ExperimentResponse)
def run_experiment(
    exp_req: ExperimentCreate,
    repo: IExperimentRepository = Depends(get_experiment_repo),
):
    data_records = repo.get_transformed_data(exp_req.transformation_run_id)

    if not data_records:
        raise HTTPException(status_code=404, detail="No transformed data found for the given run_id")

    df = pd.DataFrame([{
        "population_density": r.population_density,
        "average_income": r.average_income,
        "education_level": r.education_level,
        "economic_activity_index": r.economic_activity_index,
        "commercial_presence_index": r.commercial_presence_index
    } for r in data_records])

    features = [
        "population_density",
        "average_income",
        "education_level",
        "economic_activity_index",
        "commercial_presence_index"
    ]
    df = df.dropna(subset=features)

    if len(df) < 10:
        raise HTTPException(status_code=400, detail="Not enough valid data points for training")

    if exp_req.target_variable not in features:
        if exp_req.target_variable == "territorial_score":
            df['territorial_score'] = (
                0.3 * (df['education_level'] / 100) +
                0.3 * (df['average_income'] / df['average_income'].max()) +
                0.2 * (df['economic_activity_index'] / df['economic_activity_index'].max()) +
                0.2 * (df['commercial_presence_index'] / df['commercial_presence_index'].max())
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid target variable")

    target_col = exp_req.target_variable
    X_features = [f for f in features if f != target_col]

    X = df[X_features]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if exp_req.algorithm == "linear_regression":
        model = LinearRegression()
    elif exp_req.algorithm == "random_forest":
        model = RandomForestRegressor(random_state=42)
    elif exp_req.algorithm == "gradient_boosting":
        model = GradientBoostingRegressor(random_state=42)
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    new_exp = MLExperiment(
        transformation_run_id=exp_req.transformation_run_id,
        algorithm=exp_req.algorithm,
        target_variable=exp_req.target_variable,
        features_used=X_features,
        r2_score=float(r2),
        mae=float(mae),
        rmse=float(rmse),
        status="COMPLETED"
    )
    new_exp = repo.create_experiment(new_exp)

    os.makedirs(MODELS_DIR, exist_ok=True)
    model_filename = f"model_{new_exp.id}.joblib"
    model_path = os.path.join(MODELS_DIR, model_filename)
    joblib.dump(model, model_path)

    new_trained_model = TrainedModel(
        experiment_id=new_exp.id,
        storage_path=model_path,
        is_active=False
    )
    repo.create_trained_model(new_trained_model)
    new_exp = repo.get_experiment_by_id(new_exp.id)

    return new_exp


@router.get("/", response_model=List[ExperimentResponse])
def get_experiments(
    repo: IExperimentRepository = Depends(get_experiment_repo),
):
    return repo.get_all_experiments()


@router.patch("/{experiment_id}/activate", response_model=ExperimentResponse)
def activate_experiment(
    experiment_id: str,
    repo: IExperimentRepository = Depends(get_experiment_repo),
):
    exp = repo.get_experiment_by_id(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    repo.activate_experiment_models(experiment_id)

    exp = repo.get_experiment_by_id(experiment_id)
    return exp
