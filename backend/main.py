# ============================================================
# CardioIA - Fase 7
# Backend FastAPI Integrador
#
# Módulos integrados:
# - IoT / sensores simulados
# - Análise de risco cardíaco
# - Recomendações preventivas
# - Chatbot IBM Watson Assistant
# - Visão computacional por upload de Raio X de Tórax
# - Consulta às bases das fases anteriores
# ============================================================

from typing import Any

from fastapi import (
    FastAPI,
    Body,
    HTTPException,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware

from services.sensor_service import (
    normalizar_dados_sensor,
    simular_payload_iot,
    simular_lote_iot,
)

from services.risk_service import calcular_risco_cardiaco
from services.recommendation_service import gerar_recomendacao

from services.vision_service import (
    status_vision,
    analisar_imagem_ecg,
    analisar_upload_raio_x,
)

from services.phase_integration_service import obter_status_integracao

from services.knowledge_service import (
    consultar_conhecimento,
    gerar_resposta_baseada_em_conhecimento,
)

from services.chatbot_service import (
    status_chatbot,
    enviar_mensagem_chatbot,
    obter_mensagem_inicial,
    reiniciar_sessao_chatbot,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="CardioIA - Backend Fase 7",
    description=(
        "Backend integrador da CardioIA com IoT simulado, análise de risco, "
        "recomendação inteligente, chatbot, visão computacional por raio X "
        "e consulta às bases das fases anteriores."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROTAS BASE
# ============================================================

@app.get("/")
def root() -> dict[str, Any]:
    return {
        "app": "CardioIA",
        "phase": "Fase 7",
        "status": "online",
        "message": "Backend CardioIA operacional.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check() -> dict[str, Any]:
    """
    Verifica a saúde geral do backend e dos módulos principais.
    """

    chatbot = status_chatbot()
    vision = status_vision()

    return {
        "status": "ok",
        "backend": "online",
        "modules": {
            "iot": "simulation_ready",
            "risk": "available",
            "recommendation": "available",
            "chatbot": "configured" if chatbot.get("configured") else "not_configured",
            "vision": vision.get("mode", "unknown"),
            "knowledge": "available",
        },
        "chatbot_configured": chatbot.get("configured", False),
        "vision_model_found": vision.get("model_found", False),
        "vision_class_indices_found": vision.get("class_indices_found", False),
        "vision_tensorflow_required": vision.get("tensorflow_required", True),
    }


@app.get("/api/integration/status")
def integration_status() -> dict[str, Any]:
    """
    Retorna o status da integração entre as fases do projeto.
    """

    return obter_status_integracao()


# ============================================================
# IOT / SENSORES
# ============================================================

@app.post("/api/sensors/normalize")
def normalize_sensor_data(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Normaliza payload recebido de sensores, Web, Mobile ou simulação.
    """

    try:
        dados = normalizar_dados_sensor(payload)

        return {
            "status": "success",
            "origin": "payload_normalization",
            "sensor_data": dados,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao normalizar payload dos sensores: {exc}",
        )


@app.get("/api/iot/simulate")
def simulate_iot_data(cenario: str = "normal") -> dict[str, Any]:
    """
    Simula o mesmo payload que seria enviado pelo ESP32/Wokwi.

    Cenários aceitos:
    - normal
    - atencao
    - risco_alto
    - critico
    - offline_buffer
    - aleatorio
    """

    try:
        dados = simular_payload_iot(cenario)
        risco = calcular_risco_cardiaco(dados)
        recomendacao = gerar_recomendacao(risco)

        return {
            "status": "success",
            "origin": "esp32_wokwi_simulation",
            "scenario": cenario,
            "sensor_data": dados,
            "risk_analysis": risco,
            "recommendation": recomendacao,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao simular dados IoT: {exc}",
        )


@app.get("/api/iot/simulate/batch")
def simulate_iot_batch(
    cenario: str = "aleatorio",
    quantidade: int = 10,
) -> dict[str, Any]:
    """
    Gera um lote de medições simuladas para dashboard, gráficos ou histórico.
    """

    try:
        quantidade = max(1, min(int(quantidade), 100))

        registros = simular_lote_iot(
            cenario=cenario,
            quantidade=quantidade,
        )

        analisados = []

        for item in registros:
            risco = calcular_risco_cardiaco(item)
            recomendacao = gerar_recomendacao(risco)

            analisados.append({
                "sensor_data": item,
                "risk_analysis": risco,
                "recommendation": recomendacao,
            })

        return {
            "status": "success",
            "origin": "esp32_wokwi_batch_simulation",
            "scenario": cenario,
            "total": len(analisados),
            "records": analisados,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao gerar lote IoT simulado: {exc}",
        )


@app.get("/api/sensors/simulate")
def simulate_sensor_data(cenario: str = "normal") -> dict[str, Any]:
    """
    Endpoint mantido por compatibilidade com versões anteriores.
    Internamente usa a simulação IoT atual.
    """

    return simulate_iot_data(cenario)


# ============================================================
# ANÁLISE DE RISCO
# ============================================================

@app.post("/api/analyze")
def analyze_patient(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Endpoint principal para análise do paciente.

    Payload esperado do ESP32/Wokwi:

    {
        "patient_id": "PACIENTE_IOT_001",
        "heart_rate": 87,
        "temperature": 36.8,
        "oxygen_level": 97.0,
        "source": "iot_micropython_oled"
    }
    """

    try:
        dados = normalizar_dados_sensor(payload)
        risco = calcular_risco_cardiaco(dados)
        recomendacao = gerar_recomendacao(risco)

        return {
            "status": "success",
            "origin": "api_received_payload",
            "sensor_data": dados,
            "risk_analysis": risco,
            "recommendation": recomendacao,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao analisar sinais vitais: {exc}",
        )


@app.post("/api/risk")
def risk_only(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Retorna somente a análise de risco, sem recomendação.
    """

    try:
        dados = normalizar_dados_sensor(payload)
        risco = calcular_risco_cardiaco(dados)

        return {
            "status": "success",
            "origin": "risk_only",
            "sensor_data": dados,
            "risk_analysis": risco,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao calcular risco: {exc}",
        )


@app.post("/api/recommendation")
def recommendation_only(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Retorna análise de risco e recomendação preventiva.
    """

    try:
        dados = normalizar_dados_sensor(payload)
        risco = calcular_risco_cardiaco(dados)
        recomendacao = gerar_recomendacao(risco)

        return {
            "status": "success",
            "origin": "recommendation_only",
            "sensor_data": dados,
            "risk_analysis": risco,
            "recommendation": recomendacao,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao gerar recomendação: {exc}",
        )


# ============================================================
# VISÃO COMPUTACIONAL
# ============================================================

@app.get("/api/vision/status")
def vision_module_status() -> dict[str, Any]:
    """
    Retorna o status do módulo de visão computacional.
    """

    return status_vision()


@app.post("/api/vision")
def vision_analysis(payload: dict = Body(default={})) -> dict[str, Any]:
    """
    Endpoint antigo mantido por compatibilidade.

    A versão atual da visão computacional está preparada para análise
    de raio X de tórax via upload no endpoint /api/vision/xray.
    """

    image_name = (
        payload.get("image_name")
        or payload.get("filename")
        or payload.get("image")
    )

    return analisar_imagem_ecg(image_name)


@app.post("/api/vision/xray")
async def vision_xray_analysis(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Recebe uma imagem de raio X de tórax enviada pela Web
    e retorna a classificação prevista pelo modelo treinado.

    Formatos esperados:
    - .jpg
    - .jpeg
    - .png
    - .bmp
    - .webp
    """

    try:
        if file.filename is None or not file.filename.strip():
            raise ValueError("Nome do arquivo não informado.")

        resultado = analisar_upload_raio_x(
            file_object=file.file,
            filename=file.filename,
        )

        return {
            "status": "success",
            "origin": "web_upload",
            "filename": file.filename,
            "analysis": resultado,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao analisar imagem de raio X: {exc}",
        )


# ============================================================
# CHATBOT
# ============================================================

@app.get("/api/chatbot/status")
def chatbot_module_status() -> dict[str, Any]:
    """
    Retorna o status de configuração do chatbot.
    """

    return status_chatbot()


@app.get("/api/chatbot/welcome")
def chatbot_welcome(session_id: str | None = None) -> dict[str, Any]:
    """
    Retorna mensagem inicial do chatbot.
    """

    try:
        return obter_mensagem_inicial(session_id=session_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter mensagem inicial do chatbot: {exc}",
        )


@app.post("/api/chatbot/message")
def chatbot_message(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Envia uma mensagem para o chatbot.

    Payload esperado:
    {
        "message": "Olá, estou com dor no peito",
        "session_id": "opcional"
    }
    """

    message = payload.get("message", "")
    session_id = payload.get("session_id")

    if not str(message).strip():
        raise HTTPException(
            status_code=400,
            detail="O campo 'message' é obrigatório.",
        )

    try:
        return enviar_mensagem_chatbot(
            user_message=message,
            session_id=session_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao comunicar com o chatbot: {exc}",
        )


@app.post("/api/chatbot/restart")
def chatbot_restart(payload: dict = Body(default={})) -> dict[str, Any]:
    """
    Reinicia a sessão do chatbot.

    Payload opcional:
    {
        "session_id": "sessao_atual"
    }
    """

    session_id = payload.get("session_id")

    try:
        return reiniciar_sessao_chatbot(session_id=session_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao reiniciar sessão do chatbot: {exc}",
        )


# ============================================================
# CONHECIMENTO / BASES DAS FASES ANTERIORES
# ============================================================

@app.post("/api/knowledge/search")
def knowledge_search(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Busca informações nas bases integradas das fases anteriores.

    Payload esperado:
    {
        "query": "quais sinais indicam risco cardíaco?"
    }
    """

    query = payload.get("query", "")

    if not str(query).strip():
        raise HTTPException(
            status_code=400,
            detail="O campo 'query' é obrigatório.",
        )

    try:
        return consultar_conhecimento(query)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao consultar conhecimento: {exc}",
        )


@app.post("/api/knowledge/answer")
def knowledge_answer(payload: dict = Body(...)) -> dict[str, Any]:
    """
    Gera uma resposta textual baseada nas bases integradas.
    """

    query = payload.get("query", "")

    if not str(query).strip():
        raise HTTPException(
            status_code=400,
            detail="O campo 'query' é obrigatório.",
        )

    try:
        return {
            "status": "success",
            "query": query,
            "answer": gerar_resposta_baseada_em_conhecimento(query),
            "search": consultar_conhecimento(query),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao gerar resposta baseada em conhecimento: {exc}",
        )


# ============================================================
# ROTAS DE APOIO PARA FRONTEND/MOBILE
# ============================================================

@app.get("/api/modules")
def list_modules() -> dict[str, Any]:
    """
    Lista os principais módulos disponíveis para Web e Mobile.
    """

    return {
        "status": "success",
        "modules": [
            {
                "name": "IoT Simulado",
                "description": "Simulação dos sinais vitais enviados pelo ESP32/Wokwi.",
                "endpoints": [
                    "GET /api/iot/simulate",
                    "GET /api/iot/simulate/batch",
                    "POST /api/analyze",
                ],
            },
            {
                "name": "Análise de Risco",
                "description": "Classificação heurística de risco cardíaco.",
                "endpoints": [
                    "POST /api/analyze",
                    "POST /api/risk",
                    "POST /api/recommendation",
                ],
            },
            {
                "name": "Visão Computacional",
                "description": "Classificação de raio X de tórax via upload de imagem.",
                "endpoints": [
                    "GET /api/vision/status",
                    "POST /api/vision/xray",
                ],
            },
            {
                "name": "Chatbot",
                "description": "Assistente conversacional com IBM Watson ou fallback local.",
                "endpoints": [
                    "GET /api/chatbot/status",
                    "GET /api/chatbot/welcome",
                    "POST /api/chatbot/message",
                    "POST /api/chatbot/restart",
                ],
            },
            {
                "name": "Conhecimento",
                "description": "Consulta às bases clínicas e materiais das fases anteriores.",
                "endpoints": [
                    "POST /api/knowledge/search",
                    "POST /api/knowledge/answer",
                ],
            },
            {
                "name": "Integração",
                "description": "Status da integração geral da Fase 7.",
                "endpoints": [
                    "GET /api/integration/status",
                    "GET /api/health",
                    "GET /api/modules",
                ],
            },
        ],
    }