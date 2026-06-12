# ============================================================
# CardioIA - Fase 7
# Serviço de Análise de Risco Cardíaco
#
# Função principal:
# - calcular_risco_cardiaco()
#
# Este serviço recebe sinais vitais normalizados e retorna:
# - score de risco
# - nível de risco
# - status geral
# - motivos
# - análise individual de cada sinal vital
# ============================================================

from typing import Any


# ============================================================
# CLASSIFICAÇÃO DOS BATIMENTOS CARDÍACOS
# ============================================================

def classificar_bpm(heart_rate: int) -> dict[str, Any]:
    """
    Classifica a frequência cardíaca do paciente.
    """

    if heart_rate <= 0:
        return {
            "status": "desconhecido",
            "score": 0,
            "reason": "Frequência cardíaca não informada.",
        }

    if heart_rate < 50:
        return {
            "status": "baixo",
            "score": 35,
            "reason": "Frequência cardíaca abaixo do limite esperado.",
        }

    if heart_rate > 140:
        return {
            "status": "critico",
            "score": 45,
            "reason": "Frequência cardíaca extremamente elevada.",
        }

    if heart_rate > 120:
        return {
            "status": "critico",
            "score": 40,
            "reason": "Frequência cardíaca acima do limite esperado.",
        }

    if heart_rate > 100:
        return {
            "status": "elevado",
            "score": 20,
            "reason": "Frequência cardíaca levemente elevada.",
        }

    return {
        "status": "normal",
        "score": 0,
        "reason": "Frequência cardíaca dentro da faixa esperada.",
    }


# ============================================================
# CLASSIFICAÇÃO DA TEMPERATURA
# ============================================================

def classificar_temperatura(temperature: float) -> dict[str, Any]:
    """
    Classifica a temperatura corporal do paciente.
    """

    if temperature <= 0:
        return {
            "status": "desconhecido",
            "score": 0,
            "reason": "Temperatura não informada.",
        }

    if temperature >= 39.0:
        return {
            "status": "febre_alta",
            "score": 35,
            "reason": "Temperatura corporal muito elevada.",
        }

    if temperature >= 38.0:
        return {
            "status": "febre",
            "score": 20,
            "reason": "Temperatura corporal elevada.",
        }

    if temperature < 35.5:
        return {
            "status": "baixa",
            "score": 25,
            "reason": "Temperatura corporal abaixo do esperado.",
        }

    return {
        "status": "normal",
        "score": 0,
        "reason": "Temperatura dentro da faixa esperada.",
    }


# ============================================================
# CLASSIFICAÇÃO DA OXIGENAÇÃO
# ============================================================

def classificar_oxigenacao(oxygen_level: float) -> dict[str, Any]:
    """
    Classifica a saturação/oxigenação simulada do paciente.
    """

    if oxygen_level <= 0:
        return {
            "status": "desconhecido",
            "score": 0,
            "reason": "Saturação de oxigênio não informada.",
        }

    if oxygen_level < 90:
        return {
            "status": "grave",
            "score": 45,
            "reason": "Saturação de oxigênio em nível crítico.",
        }

    if oxygen_level < 93:
        return {
            "status": "moderada",
            "score": 35,
            "reason": "Saturação de oxigênio moderadamente reduzida.",
        }

    if oxygen_level < 95:
        return {
            "status": "leve",
            "score": 20,
            "reason": "Saturação de oxigênio abaixo do recomendado.",
        }

    return {
        "status": "normal",
        "score": 0,
        "reason": "Saturação de oxigênio dentro da faixa esperada.",
    }


# ============================================================
# STATUS GERAL COMPATÍVEL COM A LÓGICA DO ESP32
# ============================================================

def classificar_status_geral(
    temp_status: str,
    oxi_status: str,
    bpm_status: str,
) -> str:
    """
    Gera o status geral do paciente.

    Compatível com a lógica usada no ESP32:
    - RISCO_ALTO
    - ATENCAO
    - NORMAL
    """

    if (
        temp_status == "febre_alta"
        or oxi_status == "grave"
        or bpm_status == "critico"
    ):
        return "RISCO_ALTO"

    if (
        temp_status == "febre"
        or oxi_status in ["leve", "moderada"]
        or bpm_status in ["baixo", "elevado"]
    ):
        return "ATENCAO"

    return "NORMAL"


# ============================================================
# CLASSIFICAÇÃO DO NÍVEL DE RISCO
# ============================================================

def classificar_nivel_risco(score: int, status_geral: str) -> str:
    """
    Converte score numérico e status geral em nível de risco.
    """

    if status_geral == "RISCO_ALTO" or score >= 75:
        return "alto"

    if status_geral == "ATENCAO" or score >= 40:
        return "moderado"

    if score >= 15:
        return "baixo_monitorado"

    return "baixo"


# ============================================================
# INTERPRETAÇÃO TEXTUAL
# ============================================================

def interpretar_resultado(
    score: int,
    risk_level: str,
    status_geral: str,
) -> str:
    """
    Gera uma interpretação textual simples para o resultado.
    """

    if risk_level == "alto":
        return (
            "O paciente apresenta sinais compatíveis com risco elevado. "
            "É recomendada avaliação imediata e monitoramento contínuo."
        )

    if risk_level == "moderado":
        return (
            "O paciente apresenta alterações relevantes. "
            "Recomenda-se nova medição e acompanhamento preventivo."
        )

    if risk_level == "baixo_monitorado":
        return (
            "O paciente apresenta pequena alteração isolada. "
            "Não há indicação crítica, mas o acompanhamento é recomendado."
        )

    return (
        "Os sinais vitais analisados estão dentro de uma faixa aceitável "
        "para o cenário simulado."
    )


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def calcular_risco_cardiaco(dados: dict[str, Any]) -> dict[str, Any]:
    """
    Calcula o risco cardíaco a partir de sinais vitais normalizados.

    Entradas esperadas:
    - heart_rate
    - temperature
    - oxygen_level
    """

    heart_rate = int(dados.get("heart_rate", 0))
    temperature = float(dados.get("temperature", 0))
    oxygen_level = float(dados.get("oxygen_level", 98))

    bpm_result = classificar_bpm(heart_rate)
    temp_result = classificar_temperatura(temperature)
    oxi_result = classificar_oxigenacao(oxygen_level)

    score = (
        int(bpm_result["score"])
        + int(temp_result["score"])
        + int(oxi_result["score"])
    )

    score = min(score, 100)

    status_geral = classificar_status_geral(
        temp_status=temp_result["status"],
        oxi_status=oxi_result["status"],
        bpm_status=bpm_result["status"],
    )

    risk_level = classificar_nivel_risco(
        score=score,
        status_geral=status_geral,
    )

    motivos = []

    for item in [bpm_result, temp_result, oxi_result]:
        if item["status"] not in ["normal", "desconhecido"]:
            motivos.append(item["reason"])

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "alert": risk_level == "alto",
        "general_status": status_geral,
        "reasons": motivos,
        "signals": {
            "heart_rate": {
                "value": heart_rate,
                "status": bpm_result["status"],
                "score": bpm_result["score"],
                "reason": bpm_result["reason"],
            },
            "temperature": {
                "value": temperature,
                "status": temp_result["status"],
                "score": temp_result["score"],
                "reason": temp_result["reason"],
            },
            "oxygen_level": {
                "value": oxygen_level,
                "status": oxi_result["status"],
                "score": oxi_result["score"],
                "reason": oxi_result["reason"],
            },
        },
        "interpretation": interpretar_resultado(
            score=score,
            risk_level=risk_level,
            status_geral=status_geral,
        ),
    }