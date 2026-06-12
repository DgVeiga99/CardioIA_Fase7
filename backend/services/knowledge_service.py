# ============================================================
# CardioIA - Fase 7
# Serviço de Conhecimento
#
# Funções principais:
# - consultar_conhecimento()
# - gerar_resposta_baseada_em_conhecimento()
#
# Este serviço realiza uma busca simples nas bases integradas
# das fases anteriores da CardioIA.
# ============================================================

from typing import Any

from services.data_service import (
    carregar_textos_clinicos_fase1,
    carregar_mapa_conhecimento_fase2,
    carregar_intents_fase5,
)


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto para busca simples.
    """

    return str(texto or "").lower().strip()


def extrair_palavras_relevantes(consulta: str) -> list[str]:
    """
    Extrai palavras relevantes da consulta.

    Remove palavras muito curtas e alguns termos genéricos.
    """

    consulta_normalizada = normalizar_texto(consulta)

    palavras = [
        palavra.strip(".,;:!?()[]{}'\"")
        for palavra in consulta_normalizada.split()
        if len(palavra.strip(".,;:!?()[]{}'\"")) >= 4
    ]

    stopwords = {
        "para",
        "como",
        "qual",
        "quais",
        "sobre",
        "entre",
        "dentro",
        "onde",
        "quando",
        "porque",
        "isso",
        "essa",
        "esse",
        "pela",
        "pelo",
        "cardioia",
        "paciente",
        "sistema",
    }

    return [
        palavra
        for palavra in palavras
        if palavra not in stopwords
    ]


# ============================================================
# BUSCA NOS TEXTOS CLÍNICOS DA FASE 1
# ============================================================

def buscar_em_textos_clinicos(consulta: str) -> list[dict[str, Any]]:
    """
    Busca palavras-chave nos textos clínicos da Fase 1.
    """

    palavras = extrair_palavras_relevantes(consulta)
    textos = carregar_textos_clinicos_fase1()
    resultados = []

    if not palavras:
        return []

    for nome_arquivo, conteudo in textos.items():
        if not conteudo:
            continue

        conteudo_normalizado = normalizar_texto(conteudo)

        pontuacao = sum(
            1
            for palavra in palavras
            if palavra in conteudo_normalizado
        )

        if pontuacao > 0:
            trecho = conteudo[:700].replace("\n", " ").strip()

            resultados.append({
                "source": nome_arquivo,
                "score": pontuacao,
                "excerpt": trecho,
            })

    resultados.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return resultados[:3]


# ============================================================
# BUSCA NO MAPA DE CONHECIMENTO DA FASE 2
# ============================================================

def buscar_no_mapa_conhecimento(consulta: str) -> list[dict[str, Any]]:
    """
    Busca simples no mapa de conhecimento da Fase 2.

    Funciona mesmo que o CSV tenha nomes de colunas diferentes.
    """

    palavras = extrair_palavras_relevantes(consulta)
    registros = carregar_mapa_conhecimento_fase2()
    resultados = []

    if not palavras:
        return []

    for registro in registros:
        texto_registro = " ".join(
            str(valor)
            for valor in registro.values()
            if valor is not None
        )

        texto_normalizado = normalizar_texto(texto_registro)

        pontuacao = sum(
            1
            for palavra in palavras
            if palavra in texto_normalizado
        )

        if pontuacao > 0:
            resultados.append({
                "score": pontuacao,
                "data": registro,
            })

    resultados.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return resultados[:5]


# ============================================================
# BUSCA NAS INTENTS DA FASE 5
# ============================================================

def buscar_intencoes_chatbot(consulta: str) -> list[dict[str, Any]]:
    """
    Busca simples nos intents do chatbot da Fase 5.
    """

    palavras = extrair_palavras_relevantes(consulta)
    intents = carregar_intents_fase5()
    resultados = []

    if not palavras:
        return []

    for intent in intents:
        texto_intent = " ".join(
            str(valor)
            for valor in intent.values()
            if valor is not None
        )

        texto_normalizado = normalizar_texto(texto_intent)

        pontuacao = sum(
            1
            for palavra in palavras
            if palavra in texto_normalizado
        )

        if pontuacao > 0:
            resultados.append({
                "score": pontuacao,
                "intent": intent,
            })

    resultados.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return resultados[:5]


# ============================================================
# CONSULTA INTEGRADA
# ============================================================

def consultar_conhecimento(consulta: str) -> dict[str, Any]:
    """
    Consulta integrada nos materiais das fases anteriores.

    Retorna:
    - resultados em textos clínicos
    - resultados no mapa de conhecimento
    - intents relacionadas do chatbot
    """

    consulta = str(consulta or "").strip()

    textos_clinicos = buscar_em_textos_clinicos(consulta)
    mapa_conhecimento = buscar_no_mapa_conhecimento(consulta)
    intents = buscar_intencoes_chatbot(consulta)

    return {
        "query": consulta,
        "keywords": extrair_palavras_relevantes(consulta),
        "clinical_texts": textos_clinicos,
        "knowledge_map": mapa_conhecimento,
        "chatbot_intents": intents,
        "has_results": bool(
            textos_clinicos
            or mapa_conhecimento
            or intents
        ),
    }


# ============================================================
# RESPOSTA TEXTUAL BASEADA NO CONHECIMENTO
# ============================================================

def gerar_resposta_baseada_em_conhecimento(consulta: str) -> str:
    """
    Gera uma resposta textual simples usando os materiais integrados.
    """

    resultado = consultar_conhecimento(consulta)

    if not resultado["has_results"]:
        return (
            "Não encontrei uma referência direta nas bases integradas das fases anteriores. "
            "Mesmo assim, recomenda-se avaliar os sinais vitais, observar sintomas associados "
            "e encaminhar o paciente para avaliação profissional em caso de alteração relevante."
        )

    if resultado["clinical_texts"]:
        fonte = resultado["clinical_texts"][0]

        return (
            "Com base nos materiais clínicos integrados da CardioIA, foram encontradas "
            f"informações relacionadas em {fonte['source']}. "
            "A análise sugere que alterações em sinais como batimentos cardíacos, temperatura "
            "e oxigenação devem ser interpretadas em conjunto com sintomas, histórico do paciente "
            "e avaliação profissional."
        )

    if resultado["knowledge_map"]:
        return (
            "O mapa de conhecimento da CardioIA identificou relação com a consulta informada. "
            "A recomendação é correlacionar os sintomas relatados com os sinais vitais monitorados "
            "e utilizar o score de risco como apoio à decisão."
        )

    if resultado["chatbot_intents"]:
        return (
            "A consulta possui relação com as intenções do assistente conversacional da CardioIA. "
            "O sistema pode apoiar a triagem inicial, orientar o usuário e complementar a análise "
            "dos sinais vitais, mas não substitui avaliação médica."
        )

    return (
        "A consulta foi processada, mas não foi possível gerar uma resposta específica "
        "com base nas informações disponíveis."
    )