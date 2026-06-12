# ============================================================
# CardioIA - Fase 7
# Serviço de Visão Computacional
#
# Funções principais:
# - status_vision()
# - analisar_upload_raio_x()
# - analisar_raio_x_torax()
#
# Este serviço recebe uma imagem de raio X de tórax enviada
# pela interface Web e retorna a classificação prevista pelo
# modelo treinado em TensorFlow/Keras.
# ============================================================

from pathlib import Path
from typing import Any
import json
import uuid
import shutil
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"
DATA_VISION_DIR = BASE_DIR / "data" / "vision"
UPLOAD_DIR = DATA_VISION_DIR / "uploads"

MODEL_PATH = MODELS_DIR / "xray_chest_model.keras"
CLASS_INDICES_PATH = MODELS_DIR / "xray_class_indices.json"

IMG_SIZE = (224, 224)


# ============================================================
# CACHE DO MODELO
# ============================================================

_model_cache = None
_class_mapping_cache = None


# ============================================================
# STATUS DO MÓDULO
# ============================================================

def status_vision() -> dict[str, Any]:
    """
    Retorna o status técnico do módulo de visão computacional.
    """

    return {
        "module": "vision",
        "status": "available",
        "tensorflow_required": True,
        "mode": "xray_chest_classification",
        "model_expected_path": str(MODEL_PATH),
        "class_indices_expected_path": str(CLASS_INDICES_PATH),
        "model_found": MODEL_PATH.exists(),
        "class_indices_found": CLASS_INDICES_PATH.exists(),
        "data_vision_dir": str(DATA_VISION_DIR),
        "upload_dir": str(UPLOAD_DIR),
        "input_size": list(IMG_SIZE),
        "description": (
            "Módulo de visão computacional para classificação de imagem de raio X "
            "de tórax enviada pela interface Web."
        ),
    }


# ============================================================
# CARREGAMENTO DO MODELO E DAS CLASSES
# ============================================================

def carregar_modelo():
    """
    Carrega o modelo treinado em cache.

    Arquivo esperado:
    backend/models/xray_chest_model.keras
    """

    global _model_cache

    if _model_cache is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo de visão não encontrado em: {MODEL_PATH}. "
                "Execute primeiro o treinamento em backend/vision/train_xray_model.py."
            )

        _model_cache = tf.keras.models.load_model(MODEL_PATH)

    return _model_cache


def carregar_mapeamento_classes() -> dict[str, Any]:
    """
    Carrega o arquivo de classes gerado no treinamento.

    Arquivo esperado:
    backend/models/xray_class_indices.json
    """

    global _class_mapping_cache

    if _class_mapping_cache is None:
        if not CLASS_INDICES_PATH.exists():
            raise FileNotFoundError(
                f"Arquivo de classes não encontrado em: {CLASS_INDICES_PATH}. "
                "Execute primeiro o treinamento em backend/vision/train_xray_model.py."
            )

        with CLASS_INDICES_PATH.open("r", encoding="utf-8") as arquivo:
            _class_mapping_cache = json.load(arquivo)

    return _class_mapping_cache


# ============================================================
# VALIDAÇÃO E SALVAMENTO DO UPLOAD
# ============================================================

def validar_extensao_imagem(filename: str) -> None:
    """
    Valida se a imagem enviada possui extensão permitida.
    """

    extensoes_validas = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    extensao = Path(filename).suffix.lower()

    if extensao not in extensoes_validas:
        raise ValueError(
            f"Formato de imagem inválido: {extensao}. "
            f"Formatos aceitos: {', '.join(sorted(extensoes_validas))}."
        )


def salvar_upload_imagem(file_object, filename: str) -> Path:
    """
    Salva a imagem enviada pela Web em:

    backend/data/vision/uploads
    """

    if not filename or not str(filename).strip():
        raise ValueError("Nome do arquivo não informado.")

    validar_extensao_imagem(filename)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    extensao = Path(filename).suffix.lower()
    nome_seguro = f"{uuid.uuid4().hex}{extensao}"

    destino = UPLOAD_DIR / nome_seguro

    with destino.open("wb") as buffer:
        shutil.copyfileobj(file_object, buffer)

    return destino


# ============================================================
# PRÉ-PROCESSAMENTO
# ============================================================

def preprocessar_imagem(image_path: Path) -> np.ndarray:
    """
    Carrega e prepara a imagem para o modelo.

    Entrada:
    - Caminho da imagem salva

    Saída:
    - Array no formato (1, 224, 224, 3)
    - Valores normalizados entre 0 e 1
    """

    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    imagem = Image.open(image_path).convert("RGB")
    imagem = imagem.resize(IMG_SIZE)

    array = np.array(imagem).astype("float32") / 255.0
    array = np.expand_dims(array, axis=0)

    return array


# ============================================================
# INTERPRETAÇÃO DO RESULTADO
# ============================================================

def interpretar_classe(classe: str, confianca: float) -> dict[str, Any]:
    """
    Gera interpretação textual para a classe prevista.

    As classes reais dependem do CSV usado no treinamento.
    Esta função cobre nomes comuns e mantém fallback genérico.
    """

    classe_normalizada = str(classe or "").lower().strip()

    if classe_normalizada in [
        "normal",
        "no_finding",
        "no finding",
        "sem_alteracao",
        "sem_alteração",
        "sem alteracao",
        "sem alteração",
    ]:
        severity = "normal"
        message = (
            "A imagem foi classificada como sem alteração crítica aparente "
            "dentro das classes disponíveis no modelo."
        )
        recommendation = (
            "Manter acompanhamento clínico conforme necessidade, histórico do paciente "
            "e orientação profissional."
        )

    elif classe_normalizada in [
        "pneumonia",
        "pneumonia_bacteriana",
        "pneumonia bacteriana",
        "pneumonia_viral",
        "pneumonia viral",
    ]:
        severity = "atenção"
        message = (
            "O modelo identificou padrão compatível com pneumonia ou alteração pulmonar "
            "relacionada, conforme as classes utilizadas no treinamento."
        )
        recommendation = (
            "Recomenda-se avaliação médica e correlação com sintomas, exame físico "
            "e laudo radiológico."
        )

    elif classe_normalizada in [
        "cardiomegalia",
        "cardiomegaly",
    ]:
        severity = "atenção"
        message = (
            "O modelo identificou padrão compatível com aumento da área cardíaca "
            "ou cardiomegalia, conforme as classes utilizadas no treinamento."
        )
        recommendation = (
            "Recomenda-se avaliação médica, correlação com histórico cardiovascular "
            "e exames complementares."
        )

    elif classe_normalizada in [
        "covid",
        "covid19",
        "covid-19",
    ]:
        severity = "atenção"
        message = (
            "O modelo identificou padrão compatível com alteração associada à COVID-19 "
            "ou condição respiratória semelhante, conforme as classes utilizadas no treinamento."
        )
        recommendation = (
            "Recomenda-se avaliação médica e correlação com sintomas respiratórios "
            "e exames laboratoriais."
        )

    elif classe_normalizada in [
        "tuberculose",
        "tuberculosis",
    ]:
        severity = "atenção"
        message = (
            "O modelo identificou padrão compatível com tuberculose ou alteração pulmonar "
            "relacionada, conforme as classes utilizadas no treinamento."
        )
        recommendation = (
            "Recomenda-se avaliação médica especializada e correlação com exames clínicos "
            "e laboratoriais."
        )

    else:
        severity = "indefinida"
        message = (
            f"A imagem foi classificada como '{classe}'. "
            "A interpretação clínica depende das classes utilizadas no treinamento."
        )
        recommendation = (
            "Recomenda-se validar o resultado com profissional de saúde e laudo especializado."
        )

    if confianca < 0.60:
        confidence_level = "baixa"
    elif confianca < 0.80:
        confidence_level = "moderada"
    else:
        confidence_level = "alta"

    return {
        "severity": severity,
        "message": message,
        "recommendation": recommendation,
        "confidence_level": confidence_level,
        "disclaimer": (
            "Resultado gerado por modelo computacional de apoio. "
            "Não substitui avaliação médica, laudo radiológico ou diagnóstico profissional."
        ),
    }


def montar_probabilidades(
    predictions: np.ndarray,
    index_to_class: dict[str, str],
) -> list[dict[str, Any]]:
    """
    Monta ranking de probabilidades por classe.
    """

    probabilidades = predictions[0]
    ranking = []

    for indice, probabilidade in enumerate(probabilidades):
        classe = index_to_class.get(str(indice), f"classe_{indice}")

        ranking.append({
            "class": classe,
            "probability": round(float(probabilidade), 6),
            "percentage": round(float(probabilidade) * 100, 2),
        })

    ranking.sort(
        key=lambda item: item["probability"],
        reverse=True,
    )

    return ranking


# ============================================================
# INFERÊNCIA PRINCIPAL
# ============================================================

def analisar_raio_x_torax(image_path: Path) -> dict[str, Any]:
    """
    Executa a inferência em uma imagem de raio X de tórax.
    """

    modelo = carregar_modelo()
    mapping = carregar_mapeamento_classes()

    index_to_class = mapping.get("index_to_class", {})

    if not index_to_class:
        raise ValueError(
            "Mapeamento de classes inválido. Verifique o arquivo xray_class_indices.json."
        )

    imagem_processada = preprocessar_imagem(image_path)

    predictions = modelo.predict(imagem_processada)

    ranking = montar_probabilidades(
        predictions=predictions,
        index_to_class=index_to_class,
    )

    melhor_resultado = ranking[0]

    classe_prevista = melhor_resultado["class"]
    confianca = melhor_resultado["probability"]

    interpretacao = interpretar_classe(
        classe=classe_prevista,
        confianca=confianca,
    )

    return {
        "status": "analisado",
        "mode": "xray_chest_classification",
        "image": image_path.name,
        "predicted_class": classe_prevista,
        "confidence": round(float(confianca), 6),
        "confidence_percentage": round(float(confianca) * 100, 2),
        "ranking": ranking,
        "interpretation": interpretacao,
        "model": {
            "path": str(MODEL_PATH),
            "input_size": list(IMG_SIZE),
            "classes": list(index_to_class.values()),
        },
    }


def analisar_upload_raio_x(file_object, filename: str) -> dict[str, Any]:
    """
    Salva o upload e executa a análise do raio X.
    """

    caminho_imagem = salvar_upload_imagem(
        file_object=file_object,
        filename=filename,
    )

    return analisar_raio_x_torax(caminho_imagem)


# ============================================================
# COMPATIBILIDADE COM ENDPOINT ANTIGO
# ============================================================

def analisar_imagem_ecg(image_name: str | None = None) -> dict[str, Any]:
    """
    Mantido por compatibilidade com endpoints antigos.

    A versão atual da visão computacional está configurada para raio X de tórax.
    """

    return {
        "status": "available",
        "mode": "xray_chest_classification",
        "message": (
            "O módulo de visão atual está configurado para análise de raio X de tórax. "
            "Envie uma imagem pelo endpoint /api/vision/xray."
        ),
        "image_reference": image_name,
        "endpoint": "/api/vision/xray",
    }


def analisar_upload_imagem(filename: str | None = None) -> dict[str, Any]:
    """
    Mantido por compatibilidade com versões anteriores.
    """

    return analisar_imagem_ecg(filename)