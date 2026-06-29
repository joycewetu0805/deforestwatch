"""
Architecture U-Net (TensorFlow/Keras) pour la segmentation sémantique.
Input : tuiles 128×128×6 → Output : masque 128×128×5 (softmax).

Si TensorFlow n'est pas installé, une implémentation de repli (segmentation
par plus proche centroïde spectral) fournit la même interface fit/predict afin
que le pipeline et le dashboard restent fonctionnels.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from config.settings import MODELS_DIR, NUM_CLASSES, UNET_PARAMS
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

log = get_logger("unet")


def build_unet(input_shape=(128, 128, 6), num_classes=NUM_CLASSES, filters=(32, 64, 128, 256)):
    """Construit le modèle U-Net Keras (encodeur/bottleneck/décodeur + skips)."""
    from tensorflow.keras import layers, Model

    def conv_block(x, f):
        x = layers.Conv2D(f, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.Conv2D(f, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        return x

    inp = layers.Input(input_shape)
    skips, x = [], inp
    for f in filters:
        c = conv_block(x, f)
        skips.append(c)
        x = layers.MaxPool2D()(c)
        x = layers.Dropout(0.3)(x)

    x = conv_block(x, filters[-1] * 2)  # bottleneck

    for f, skip in zip(reversed(filters), reversed(skips)):
        x = layers.Conv2DTranspose(f, 2, strides=2, padding="same")(x)
        x = layers.Concatenate()([x, skip])
        x = layers.Dropout(0.3)(x)
        x = conv_block(x, f)

    out = layers.Conv2D(num_classes, 1, activation="softmax")(x)
    return Model(inp, out, name="UNet")


class UNetModel:
    name = "U-Net"

    def __init__(self, **params):
        self.params = {**UNET_PARAMS, **params}
        self.model = None
        self._backend = None
        self._centroids = None  # repli

    def _ensure_model(self):
        if self.model is not None or self._backend == "fallback":
            return
        try:
            import tensorflow as tf  # noqa: F401

            self.model = build_unet(
                self.params["input_shape"], self.params["num_classes"],
                tuple(self.params["filters"]),
            )
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(self.params["learning_rate"]),
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"],
            )
            self._backend = "tensorflow"
            log.info("U-Net Keras construit.")
        except Exception as exc:
            log.warning(f"TensorFlow indisponible ({exc}) → repli centroïdes spectraux.")
            self._backend = "fallback"

    def fit(self, X, y, X_val=None, y_val=None, epochs=None):
        self._ensure_model()
        if self._backend == "tensorflow":
            import tensorflow as tf

            cbs = [
                tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5),
            ]
            val = (X_val, y_val) if X_val is not None else None
            self.model.fit(
                X, y, validation_data=val,
                epochs=epochs or self.params["epochs"],
                batch_size=self.params["batch_size"], callbacks=cbs, verbose=0,
            )
        else:
            # Repli : moyenne spectrale par classe (centroïdes)
            flatX = X.reshape(-1, X.shape[-1])
            flatY = y.reshape(-1)
            self._centroids = np.stack(
                [flatX[flatY == c].mean(0) if np.any(flatY == c) else np.zeros(X.shape[-1])
                 for c in range(NUM_CLASSES)]
            )
        log.info(f"{self.name} entraîné ({self._backend}) sur {len(X)} tuiles.")
        return self

    def predict(self, X):
        """Renvoie les masques de classes (N,H,W)."""
        self._ensure_model()
        if self._backend == "tensorflow":
            return self.model.predict(X, verbose=0).argmax(-1)
        # repli centroïdes
        N, H, W, B = X.shape
        flat = X.reshape(-1, B)
        d = np.linalg.norm(flat[:, None, :] - self._centroids[None, :, :], axis=-1)
        return d.argmin(-1).reshape(N, H, W)

    def save(self, path: Path | None = None):
        self._ensure_model()
        if self._backend == "tensorflow":
            path = Path(path or MODELS_DIR / "unet.keras")
            ensure_dir(path.parent)
            self.model.save(path)
        else:
            import joblib

            path = Path(path or MODELS_DIR / "unet_fallback.joblib")
            ensure_dir(path.parent)
            joblib.dump(self._centroids, path)
        log.info(f"Modèle sauvegardé : {path}")
        return path


def main() -> None:
    from src.utils import synthetic

    ds = synthetic.build_tile_dataset(n_tiles=16)
    UNetModel().fit(ds["X"], ds["y"], epochs=1)


if __name__ == "__main__":
    main()
