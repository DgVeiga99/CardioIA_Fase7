# ============================================================
# CardioIA - Fase 7
# Serviço de Sensores / IoT
#
# Funções principais:
# - normalizar_dados_sensor()
# - simular_payload_iot()
# - simular_lote_iot()
#
# Este serviço padroniza dados vindos de:
# - ESP32/Wokwi
# - Web
# - Mobile
# - Postman/Swagger
# - Simulador interno do backend
# ============================================================

from datetime import datetime
from random import randint, uniform, choice
from typing import Any


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _buscar_primeiro_valor(
    payload: dict[str, Any],
    chaves: list[str],
    valor_padrao: Any = None,
) -> Any:
    """
    Procura o primeiro campo existente dentro de uma lista de possíveis nomes.
    """

    for chave in chaves:
        if chave in payload and payload.get(chave) is not None:
            return payload.get(chave)

    return valor_padrao


def _converter_int(valor: Any, padrao: int = 0) -> int:
    """
    Converte um valor para inteiro com segurança.
    """

    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return padrao


def _converter_float(valor: Any, padrao: float = 0.0) -> float:
    """
    Converte um valor para float com segurança.
    """

    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def _timestamp_atual() -> str:
    """
    Retorna timestamp ISO para registro da leitura no backend.
    """

    return datetime.now().isoformat(timespec="seconds")


# ============================================================
# NORMALIZAÇÃO DOS DADOS
# ============================================================

def normalizar_dados_sensor(payload: dict[str, Any] | None) -> dict[str, Any]:
    """
    Normaliza os dados recebidos do ESP32/Wokwi, Web, Mobile ou simulador.

    Payload preferencial enviado pelo ESP32 MicroPython:

    {
        "patient_id": "PACIENTE_IOT_001",
        "heart_rate": 87,
        "temperature": 36.8,
        "oxygen_level": 97.0,
        "source": "iot_micropython_oled"
    }

    Também aceita variações:
    - heart_rate, bpm, batimentos, frequencia_cardiaca
    - temperature, temp, temperatura
    - oxygen_level, spo2, oxygen, saturacao, oxigenacao, humidity, umidade
    """

    payload = payload or {}

    patient_id = _buscar_primeiro_valor(
        payload,
        ["patient_id", "paciente_id", "id_paciente", "device_id"],
        "PACIENTE_SIMULADO_001",
    )

    heart_rate = _buscar_primeiro_valor(
        payload,
        ["heart_rate", "bpm", "batimentos", "frequencia_cardiaca"],
        0,
    )

    temperature = _buscar_primeiro_valor(
        payload,
        ["temperature", "temp", "temperatura"],
        0.0,
    )

    oxygen_level = _buscar_primeiro_valor(
        payload,
        [
            "oxygen_level",
            "spo2",
            "oxygen",
            "saturacao",
            "oxigenacao",
            "humidity",
            "umidade",
        ],
        98.0,
    )

    source = _buscar_primeiro_valor(
        payload,
        ["source", "origem"],
        "simulado",
    )

    timestamp = _buscar_primeiro_valor(
        payload,
        ["timestamp", "datetime", "data_hora"],
        _timestamp_atual(),
    )

    esp32_ticks_ms = _buscar_primeiro_valor(
        payload,
        ["ts", "ticks_ms", "esp32_ts"],
        None,
    )

    return {
        "patient_id": str(patient_id),
        "heart_rate": _converter_int(heart_rate, 0),
        "temperature": round(_converter_float(temperature, 0.0), 1),
        "oxygen_level": round(_converter_float(oxygen_level, 98.0), 1),
        "source": str(source),
        "timestamp": str(timestamp),
        "esp32_ticks_ms": esp32_ticks_ms,
    }


# ============================================================
# SIMULAÇÃO COMPATÍVEL COM ESP32/WOKWI
# ============================================================

def simular_payload_iot(cenario: str = "normal") -> dict[str, Any]:
    """
    Simula o mesmo payload que o ESP32 enviaria ao endpoint /api/analyze.

    Cenários disponíveis:
    - normal
    - atencao
    - risco_alto
    - critico
    - offline_buffer
    - aleatorio
    """

    cenario = (cenario or "normal").lower().strip()

    if cenario == "normal":
        payload = {
            "patient_id": "PACIENTE_IOT_001",
            "heart_rate": randint(60, 95),
            "temperature": round(uniform(36.1, 37.3), 1),
            "oxygen_level": round(uniform(96.0, 99.0), 1),
            "source": "iot_micropython_oled_simulado",
        }

    elif cenario == "atencao":
        payload = {
            "patient_id": "PACIENTE_IOT_001",
            "heart_rate": randint(101, 120),
            "temperature": round(uniform(37.5, 38.5), 1),
            "oxygen_level": round(uniform(93.0, 95.0), 1),
            "source": "iot_micropython_oled_simulado",
        }

    elif cenario == "risco_alto":
        payload = {
            "patient_id": "PACIENTE_IOT_001",
            "heart_rate": randint(121, 155),
            "temperature": round(uniform(38.6, 40.0), 1),
            "oxygen_level": round(uniform(86.0, 92.0), 1),
            "source": "iot_micropython_oled_simulado",
        }

    elif cenario == "critico":
        payload = {
            "patient_id": "PACIENTE_IOT_001",
            "heart_rate": choice([randint(35, 49), randint(145, 175)]),
            "temperature": round(uniform(39.0, 40.5), 1),
            "oxygen_level": round(uniform(82.0, 89.0), 1),
            "source": "iot_micropython_oled_simulado",
        }

    elif cenario == "offline_buffer":
        payload = {
            "patient_id": "PACIENTE_IOT_001",
            "heart_rate": randint(45, 160),
            "temperature": round(uniform(36.0, 39.5), 1),
            "oxygen_level": round(uniform(88.0, 98.0), 1),
            "source": "iot_buffer_offline_simulado",
        }

    else:
        payload = {
            "patient_id": "PACIENTE_IOT_001",
            "heart_rate": randint(45, 160),
            "temperature": round(uniform(35.8, 40.0), 1),
            "oxygen_level": round(uniform(86.0, 99.0), 1),
            "source": "iot_micropython_oled_simulado",
        }

    return normalizar_dados_sensor(payload)


def simular_lote_iot(
    cenario: str = "aleatorio",
    quantidade: int = 10,
) -> list[dict[str, Any]]:
    """
    Gera múltiplas leituras simuladas para gráficos, dashboards e testes.
    """

    quantidade = max(1, min(int(quantidade), 100))

    return [
        simular_payload_iot(cenario=cenario)
        for _ in range(quantidade)
    ]