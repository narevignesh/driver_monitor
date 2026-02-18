import cv2
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam


IMAGE_SIZE = (224, 224)


def build_model():
    base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False

    x = GlobalAveragePooling2D()(base_model.output)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.5)(x)
    output = Dense(1, activation="sigmoid")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(
        optimizer=Adam(learning_rate=0.0005),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def preprocess_frame(frame):
    resized = cv2.resize(frame, IMAGE_SIZE)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    normalized = rgb.astype(np.float32) / 255.0
    return np.expand_dims(normalized, axis=0)


def predict_frame(model, frame):
    input_tensor = preprocess_frame(frame)
    prediction = model.predict(input_tensor, verbose=0)
    return float(prediction[0][0])
