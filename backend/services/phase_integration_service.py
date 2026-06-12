# ============================================================
# CardioIA - Fase 7
# Serviço de Integração das Fases
#
# Função principal:
# - obter_status_integracao()
#
# Este serviço consolida o status dos módulos integrados:
# - dados
# - IoT
# - análise de risco
# - recomendações
# - chatbot
# - visão computacional
# - frontend/mobile/backend
# ============================================================

from typing import Any

from services.data_service import resumo_dados_integrados
from services.chatbot_service import status_chatbot
from services.vision_service import status_vision


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def obter_status_integracao() -> dict[str, Any]:
    """
    Retorna o status consolidado da integração da CardioIA - Fase 7.
    """

    dados = resumo_dados_integrados()
    chatbot = status_chatbot()
    vision = status_vision()

    return {
        "platform": "CardioIA",
        "phase": "Fase 7",
        "status": "integrado",
        "description": (
            "Backend integrador da CardioIA conectando módulos de dados, IoT, "
            "análise de risco, recomendações preventivas, chatbot, visão computacional "
            "e interfaces Web/Mobile."
        ),
        "technical_strategy": {
            "iot": (
                "O módulo IoT foi desenvolvido com ESP32 em MicroPython no Wokwi. "
                "O dispositivo coleta temperatura simulada pelo DHT22, oxigenação simulada "
                "pela umidade do DHT22 e batimentos cardíacos simulados por potenciômetro. "
                "Como o Wokwi não consegue enviar dados diretamente ao backend local no VSCode, "
                "o backend possui endpoints de simulação compatíveis com o mesmo payload JSON."
            ),
            "risk": (
                "A análise de risco cardíaco utiliza uma lógica heurística explicável para o MVP, "
                "com classificação individual de batimentos, temperatura e oxigenação. "
                "A estrutura está preparada para futura substituição por modelo preditivo treinado."
            ),
            "vision": (
                "O módulo de visão computacional está estruturado para receber imagens de raio X "
                "de tórax pela interface Web, pré-processar a imagem e realizar classificação "
                "com modelo TensorFlow/Keras treinado a partir dos dados em backend/data/vision."
            ),
            "chatbot": (
                "O chatbot utiliza IBM Watson Assistant quando as credenciais estão configuradas "
                "no arquivo .env. Caso contrário, o backend mantém fallback local para não interromper "
                "a operação do MVP."
            ),
            "knowledge": (
                "O serviço de conhecimento realiza consulta simples em bases das fases anteriores, "
                "incluindo textos clínicos, mapa de conhecimento e intents do chatbot."
            ),
        },
        "runtime_status": {
            "data": {
                "available": dados.get("data_dir_exists", False),
                "details": dados,
            },
            "chatbot": {
                "configured": chatbot.get("configured", False),
                "provider": chatbot.get("provider"),
                "env_file_found": chatbot.get("env_file_found"),
            },
            "vision": {
                "mode": vision.get("mode"),
                "tensorflow_required": vision.get("tensorflow_required"),
                "model_found": vision.get("model_found"),
                "class_indices_found": vision.get("class_indices_found"),
                "model_expected_path": vision.get("model_expected_path"),
            },
        },
        "integrated_modules": [
            {
                "phase": "Fase 1",
                "module": "Base clínica e pacientes simulados",
                "status": "integrado",
                "description": (
                    "Base inicial utilizada para estruturar o domínio clínico da CardioIA, "
                    "incluindo dados e textos de apoio sobre doenças cardiovasculares."
                ),
                "details": dados.get("fase1", {}),
            },
            {
                "phase": "Fase 2",
                "module": "Classificador, frases e mapa de conhecimento",
                "status": "integrado",
                "description": (
                    "Base auxiliar para consulta de conhecimento, frases de pacientes "
                    "e estruturas de classificação textual."
                ),
                "details": dados.get("fase2", {}),
            },
            {
                "phase": "Fase 3",
                "module": "IoT com ESP32, MicroPython, DHT22, potenciômetro, chave e OLED",
                "status": "integrado_por_simulacao",
                "description": (
                    "Módulo físico/simulado responsável pela coleta dos sinais vitais. "
                    "A integração HTTP está preparada no código embarcado, enquanto o backend "
                    "simula o mesmo payload para viabilizar testes locais."
                ),
                "details": {
                    "folder": "iot/",
                    "expected_files": [
                        "main.py",
                        "ssd1306.py",
                        "diagram.json",
                        "wokwi-project.txt",
                    ],
                    "sensor_payload": {
                        "patient_id": "PACIENTE_IOT_001",
                        "heart_rate": "batimentos simulados pelo potenciômetro",
                        "temperature": "temperatura simulada pelo DHT22",
                        "oxygen_level": "oxigenação simulada pela umidade do DHT22",
                        "source": "iot_micropython_oled",
                    },
                    "backend_endpoints": [
                        "POST /api/analyze",
                        "GET /api/iot/simulate",
                        "GET /api/iot/simulate/batch",
                    ],
                },
            },
            {
                "phase": "Fase 4",
                "module": "Visão computacional para raio X de tórax",
                "status": (
                    "modelo_encontrado"
                    if vision.get("model_found") and vision.get("class_indices_found")
                    else "aguardando_treinamento"
                ),
                "description": (
                    "Módulo preparado para classificar imagens de raio X de tórax enviadas "
                    "pela interface Web. O treinamento utiliza imagens e CSV localizados "
                    "em backend/data/vision."
                ),
                "details": {
                    "service": "vision_service.py",
                    "training_script": "vision/train_xray_model.py",
                    "endpoint": "POST /api/vision/xray",
                    "status": vision,
                },
            },
            {
                "phase": "Fase 5",
                "module": "Assistente conversacional",
                "status": (
                    "configurado"
                    if chatbot.get("configured")
                    else "fallback_local"
                ),
                "description": (
                    "Assistente conversacional integrado ao IBM Watson Assistant, "
                    "com fallback local para garantir funcionamento do backend em ambiente de teste."
                ),
                "details": {
                    "data": dados.get("fase5", {}),
                    "chatbot_status": chatbot,
                    "endpoints": [
                        "GET /api/chatbot/status",
                        "GET /api/chatbot/welcome",
                        "POST /api/chatbot/message",
                        "POST /api/chatbot/restart",
                    ],
                },
            },
            {
                "phase": "Fase 6",
                "module": "Análise preditiva de risco cardíaco",
                "status": "integrado_em_mvp",
                "description": (
                    "Módulo de análise de risco com regras explicáveis para classificar "
                    "os sinais vitais em baixo, baixo monitorado, moderado ou alto risco."
                ),
                "details": {
                    "service": "risk_service.py",
                    "recommendation_service": "recommendation_service.py",
                    "main_endpoint": "POST /api/analyze",
                    "auxiliary_endpoints": [
                        "POST /api/risk",
                        "POST /api/recommendation",
                    ],
                    "observation": (
                        "A lógica atual utiliza regras clínicas simplificadas e pode ser "
                        "substituída futuramente por modelo .pkl, .joblib, .keras ou API preditiva."
                    ),
                },
            },
            {
                "phase": "Fase 7",
                "module": "Solução integrada Web/Mobile/Backend",
                "status": "operacional",
                "description": (
                    "Camada final de integração do MVP, conectando backend FastAPI, "
                    "frontend Web, aplicativo Mobile, chatbot, IoT, visão computacional "
                    "e análise de risco."
                ),
                "details": {
                    "backend": "FastAPI",
                    "frontend_ready": True,
                    "mobile_ready": True,
                    "docs": "/docs",
                    "health": "/api/health",
                    "modules_endpoint": "/api/modules",
                },
            },
        ],
    }