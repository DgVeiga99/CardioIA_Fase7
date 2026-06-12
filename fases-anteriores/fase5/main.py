# ============================================================================================================
#        ATIVIDADE FASE 5 - Capítulo 1 -Assistente Cardiológico Inteligente: Experiência do Paciente
# ============================================================================================================
#                                   ASSISTENTE CARDIOLÓGICO VIRTUAL
# ------------------------------------------------------------------------------------------------------------
"""
# Autor.....: Diego Nunes Veiga
# RM........: 560658
# Turma.....: Graduação - 2TIAOR
# Data......: 26/03/2026
# Assunto...: ASSISTENTE CARDIOLÓGICO VIRTUAL
"""

#============================================================================================================
#                        INFORMAÇÕES COLETADAS PARA DESENVOLVIMENTO DO SOFTWARE
#============================================================================================================

# O software desenvolvido em Python utilizando o framework Flask tem como objetivo implementar um Assistente
# Cardiológico Inteligente (CardioIA), capaz de interagir com o usuário por meio de linguagem natural.
# O sistema simula um atendimento inicial em saúde, auxiliando o paciente com informações sobre sintomas,
# exames cardiológicos, situações de emergência e orientações de preparo para exames.

# O funcionamento do sistema é baseado em regras de Processamento de Linguagem Natural (NLP), onde as mensagens
# do usuário são analisadas para identificação de intenções (intents) e entidades (entities), permitindo que
# o chatbot forneça respostas adequadas conforme o contexto da conversa.

# O sistema é responsável por tratar os seguintes tipos de interação:
#   * Identificação de sintomas leves - fornecendo orientações básicas e recomendando acompanhamento médico
#   * Identificação de sintomas graves - priorizando a segurança do usuário e direcionando para atendimento emergencial
#   * Retirada de duvidas sobre os exames - informa qual o procedimento do exame
#   * Orientação de preparo para exames - informando cuidados necessários antes da realização do procedimento
#   * Controle de fluxo conversacional - utilizando respostas afirmativas e negativas para guiar a interação

# Limitações do sistema:
#   * Não realiza diagnóstico médico
#   * Não substitui avaliação de um profissional de saúde
#   * Atua exclusivamente como suporte informativo e educacional


# ============================================================================================================
#                                 BIBLIOTECAS, LISTAS E DICIONÁRIOS
# ============================================================================================================

from flask import Flask, render_template, request, jsonify, session
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


# Instância para chamada do programa principal
app = Flask(__name__)
app.secret_key = "cardioia_chave_secreta_trocar_em_producao"


# CONFIGURAÇÕES DO WATSON
API_KEY = "7-s9qjtizkDPpmgkjur5KPclYNFCNRXFzMapsvN7nE_t"
SERVICE_URL = "https://api.us-south.assistant.watson.cloud.ibm.com/instances/d2c8cf52-de68-4136-ac61-c0dda25f3b72"
ASSISTANT_ID = "2f72b177-cd1b-4070-8ae1-eabc809e8d04"
WATSON_VERSION = "2024-08-25"

authenticator = IAMAuthenticator(API_KEY)
assistant = AssistantV2(version=WATSON_VERSION,authenticator=authenticator)
assistant.set_service_url(SERVICE_URL)


#=============================================================================================================
#                                      PROCEDIMENTOS E FUNÇÕES
#=============================================================================================================


# Cria uma nova sessão no Watson Assistant e retorna o session_id.
def create_watson_session():
    response = assistant.create_session(assistant_id=ASSISTANT_ID).get_result()
    return response["session_id"]


# Encerra uma sessão existente no Watson Assistant.
def delete_watson_session(session_id):
    assistant.delete_session(assistant_id=ASSISTANT_ID,session_id=session_id).get_result()


# Extrai e consolida os textos retornados pelo Watson.
def extract_text_from_response(response):
    generic_items = response.get("output", {}).get("generic", [])
    texts = []

    for item in generic_items:
        if item.get("response_type") == "text":
            text = item.get("text", "").strip()
            if text:
                texts.append(text)

    if not texts:
        return "Não foi possível obter uma resposta do assistente neste momento."

    return "\n".join(texts)


# Envia a mensagem do usuário para o Watson e retorna a resposta textual.
def send_message_to_watson(user_message, session_id):
    response = assistant.message(
        assistant_id=ASSISTANT_ID,
        session_id=session_id,
        input={"message_type": "text","text": user_message}
    ).get_result()

    return extract_text_from_response(response)

# Busca a mensagem inicial do Watson.
def get_welcome_message(session_id):
    return send_message_to_watson("", session_id)


# Renderiza a interface principal e cria sessão no Watson caso ainda não exista.
@app.route("/")
def index():
    try:
        if "watson_session_id" not in session:
            session["watson_session_id"] = create_watson_session()

        return render_template("index.html")

    except Exception as exc:
        return f"Erro ao criar sessão no Watson: {str(exc)}", 500


# Retorna a mensagem inicial configurada no Watson.
@app.route("/welcome", methods=["GET"])
def welcome():
    try:
        if "watson_session_id" not in session:
            session["watson_session_id"] = create_watson_session()

        welcome_text = get_welcome_message(session["watson_session_id"])
        return jsonify({"reply": welcome_text})

    except Exception as exc:
        return jsonify({"reply": f"Erro ao obter mensagem inicial: {str(exc)}"}), 500


# Recebe a mensagem do usuário, envia ao Watson e devolve a resposta.
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()

    if not user_message:
        return jsonify({"reply": "Digite uma mensagem para continuar."}), 400

    try:
        if "watson_session_id" not in session:
            session["watson_session_id"] = create_watson_session()

        reply = send_message_to_watson(
            user_message=user_message,
            session_id=session["watson_session_id"]
        )

        return jsonify({"reply": reply})

    except Exception as exc:
        return jsonify({"reply": f"Erro ao consultar o Watson: {str(exc)}"}), 500


# Reinicia a conversa do usuário, fechando a sessão atual e criando outra.
@app.route("/reset-session", methods=["POST"])
def reset_session():

    try:
        old_session_id = session.get("watson_session_id")

        if old_session_id:
            try:
                delete_watson_session(old_session_id)
            except Exception:
                pass

        session["watson_session_id"] = create_watson_session()
        welcome_text = get_welcome_message(session["watson_session_id"])

        return jsonify({
            "message": "Sessão reiniciada com sucesso.",
            "welcome": welcome_text
        })

    except Exception as exc:
        return jsonify({"message": f"Erro ao reiniciar sessão: {str(exc)}"}), 500


# ============================================================================================================
#                                         PROGRAMA PRINCIPAL
# ============================================================================================================


if __name__ == "__main__":
    app.run(debug=True)