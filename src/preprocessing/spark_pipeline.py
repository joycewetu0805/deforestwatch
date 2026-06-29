"""
Pipeline PySpark de nettoyage et de mise à l'échelle des features pixel-based.

Justifie l'usage du Big Data : chargement distribué, nettoyage, statistiques
par classe, StandardScaler PySpark, export Parquet partitionné par année.
Si PySpark n'est pas installé, un repli pandas/numpy équivalent est utilisé.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config.settings import FEATURE_NAMES, PROCESSED_DIR
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("spark_pipeline")


def _build_dataframe() -> pd.DataFrame:
    ds = synthetic.build_pixel_dataset()
    df = pd.DataFrame(ds["X"], columns=ds["feature_names"])
    df["label"] = ds["y"]
    from config.settings import ANALYSIS_YEARS

    df["year"] = ANALYSIS_YEARS[-1]
    return df


def run(out_dir: Path = PROCESSED_DIR) -> dict:
    ensure_dir(out_dir)
    try:
        return _run_spark(out_dir)
    except Exception as exc:  # pragma: no cover - dépend de l'install Spark
        log.warning(f"PySpark indisponible ({exc}). Repli pandas.")
        return _run_pandas(out_dir)


def _run_spark(out_dir: Path) -> dict:
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import VectorAssembler, StandardScaler

    spark = (
        SparkSession.builder.appName("DeforestWatch-Preprocessing")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    pdf = _build_dataframe()
    sdf = spark.createDataFrame(pdf)

    # Nettoyage : suppression des lignes avec valeurs nulles/aberrantes
    sdf = sdf.na.drop()
    for col in FEATURE_NAMES:
        sdf = sdf.filter((sdf[col] > -1e6) & (sdf[col] < 1e6))

    # Statistiques descriptives par classe
    stats = sdf.groupBy("label").count().toPandas()
    log.info(f"Effectifs par classe :\n{stats.to_string(index=False)}")

    # Feature scaling
    assembler = VectorAssembler(inputCols=FEATURE_NAMES, outputCol="features_raw")
    sdf = assembler.transform(sdf)
    scaler = StandardScaler(inputCol="features_raw", outputCol="features", withMean=True, withStd=True)
    sdf = scaler.fit(sdf).transform(sdf)

    parquet_path = str(out_dir / "features_clean.parquet")
    sdf.select("year", "label", "features").write.mode("overwrite").partitionBy("year").parquet(parquet_path)
    n = sdf.count()
    spark.stop()
    log.info(f"Spark : {n} pixels nettoyés et exportés en Parquet → {parquet_path}")
    return {"engine": "pyspark", "n_rows": int(n), "path": parquet_path}


def _run_pandas(out_dir: Path) -> dict:
    df = _build_dataframe().dropna()
    df = df[(df[FEATURE_NAMES] > -1e6).all(axis=1) & (df[FEATURE_NAMES] < 1e6).all(axis=1)]
    # StandardScaler manuel
    df[FEATURE_NAMES] = (df[FEATURE_NAMES] - df[FEATURE_NAMES].mean()) / (df[FEATURE_NAMES].std() + 1e-9)
    path = out_dir / "features_clean.parquet"
    try:
        df.to_parquet(path, partition_cols=["year"])
    except Exception:
        path = out_dir / "features_clean.csv"
        df.to_csv(path, index=False)
    log.info(f"Pandas : {len(df)} pixels nettoyés → {path}")
    return {"engine": "pandas", "n_rows": int(len(df)), "path": str(path)}


def main() -> None:
    run()


if __name__ == "__main__":
    main()
