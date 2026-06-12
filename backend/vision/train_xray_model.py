# ============================================================
# CardioIA - Fase 7
# Treinamento de Modelo de Visão Computacional
# Classificação Multi-Label de Raio X de Tórax
#
# Entrada esperada:
# - backend/data/vision/metadata.csv
# - backend/data/vision/images/
#
# CSV esperado:
# filename,width,height,class,xmin,ymin,xmax,ymax
#
# Saída gerada:
# - backend/models/xray_chest_model.keras
# - backend/models/xray_class_indices.json
# - backend/models/xray_training_history.json
# ============================================================

from pathlib import Path
import json

import pandas as pd
import tensorflow as tf
from keras import layers, models
from keras.src.legacy.preprocessing.image import ImageDataGenerator
from keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
)


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "vision"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "metadata.csv"

MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "xray_chest_model.keras"
CLASS_INDICES_PATH = MODELS_DIR / "xray_class_indices.json"
TRAINING_HISTORY_PATH = MODELS_DIR / "xray_training_history.json"


# ============================================================
# PARÂMETROS DO TREINAMENTO
# ============================================================

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 30
VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42


# ============================================================
# VALIDAÇÃO DE ESTRUTURA
# ============================================================

def validar_estrutura() -> None:
    """
    Valida se a estrutura necessária para treinamento existe.
    """

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Pasta de dados de visão não encontrada: {DATA_DIR}"
        )

    if not IMAGES_DIR.exists():
        raise FileNotFoundError(
            f"Pasta de imagens não encontrada: {IMAGES_DIR}"
        )

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo CSV de metadados não encontrado: {CSV_PATH}"
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CARREGAMENTO E TRATAMENTO DO DATASET
# ============================================================

def carregar_dataframe() -> tuple[pd.DataFrame, list[str]]:
    """
    Carrega o metadata.csv e transforma o dataset para classificação multi-label.

    O arquivo original possui estrutura de detecção/localização:

    filename,width,height,class,xmin,ymin,xmax,ymax

    Como o modelo atual é de classificação, as coordenadas xmin, ymin, xmax e ymax
    são ignoradas neste treinamento.

    Para imagens com múltiplas classes, o dataframe final usa codificação multi-hot:

    filename,Atelectasis,Cardiomegaly,Effusion,...
    img001.png,1,0,1,...
    """

    df = pd.read_csv(CSV_PATH)

    colunas_obrigatorias = {"filename", "class"}

    if not colunas_obrigatorias.issubset(df.columns):
        raise ValueError(
            "O CSV precisa conter as colunas obrigatórias: "
            "'filename' e 'class'."
        )

    df = df[["filename", "class"]].copy()

    df["filename"] = df["filename"].astype(str).str.strip()
    df["class"] = df["class"].astype(str).str.strip()

    df = df.dropna()
    df = df.drop_duplicates()

    df = df[
        (df["filename"] != "")
        & (df["class"] != "")
        & (df["filename"].str.lower() != "nan")
        & (df["class"].str.lower() != "nan")
    ]

    if df.empty:
        raise ValueError("O CSV não possui registros válidos para treinamento.")

    # Verifica se os arquivos realmente existem dentro de backend/data/vision/images
    df["image_path_exists"] = df["filename"].apply(
        lambda nome: (IMAGES_DIR / nome).exists()
    )

    imagens_faltantes = df[df["image_path_exists"] == False]

    if not imagens_faltantes.empty:
        print()
        print("ATENÇÃO: algumas imagens listadas no CSV não foram encontradas.")
        print("Essas imagens serão ignoradas no treinamento.")
        print(imagens_faltantes[["filename", "class"]].head(20))
        print()

    df = df[df["image_path_exists"] == True].drop(columns=["image_path_exists"])

    if df.empty:
        raise ValueError(
            "Nenhuma imagem válida foi encontrada com base no CSV. "
            "Verifique se os nomes em metadata.csv batem com os arquivos em "
            "backend/data/vision/images."
        )

    classes = sorted(df["class"].unique().tolist())

    if len(classes) < 2:
        raise ValueError(
            "É necessário ter pelo menos duas classes diferentes para treinamento."
        )

    # Converte linhas duplicadas por imagem em multi-label.
    # Exemplo:
    # img001.png Cardiomegaly
    # img001.png Pneumothorax
    #
    # Vira:
    # img001.png Cardiomegaly=1 Pneumothorax=1
    df_multi_label = (
        pd.crosstab(df["filename"], df["class"])
        .reindex(columns=classes, fill_value=0)
        .clip(upper=1)
        .reset_index()
    )

    for classe in classes:
        df_multi_label[classe] = df_multi_label[classe].astype("float32")

    print()
    print("Dataset carregado com sucesso.")
    print(f"Total de anotações no CSV: {len(df)}")
    print(f"Total de imagens únicas válidas: {len(df_multi_label)}")
    print(f"Total de classes: {len(classes)}")
    print()
    print("Classes detectadas:")
    for classe in classes:
        total = int(df_multi_label[classe].sum())
        print(f"- {classe}: {total} imagens")
    print()

    imagens_multiclasse = int((df_multi_label[classes].sum(axis=1) > 1).sum())

    print(f"Imagens com mais de uma classe: {imagens_multiclasse}")
    print()

    return df_multi_label, classes


# ============================================================
# GERADORES DE TREINO E VALIDAÇÃO
# ============================================================

def criar_geradores(df: pd.DataFrame, classes: list[str]):
    """
    Cria os geradores de treino e validação.

    Como o problema é multi-label, usamos:
    - y_col=classes
    - class_mode='raw'

    Assim cada imagem retorna um vetor multi-hot.
    """

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        validation_split=VALIDATION_SPLIT,
        rotation_range=10,
        width_shift_range=0.05,
        height_shift_range=0.05,
        zoom_range=0.10,
        horizontal_flip=False,
        fill_mode="nearest",
    )

    validation_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        validation_split=VALIDATION_SPLIT,
    )

    train_generator = train_datagen.flow_from_dataframe(
        dataframe=df,
        directory=str(IMAGES_DIR),
        x_col="filename",
        y_col=classes,
        target_size=IMG_SIZE,
        color_mode="rgb",
        class_mode="raw",
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=RANDOM_SEED,
        subset="training",
    )

    validation_generator = validation_datagen.flow_from_dataframe(
        dataframe=df,
        directory=str(IMAGES_DIR),
        x_col="filename",
        y_col=classes,
        target_size=IMG_SIZE,
        color_mode="rgb",
        class_mode="raw",
        batch_size=BATCH_SIZE,
        shuffle=False,
        seed=RANDOM_SEED,
        subset="validation",
    )

    return train_generator, validation_generator


# ============================================================
# CONSTRUÇÃO DO MODELO
# ============================================================

def construir_modelo(num_classes: int) -> tf.keras.Model:
    """
    Constrói uma CNN baseada em Transfer Learning com MobileNetV2.

    Como o problema é multi-label:
    - saída usa sigmoid
    - loss usa binary_crossentropy

    Isso permite que uma imagem pertença a mais de uma classe ao mesmo tempo.
    """

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
        include_top=False,
        weights="imagenet",
    )

    base_model.trainable = False

    inputs = layers.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3))

    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs * 255.0)
    x = base_model(x, training=False)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)

    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.35)(x)

    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.25)(x)

    outputs = layers.Dense(num_classes, activation="sigmoid")(x)

    model = models.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="binary_accuracy"),
            tf.keras.metrics.AUC(name="auc", multi_label=True),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )

    return model


# ============================================================
# CALLBACKS
# ============================================================

def criar_callbacks():
    """
    Cria callbacks para melhorar o treinamento.
    """

    return [
        ModelCheckpoint(
            filepath=str(MODEL_PATH),
            monitor="val_auc",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]


# ============================================================
# SALVAMENTO DE ARQUIVOS AUXILIARES
# ============================================================

def salvar_indices_classes(classes: list[str]) -> None:
    """
    Salva o mapeamento de classes.

    Exemplo:

    {
        "mode": "multi_label",
        "class_to_index": {
            "Atelectasis": 0,
            "Cardiomegaly": 1
        },
        "index_to_class": {
            "0": "Atelectasis",
            "1": "Cardiomegaly"
        }
    }
    """

    class_to_index = {
        classe: indice
        for indice, classe in enumerate(classes)
    }

    index_to_class = {
        str(indice): classe
        for classe, indice in class_to_index.items()
    }

    payload = {
        "mode": "multi_label",
        "threshold": 0.50,
        "class_to_index": class_to_index,
        "index_to_class": index_to_class,
        "classes": classes,
        "img_size": list(IMG_SIZE),
        "model_file": MODEL_PATH.name,
        "loss": "binary_crossentropy",
        "output_activation": "sigmoid",
    }

    CLASS_INDICES_PATH.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def salvar_historico(history: tf.keras.callbacks.History) -> None:
    """
    Salva o histórico do treinamento em JSON.
    """

    historico = {}

    for chave, valores in history.history.items():
        historico[chave] = [
            float(valor)
            for valor in valores
        ]

    TRAINING_HISTORY_PATH.write_text(
        json.dumps(historico, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


# ============================================================
# TREINAMENTO PRINCIPAL
# ============================================================

def treinar_modelo() -> None:
    """
    Executa o pipeline completo de treinamento.
    """

    print()
    print("==================================================")
    print("CardioIA - Treinamento Multi-Label de Raio X")
    print("==================================================")
    print()

    validar_estrutura()

    df, classes = carregar_dataframe()

    train_generator, validation_generator = criar_geradores(df, classes)

    num_classes = len(classes)

    salvar_indices_classes(classes)

    model = construir_modelo(num_classes=num_classes)

    print("Resumo do modelo:")
    model.summary()
    print()

    callbacks = criar_callbacks()

    history = model.fit(
        train_generator,
        validation_data=validation_generator,
        epochs=EPOCHS,
        callbacks=callbacks,
    )

    model.save(MODEL_PATH)

    salvar_historico(history)

    print()
    print("==================================================")
    print("Treinamento concluído com sucesso.")
    print("==================================================")
    print(f"Modelo salvo em: {MODEL_PATH}")
    print(f"Classes salvas em: {CLASS_INDICES_PATH}")
    print(f"Histórico salvo em: {TRAINING_HISTORY_PATH}")
    print()


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":
    treinar_modelo()