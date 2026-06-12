# ============================================================
# CardioIA - Fase 7
# Serviço de Chatbot com IBM Watson Assistant
#
# Funções principais:
# - status_chatbot()
# - enviar_mensagem_chatbot()
# - obter_mensagem_inicial()
# - reiniciar_sessao_chatbot()
#
# Este serviço usa IBM Watson Assistant quando o .env está
# configurado corretamente. Caso contrário, utiliza fallback local
# para não quebrar o backend.
# ============================================================

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


WATSON_API_KEY = os.getenv("WATSON_API_KEY")
WATSON_SERVICE_URL = os.getenv("WATSON_SERVICE_URL")
WATSON_ASSISTANT_ID = os.getenv("WATSON_ASSISTANT_ID")
WATSON_VERSION = os.getenv("WATSON_VERSION")


# ============================================================
# FUNÇÕES DE STATUS
# ============================================================

def chatbot_configurado() -> bool:
    """
    Verifica se as credenciais obrigatórias do Watson foram carregadas.
    """

    return all([
        WATSON_API_KEY,
        WATSON_SERVICE_URL,
        WATSON_ASSISTANT_ID,
    ])


def status_chatbot() -> dict[str, Any]:
    """
    Retorna o status da configuração do chatbot.
    Não expõe dados sensíveis.
    """

    return {
        "provider": "IBM Watson Assistant",
        "configured": chatbot_configurado(),
        "api_key_configured": bool(WATSON_API_KEY),
        "service_url_configured": bool(WATSON_SERVICE_URL),
        "assistant_id_configured": bool(WATSON_ASSISTANT_ID),
        "version": WATSON_VERSION,
        "sdk_required_version": "ibm-watson==6.1.0",
        "env_file_found": ENV_PATH.exists(),
        "env_path": str(ENV_PATH),
    }


# ============================================================
# CLIENTE WATSON
# ============================================================

def criar_cliente_watson() -> AssistantV2:
    """
    Cria uma instância do cliente IBM Watson Assistant.
    """

    if not chatbot_configurado():
        raise RuntimeError(
            "Credenciais do IBM Watson Assistant não configuradas. "
            "Verifique WATSON_API_KEY, WATSON_SERVICE_URL e "
            "WATSON_ASSISTANT_ID no arquivo backend/.env."
        )

    authenticator = IAMAuthenticator(WATSON_API_KEY)

    assistant = AssistantV2(
        version=WATSON_VERSION,
        authenticator=authenticator,
    )

    assistant.set_service_url(WATSON_SERVICE_URL)

    return assistant


# ============================================================
# FALLBACK LOCAL
# ============================================================

def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto para regras simples do fallback local.
    """

    return str(texto or "").lower().strip()


def resposta_fallback_local(mensagem: str) -> dict[str, Any]:
    """
    Resposta local caso o Watson não esteja configurado.
    """

    texto = normalizar_texto(mensagem)

    if any(palavra in texto for palavra in ["risco", "cardiaco", "cardíaco", "infarto"]):
        answer = (
            "A CardioIA avalia sinais como batimentos cardíacos, temperatura e oxigenação "
            "para estimar um nível de risco. Em caso de dor no peito, falta de ar, tontura "
            "ou piora dos sinais, procure atendimento médico imediatamente."
        )

    elif any(palavra in texto for palavra in ["bpm", "batimento", "batimentos", "frequencia", "frequência"]):
        answer = (
            "Os batimentos cardíacos são analisados como um dos principais indicadores "
            "do sistema. Valores muito baixos ou muito altos aumentam o score de risco."
        )

    elif any(palavra in texto for palavra in ["oxigenacao", "oxigenação", "spo2", "saturacao", "saturação", "oxigenio", "oxigênio"]):
        answer = (
            "A oxigenação é interpretada como saturação simulada. Valores reduzidos podem "
            "indicar atenção ou risco elevado, dependendo do nível detectado."
        )

    elif any(palavra in texto for palavra in ["temperatura", "febre"]):
        answer = (
            "A temperatura corporal é usada como indicador auxiliar. Febre ou febre alta "
            "aumentam a pontuação de risco no sistema."
        )

    elif any(palavra in texto for palavra in ["raio x", "raiox", "xray", "tórax", "torax", "imagem"]):
        answer = (
            "O módulo de visão da CardioIA está preparado para receber imagens de raio X "
            "de tórax pela interface Web, realizar pré-processamento e retornar uma "
            "classificação com percentual de confiança."
        )

    elif any(palavra in texto for palavra in ["sensor", "esp32", "wokwi", "iot"]):
        answer = (
            "O módulo IoT utiliza ESP32 com sensores simulados no Wokwi. Como a comunicação "
            "direta com o backend local pode ser limitada, o backend possui endpoints de "
            "simulação compatíveis com o payload do dispositivo."
        )

    else:
        answer = (
            "Sou o assistente da CardioIA. Posso ajudar com dúvidas sobre sinais vitais, "
            "risco cardíaco, sensores IoT, visão computacional e funcionamento da solução."
        )

    return {
        "provider": "local_fallback",
        "configured": False,
        "session_id": "LOCAL_FALLBACK_SESSION",
        "message": mensagem,
        "answer": answer,
        "intents": [],
        "entities": [],
        "raw_output": {},
    }


# ============================================================
# SESSÕES WATSON
# ============================================================

def criar_sessao_chatbot() -> str:
    """
    Cria uma sessão no IBM Watson Assistant.
    """

    assistant = criar_cliente_watson()

    response = assistant.create_session(
        assistant_id=WATSON_ASSISTANT_ID,
    ).get_result()

    return response["session_id"]


def deletar_sessao_chatbot(session_id: str) -> dict[str, Any]:
    """
    Remove uma sessão ativa do Watson.
    """

    assistant = criar_cliente_watson()

    assistant.delete_session(
        assistant_id=WATSON_ASSISTANT_ID,
        session_id=session_id,
    ).get_result()

    return {
        "deleted": True,
        "session_id": session_id,
    }


def reiniciar_sessao_chatbot(session_id: str | None = None) -> dict[str, Any]:
    """
    Reinicia a conversa criando uma nova sessão no Watson.
    Caso o Watson não esteja configurado, reinicia em modo fallback local.
    """

    if not chatbot_configurado():
        return {
            "provider": "local_fallback",
            "old_session_id": session_id,
            "new_session_id": "LOCAL_FALLBACK_SESSION",
            "welcome": {
                "provider": "local_fallback",
                "answer": "Sessão local reiniciada. Como posso ajudar na CardioIA?",
                "session_id": "LOCAL_FALLBACK_SESSION",
            },
        }

    if session_id:
        try:
            deletar_sessao_chatbot(session_id)
        except Exception:
            pass

    new_session_id = criar_sessao_chatbot()

    return {
        "provider": "ibm_watson",
        "old_session_id": session_id,
        "new_session_id": new_session_id,
        "welcome": {
            "provider": "ibm_watson",
            "answer": "Sessão reiniciada com sucesso. Como posso ajudar?",
            "session_id": new_session_id,
        },
    }


# ============================================================
# EXTRAÇÃO DE RESPOSTAS DO WATSON
# ============================================================

def extrair_texto_resposta(response: dict[str, Any]) -> str:
    """
    Extrai as respostas textuais retornadas pelo Watson.
    """

    generic_items = response.get("output", {}).get("generic", [])
    textos = []

    for item in generic_items:
        if item.get("response_type") == "text":
            texto = str(item.get("text", "")).strip()

            if texto:
                textos.append(texto)

    if not textos:
        return "Não foi possível obter uma resposta do assistente neste momento."

    return "\n".join(textos)


def extrair_intents(response: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extrai as intenções identificadas pelo Watson.
    """

    return response.get("output", {}).get("intents", [])


def extrair_entities(response: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extrai as entidades identificadas pelo Watson.
    """

    return response.get("output", {}).get("entities", [])


# ============================================================
# ENVIO DE MENSAGENS
# ============================================================

def enviar_mensagem_chatbot(
    user_message: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Envia uma mensagem para o IBM Watson Assistant.

    Caso não receba session_id, cria uma nova sessão automaticamente.
    Se Watson não estiver configurado, usa fallback local.
    """

    mensagem = str(user_message or "").strip()

    if not mensagem:
        raise ValueError("A mensagem do usuário não pode estar vazia.")

    if not chatbot_configurado():
        return resposta_fallback_local(mensagem)

    assistant = criar_cliente_watson()

    active_session_id = session_id or criar_sessao_chatbot()

    response = assistant.message(
        assistant_id=WATSON_ASSISTANT_ID,
        session_id=active_session_id,
        input={
            "message_type": "text",
            "text": mensagem,
        },
    ).get_result()

    answer = extrair_texto_resposta(response)
    intents = extrair_intents(response)
    entities = extrair_entities(response)

    return {
        "provider": "ibm_watson",
        "configured": True,
        "session_id": active_session_id,
        "message": mensagem,
        "answer": answer,
        "intents": intents,
        "entities": entities,
        "raw_output": response.get("output", {}),
    }


def obter_mensagem_inicial(session_id: str | None = None) -> dict[str, Any]:
    """
    Retorna a mensagem inicial do assistente.
    """

    if not chatbot_configurado():
        return {
            "provider": "local_fallback",
            "configured": False,
            "session_id": "LOCAL_FALLBACK_SESSION",
            "answer": "Olá! Sou o assistente virtual da CardioIA. Como posso ajudar?",
            "intents": [],
            "entities": [],
        }

    active_session_id = session_id or criar_sessao_chatbot()

    try:
        return enviar_mensagem_chatbot(
            user_message="Olá",
            session_id=active_session_id,
        )

    except Exception as exc:
        return {
            "provider": "ibm_watson",
            "configured": True,
            "session_id": active_session_id,
            "answer": "Olá! Sou o assistente virtual da CardioIA. Como posso ajudar?",
            "intents": [],
            "entities": [],
            "error": str(exc),
        }