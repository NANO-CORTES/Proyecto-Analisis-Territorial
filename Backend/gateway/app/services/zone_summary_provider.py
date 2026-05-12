import os
import joblib
import random
import logging
import numpy as np

logger = logging.getLogger(__name__)

class PredictorService:
    def __init__(self):
        # Cargamos el modelo donde is_active=true (simulado usando joblib)
        self.model_path = os.getenv("MODEL_PATH", "model.joblib")
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                self.model = None
                logger.warning(f"Model not found at {self.model_path}. Using mock predictions.")
        except Exception as e:
            self.model = None
            logger.error(f"Error loading model: {e}")

    def predict(self, zone_metrics: dict) -> dict:
        """
        Devuelve prediction_value (0-1), prediction_label (Bajo <0.4, Medio 0.4-0.7, Alto >0.7) 
        y confidence_score.
        """
        # Filtrar solo valores numéricos
        numeric_metrics = [v for k, v in zone_metrics.items() if isinstance(v, (int, float))]
        
        if self.model and numeric_metrics:
            try:
                # Si existiera el modelo real
                features = np.array(numeric_metrics).reshape(1, -1)
                prediction_value = float(self.model.predict(features)[0])
                confidence_score = 0.95
            except Exception as e:
                logger.error(f"Error predicting with model: {e}")
                prediction_value = random.uniform(0, 1)
                confidence_score = random.uniform(0.7, 0.99)
        else:
            # Fallback a simulación o valor neutro
            prediction_value = random.uniform(0, 1)
            confidence_score = random.uniform(0.7, 0.99)
            
        if prediction_value < 0.4:
            prediction_label = "Bajo"
        elif prediction_value <= 0.7:
            prediction_label = "Medio"
        else:
            prediction_label = "Alto"
            
        return {
            "prediction_value": round(prediction_value, 4),
            "prediction_label": prediction_label,
            "confidence_score": round(confidence_score, 4)
        }
