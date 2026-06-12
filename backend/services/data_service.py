# ============================================================
# CardioIA - Fase 7
# Serviço de Dados
#
# Funções principais:
# - ler_txt()
# - ler_csv()
# - ler_json()
# - resumo_dados_integrados()
#
# Este serviço centraliza a leitura dos arquivos da pasta:
# backend/data/
# ============================================================

from pathlib import Path
from typing import Any
import csv
import json


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# FUNÇÕES GENÉRICAS DE LEITURA
# ============================================================

def arquivo_existe(caminho: Path) -> bool:
    """
    Verifica se um caminho existe e é arquivo.
    """

    return caminho.exists() and caminho.is_file()


def ler_txt(caminho: Path) -> str:
    """
    Lê arquivo TXT com tentativa de UTF-8 e fallback para latin-1.
    """

    if not arquivo_existe(caminho):
        return ""

    try:
        return caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return caminho.read_text(encoding="latin-1")
    except Exception:
        return ""


def ler_csv(caminho: Path) -> list[dict[str, Any]]:
    """
    Lê arquivo CSV com tentativa de UTF-8 e fallback para latin-1.
    """

    if not arquivo_existe(caminho):
        return []

    try:
        with caminho.open("r", encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))
    except UnicodeDecodeError:
        try:
            with caminho.open("r", encoding="latin-1", newline="") as arquivo:
                return list(csv.DictReader(arquivo))
        except Exception:
            return []
    except Exception:
        return []


def ler_json(caminho: Path) -> Any:
    """
    Lê arquivo JSON com tentativa de UTF-8 e fallback para latin-1.
    """

    if not arquivo_existe(caminho):
        return None

    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        try:
            return json.loads(caminho.read_text(encoding="latin-1"))
        except Exception:
            return None
    except Exception:
        return None


def listar_arquivos_fase(nome_fase: str) -> list[str]:
    """
    Lista os arquivos existentes dentro de uma pasta de fase.

    Exemplo:
    backend/data/fase1
    backend/data/fase2
    backend/data/fase5
    """

    pasta = DATA_DIR / nome_fase

    if not pasta.exists():
        return []

    return [
        arquivo.name
        for arquivo in pasta.iterdir()
        if arquivo.is_file()
    ]


# ============================================================
# FASE 1
# ============================================================

def carregar_pacientes_fase1() -> list[dict[str, Any]]:
    """
    Carrega a base de pacientes cardíacos simulados da Fase 1.
    """

    caminho = DATA_DIR / "fase1" / "pacientes_cardiacos_simulados.csv"
    return ler_csv(caminho)


def carregar_textos_clinicos_fase1() -> dict[str, str]:
    """
    Carrega os textos clínicos usados como base de conhecimento.
    """

    pasta = DATA_DIR / "fase1"

    arquivos_txt = [
        "CONHECIMENTO_INFARTO_AGUDO.txt",
        "INFARTO_DIAGNOSTICO_INTERVENCOES.txt",
        "PERFIL_DOENCAS_CARDIOVASCULARES.txt",
        "PREVALENCIA_DOENCAS_CARDIACAS.txt",
    ]

    textos = {}

    for nome_arquivo in arquivos_txt:
        caminho = pasta / nome_arquivo
        textos[nome_arquivo] = ler_txt(caminho)

    return textos


# ============================================================
# FASE 2
# ============================================================

def carregar_base_classificador_fase2() -> list[dict[str, Any]]:
    """
    Carrega base do classificador da Fase 2.
    """

    caminho = DATA_DIR / "fase2" / "base_classificador.csv"
    return ler_csv(caminho)


def carregar_frases_pacientes_fase2() -> str:
    """
    Carrega frases simuladas de pacientes da Fase 2.
    """

    caminho = DATA_DIR / "fase2" / "frases_pacientes.txt"
    return ler_txt(caminho)


def carregar_mapa_conhecimento_fase2() -> list[dict[str, Any]]:
    """
    Carrega mapa de conhecimento CardioIA da Fase 2.
    """

    caminho = DATA_DIR / "fase2" / "mapa_conhecimento_cardio.csv"
    return ler_csv(caminho)


# ============================================================
# FASE 5
# ============================================================

def carregar_intents_fase5() -> list[dict[str, Any]]:
    """
    Carrega intents do chatbot da Fase 5.
    """

    caminho = DATA_DIR / "fase5" / "Intents.csv"
    return ler_csv(caminho)


def carregar_entities_fase5() -> list[dict[str, Any]]:
    """
    Carrega entities do chatbot da Fase 5.
    """

    caminho = DATA_DIR / "fase5" / "Entities.csv"
    return ler_csv(caminho)


def carregar_dialogo_fase5() -> Any:
    """
    Carrega JSON de diálogo do Watson/assistente da Fase 5.
    """

    caminho = DATA_DIR / "fase5" / "Assistente-Cardio-dialog.json"
    return ler_json(caminho)


# ============================================================
# VISÃO COMPUTACIONAL
# ============================================================

def resumo_dados_vision() -> dict[str, Any]:
    """
    Retorna um resumo da estrutura de dados de visão computacional.
    """

    vision_dir = DATA_DIR / "vision"
    images_dir = vision_dir / "images"
    uploads_dir = vision_dir / "uploads"
    metadata_path = vision_dir / "metadata.csv"

    total_imagens = 0

    if images_dir.exists():
        total_imagens = len([
            arquivo
            for arquivo in images_dir.iterdir()
            if arquivo.is_file()
            and arquivo.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
        ])

    metadata = ler_csv(metadata_path)

    return {
        "vision_dir": str(vision_dir),
        "vision_dir_exists": vision_dir.exists(),
        "images_dir": str(images_dir),
        "images_dir_exists": images_dir.exists(),
        "uploads_dir": str(uploads_dir),
        "uploads_dir_exists": uploads_dir.exists(),
        "metadata_path": str(metadata_path),
        "metadata_found": metadata_path.exists(),
        "total_images": total_imagens,
        "total_metadata_records": len(metadata),
    }


# ============================================================
# RESUMO INTEGRADO
# ============================================================

def resumo_dados_integrados() -> dict[str, Any]:
    """
    Retorna um resumo dos dados disponíveis nas fases integradas.
    """

    pacientes = carregar_pacientes_fase1()
    textos_clinicos = carregar_textos_clinicos_fase1()

    base_classificador = carregar_base_classificador_fase2()
    frases_pacientes = carregar_frases_pacientes_fase2()
    mapa_conhecimento = carregar_mapa_conhecimento_fase2()

    intents = carregar_intents_fase5()
    entities = carregar_entities_fase5()
    dialogo = carregar_dialogo_fase5()

    vision = resumo_dados_vision()

    return {
        "data_dir": str(DATA_DIR),
        "data_dir_exists": DATA_DIR.exists(),
        "fase1": {
            "folder": "data/fase1",
            "arquivos": listar_arquivos_fase("fase1"),
            "total_pacientes": len(pacientes),
            "textos_clinicos": list(textos_clinicos.keys()),
            "textos_clinicos_carregados": sum(
                1 for texto in textos_clinicos.values() if bool(texto)
            ),
        },
        "fase2": {
            "folder": "data/fase2",
            "arquivos": listar_arquivos_fase("fase2"),
            "total_registros_classificador": len(base_classificador),
            "frases_pacientes_carregadas": bool(frases_pacientes),
            "total_itens_mapa_conhecimento": len(mapa_conhecimento),
        },
        "fase5": {
            "folder": "data/fase5",
            "arquivos": listar_arquivos_fase("fase5"),
            "total_intents": len(intents),
            "total_entities": len(entities),
            "dialogo_carregado": dialogo is not None,
        },
        "vision": vision,
    }