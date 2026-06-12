# ============================================================
# CardioIA - Fase 7
# Serviço de Recomendações
#
# Função principal:
# - gerar_recomendacao()
#
# Este serviço recebe o resultado da análise de risco cardíaco
# e gera uma recomendação textual para apoio à triagem.
# ============================================================

from typing import Any


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def gerar_recomendacao(resultado_risco: dict[str, Any]) -> dict[str, Any]:
    """
    Gera recomendação preventiva com base no nível de risco calculado.

    Entrada esperada:
    {
        "risk_score": 80,
        "risk_level": "alto",
        "alert": True,
        "general_status": "RISCO_ALTO",
        "reasons": [...]
    }

    Saída:
    {
        "priority": "...",
        "message": "...",
        "actions": [...],
        "based_on": [...]
    }

    Observação:
    Este módulo não substitui avaliação médica. Atua como apoio à triagem
    e à tomada de decisão no MVP.
    """

    risk_level = resultado_risco.get("risk_level", "baixo")
    reasons = resultado_risco.get("reasons", [])
    score = resultado_risco.get("risk_score", 0)
    general_status = resultado_risco.get("general_status", "NORMAL")

    if risk_level == "alto":
        return {
            "priority": "crítica",
            "risk_score": score,
            "risk_level": risk_level,
            "general_status": general_status,
            "message": (
                "Risco elevado identificado. Recomenda-se avaliação médica imediata, "
                "monitoramento contínuo dos sinais vitais e acionamento da equipe responsável."
            ),
            "actions": [
                "Repetir a medição para confirmar os dados.",
                "Verificar sintomas associados, como dor no peito, falta de ar, tontura ou confusão.",
                "Acionar suporte médico se os sinais persistirem ou piorarem.",
                "Priorizar o paciente na fila de triagem.",
            ],
            "based_on": reasons,
            "disclaimer": (
                "Esta recomendação é gerada por sistema de apoio e não substitui diagnóstico médico."
            ),
        }

    if risk_level == "moderado":
        return {
            "priority": "atenção",
            "risk_score": score,
            "risk_level": risk_level,
            "general_status": general_status,
            "message": (
                "Alterações relevantes foram detectadas. Recomenda-se acompanhar a evolução "
                "dos sinais vitais e realizar nova medição em curto intervalo."
            ),
            "actions": [
                "Realizar nova leitura dos sensores.",
                "Verificar se houve esforço físico recente, febre, ansiedade ou condição clínica associada.",
                "Manter observação preventiva.",
                "Comparar a leitura atual com o histórico do paciente.",
            ],
            "based_on": reasons,
            "disclaimer": (
                "Esta recomendação é gerada por sistema de apoio e não substitui diagnóstico médico."
            ),
        }

    if risk_level == "baixo_monitorado":
        return {
            "priority": "observação",
            "risk_score": score,
            "risk_level": risk_level,
            "general_status": general_status,
            "message": (
                "Há pequena alteração em pelo menos um sinal vital. O cenário não indica risco crítico, "
                "mas recomenda monitoramento preventivo."
            ),
            "actions": [
                "Acompanhar novas medições.",
                "Comparar com histórico do paciente.",
                "Observar sintomas adicionais.",
                "Reavaliar caso os sinais evoluam para piora.",
            ],
            "based_on": reasons,
            "disclaimer": (
                "Esta recomendação é gerada por sistema de apoio e não substitui diagnóstico médico."
            ),
        }

    return {
        "priority": "normal",
        "risk_score": score,
        "risk_level": risk_level,
        "general_status": general_status,
        "message": (
            "Indicadores dentro de uma faixa aceitável. Recomenda-se manter o monitoramento "
            "preventivo e acompanhar novas medições."
        ),
        "actions": [
            "Manter rotina de acompanhamento.",
            "Registrar nova medição periodicamente.",
            "Observar mudanças nos sinais vitais ao longo do tempo.",
        ],
        "based_on": reasons,
        "disclaimer": (
            "Esta recomendação é gerada por sistema de apoio e não substitui diagnóstico médico."
        ),
    }