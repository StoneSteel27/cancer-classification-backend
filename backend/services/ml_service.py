import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from flask import current_app


class MLService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            with current_app.app_context():
                self._model = tf.keras.models.load_model(current_app.config['MODEL_PATH'])
                self.image_size = current_app.config['IMAGE_SIZE']
                self.class_labels = current_app.config['CLASS_LABELS']

    def predict_image(self, image_file):
        try:
            img = Image.open(image_file).convert('RGB')
            img = img.resize(self.image_size)
            img_array = img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            pred_prob = self._model.predict(img_array)[0][0]
            class_idx = 1 if pred_prob > 0.5 else 0
            class_label = self.class_labels[class_idx]
            confidence = pred_prob if class_idx == 1 else (1 - pred_prob)

            return {
                'prediction': class_label,
                'confidence': float(confidence * 100)
            }
        except Exception as e:
            return {'error': str(e)}
