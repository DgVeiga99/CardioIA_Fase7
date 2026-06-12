import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  Platform
} from "react-native";
import { StatusBar } from "expo-status-bar";

const API_BASE_URL = "http://192.168.0.147:8000";

export default function App() {
  const [screen, setScreen] = useState("login");
  const [loggedUser, setLoggedUser] = useState("");
  const [patientId, setPatientId] = useState("PAC001");
  const [heartRate, setHeartRate] = useState("132");
  const [temperature, setTemperature] = useState("38.4");
  const [oxygenLevel, setOxygenLevel] = useState("93");
  const [riskResult, setRiskResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [chatSessionId, setChatSessionId] = useState(null);
  const [chatMessage, setChatMessage] = useState("Estou com dor no peito e falta de ar.");
  const [chatResponse, setChatResponse] = useState(null);

  const [backendStatus, setBackendStatus] = useState(null);

  async function login() {
    if (!loggedUser.trim()) {
      setLoggedUser("Aluno FIAP");
    }
    setScreen("dashboard");
  }

  async function analyzeRisk() {
    setLoading(true);
    setRiskResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          patient_id: patientId,
          heart_rate: Number(heartRate),
          temperature: Number(temperature),
          oxygen_level: Number(oxygenLevel),
          source: "mobile"
        })
      });

      const data = await response.json();
      setRiskResult(data);
    } catch (error) {
      setRiskResult({
        error: true,
        message: "Não foi possível conectar ao backend. Verifique se o FastAPI está rodando e se o IP está correto.",
        details: String(error)
      });
    } finally {
      setLoading(false);
    }
  }

  async function createChatSession() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/session`, {
        method: "POST"
      });

      const data = await response.json();
      setChatSessionId(data.session_id || data.new_session_id || null);
      setChatResponse({
        answer: "Sessão do chatbot criada com sucesso."
      });
    } catch (error) {
      setChatResponse({
        answer: "Erro ao criar sessão do chatbot. Verifique o backend.",
        details: String(error)
      });
    }
  }

  async function sendChatMessage() {
    setLoading(true);

    try {
      let activeSession = chatSessionId;

      if (!activeSession) {
        const sessionResponse = await fetch(`${API_BASE_URL}/api/chatbot/session`, {
          method: "POST"
        });
        const sessionData = await sessionResponse.json();
        activeSession = sessionData.session_id || sessionData.new_session_id;
        setChatSessionId(activeSession);
      }

      const response = await fetch(`${API_BASE_URL}/api/chatbot/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: chatMessage,
          session_id: activeSession
        })
      });

      const data = await response.json();
      setChatResponse(data);
    } catch (error) {
      setChatResponse({
        answer: "Não foi possível enviar a mensagem ao chatbot IBM Watson.",
        details: String(error)
      });
    } finally {
      setLoading(false);
    }
  }

  async function checkBackendStatus() {
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/mvp/status`);
      const data = await response.json();
      setBackendStatus(data);
    } catch (error) {
      setBackendStatus({
        error: true,
        message: "Backend indisponível ou IP incorreto.",
        details: String(error)
      });
    } finally {
      setLoading(false);
    }
  }

  function RiskBadge({ level }) {
    let label = level || "indefinido";

    return (
      <View style={styles.badge}>
        <Text style={styles.badgeText}>{String(label).toUpperCase()}</Text>
      </View>
    );
  }

  function Header() {
    return (
      <View style={styles.header}>
        <Text style={styles.logo}>CardioIA</Text>
        <Text style={styles.headerSubtitle}>Monitoramento Inteligente Cardíaco</Text>
      </View>
    );
  }

  function Menu() {
    return (
      <View style={styles.menu}>
        <TouchableOpacity style={styles.menuButton} onPress={() => setScreen("dashboard")}>
          <Text style={styles.menuText}>Dashboard</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuButton} onPress={() => setScreen("risk")}>
          <Text style={styles.menuText}>Risco</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuButton} onPress={() => setScreen("chatbot")}>
          <Text style={styles.menuText}>Chatbot</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuButton} onPress={() => setScreen("status")}>
          <Text style={styles.menuText}>Status</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (screen === "login") {
    return (
      <SafeAreaView style={styles.safe}>
        <StatusBar style="light" />
        <View style={styles.loginContainer}>
          <Text style={styles.loginTitle}>CardioIA Mobile</Text>
          <Text style={styles.loginSubtitle}>
            Plataforma mobile integrada ao backend FastAPI, chatbot IBM Watson e sensores IoT.
          </Text>

          <TextInput
            style={styles.input}
            placeholder="Digite seu nome"
            placeholderTextColor="#64748b"
            value={loggedUser}
            onChangeText={setLoggedUser}
          />

          <TouchableOpacity style={styles.primaryButton} onPress={login}>
            <Text style={styles.primaryButtonText}>Entrar no sistema</Text>
          </TouchableOpacity>

          <Text style={styles.footer}>FIAP - Fase 7 | MVP CardioIA</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.container}>
        <Header />
        <Menu />

        {screen === "dashboard" && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Dashboard do Paciente</Text>
            <Text style={styles.text}>
              Usuário: {loggedUser || "Aluno FIAP"}
            </Text>

            <View style={styles.metricGrid}>
              <View style={styles.metricCard}>
                <Text style={styles.metricLabel}>Batimentos</Text>
                <Text style={styles.metricValue}>{heartRate} bpm</Text>
              </View>

              <View style={styles.metricCard}>
                <Text style={styles.metricLabel}>Temperatura</Text>
                <Text style={styles.metricValue}>{temperature} °C</Text>
              </View>

              <View style={styles.metricCard}>
                <Text style={styles.metricLabel}>Oxigenação</Text>
                <Text style={styles.metricValue}>{oxygenLevel}%</Text>
              </View>
            </View>

            <Text style={styles.text}>
              Dados simulados a partir da arquitetura IoT com ESP32, DHT22, potenciômetro e OLED no Wokwi.
            </Text>

            <TouchableOpacity style={styles.primaryButton} onPress={() => setScreen("risk")}>
              <Text style={styles.primaryButtonText}>Ir para análise de risco</Text>
            </TouchableOpacity>
          </View>
        )}

        {screen === "risk" && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Análise de Risco Cardíaco</Text>

            <Text style={styles.label}>ID do paciente</Text>
            <TextInput style={styles.input} value={patientId} onChangeText={setPatientId} />

            <Text style={styles.label}>Batimentos cardíacos</Text>
            <TextInput
              style={styles.input}
              value={heartRate}
              onChangeText={setHeartRate}
              keyboardType="numeric"
            />

            <Text style={styles.label}>Temperatura</Text>
            <TextInput
              style={styles.input}
              value={temperature}
              onChangeText={setTemperature}
              keyboardType="numeric"
            />

            <Text style={styles.label}>Oxigenação</Text>
            <TextInput
              style={styles.input}
              value={oxygenLevel}
              onChangeText={setOxygenLevel}
              keyboardType="numeric"
            />

            <TouchableOpacity style={styles.primaryButton} onPress={analyzeRisk}>
              <Text style={styles.primaryButtonText}>
                {loading ? "Analisando..." : "Executar análise"}
              </Text>
            </TouchableOpacity>

            {riskResult && (
              <View style={styles.resultBox}>
                {riskResult.error ? (
                  <>
                    <Text style={styles.errorText}>{riskResult.message}</Text>
                    <Text style={styles.smallText}>{riskResult.details}</Text>
                  </>
                ) : (
                  <>
                    <Text style={styles.resultTitle}>Resultado da IA</Text>
                    <RiskBadge level={riskResult.risk_level} />
                    <Text style={styles.resultText}>
                      Score de risco: {riskResult.risk_score}
                    </Text>
                    <Text style={styles.resultText}>
                      Alerta: {riskResult.alert ? "Sim" : "Não"}
                    </Text>
                    <Text style={styles.resultText}>
                      Recomendação: {riskResult.recommendation?.message || riskResult.recommendation || "Não informado"}
                    </Text>
                  </>
                )}
              </View>
            )}
          </View>
        )}

        {screen === "chatbot" && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Chatbot IBM Watson</Text>
            <Text style={styles.text}>
              Assistente conversacional integrado ao backend Python da CardioIA.
            </Text>

            <TouchableOpacity style={styles.secondaryButton} onPress={createChatSession}>
              <Text style={styles.secondaryButtonText}>Criar sessão Watson</Text>
            </TouchableOpacity>

            <Text style={styles.label}>Mensagem</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={chatMessage}
              onChangeText={setChatMessage}
              multiline
            />

            <TouchableOpacity style={styles.primaryButton} onPress={sendChatMessage}>
              <Text style={styles.primaryButtonText}>
                {loading ? "Enviando..." : "Enviar mensagem"}
              </Text>
            </TouchableOpacity>

            {chatSessionId && (
              <Text style={styles.smallText}>Sessão ativa: {chatSessionId}</Text>
            )}

            {chatResponse && (
              <View style={styles.resultBox}>
                <Text style={styles.resultTitle}>Resposta do assistente</Text>
                <Text style={styles.resultText}>
                  {chatResponse.answer || chatResponse.message || JSON.stringify(chatResponse, null, 2)}
                </Text>
              </View>
            )}
          </View>
        )}

        {screen === "status" && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Status da Integração</Text>

            <Text style={styles.text}>
              Esta tela demonstra a comunicação do aplicativo mobile com o backend unificado da CardioIA.
            </Text>

            <TouchableOpacity style={styles.primaryButton} onPress={checkBackendStatus}>
              <Text style={styles.primaryButtonText}>
                {loading ? "Verificando..." : "Verificar backend"}
              </Text>
            </TouchableOpacity>

            {backendStatus && (
              <View style={styles.resultBox}>
                {backendStatus.error ? (
                  <>
                    <Text style={styles.errorText}>{backendStatus.message}</Text>
                    <Text style={styles.smallText}>{backendStatus.details}</Text>
                  </>
                ) : (
                  <>
                    <Text style={styles.resultTitle}>Backend conectado</Text>
                    <Text style={styles.resultText}>
                      {JSON.stringify(backendStatus, null, 2)}
                    </Text>
                  </>
                )}
              </View>
            )}

            <View style={styles.statusList}>
              <Text style={styles.statusItem}>Backend FastAPI</Text>
              <Text style={styles.statusItem}>Análise de risco cardíaco</Text>
              <Text style={styles.statusItem}>Chatbot IBM Watson</Text>
              <Text style={styles.statusItem}>IoT Wokwi com MicroPython</Text>
              <Text style={styles.statusItem}>Frontend Web + Mobile Expo</Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#020617"
  },
  container: {
    flexGrow: 1,
    padding: 20,
    paddingTop: Platform.OS === "web" ? 30 : 50,
    backgroundColor: "#020617"
  },
  loginContainer: {
    flex: 1,
    minHeight: Platform.OS === "web" ? "100vh" : "100%",
    backgroundColor: "#020617",
    alignItems: "center",
    justifyContent: "center",
    padding: 24
  },
  loginTitle: {
    color: "#38bdf8",
    fontSize: 34,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 12
  },
  loginSubtitle: {
    color: "#cbd5e1",
    fontSize: 16,
    textAlign: "center",
    marginBottom: 28,
    maxWidth: 420
  },
  header: {
    marginBottom: 18
  },
  logo: {
    color: "#38bdf8",
    fontSize: 32,
    fontWeight: "bold"
  },
  headerSubtitle: {
    color: "#94a3b8",
    fontSize: 15,
    marginTop: 4
  },
  menu: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 18
  },
  menuButton: {
    backgroundColor: "#111827",
    borderColor: "#1f2937",
    borderWidth: 1,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12
  },
  menuText: {
    color: "#e5e7eb",
    fontWeight: "bold",
    fontSize: 13
  },
  card: {
    backgroundColor: "#111827",
    borderRadius: 22,
    padding: 20,
    borderWidth: 1,
    borderColor: "#1f2937",
    marginBottom: 20
  },
  cardTitle: {
    color: "#f8fafc",
    fontSize: 23,
    fontWeight: "bold",
    marginBottom: 14
  },
  text: {
    color: "#cbd5e1",
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 14
  },
  label: {
    color: "#94a3b8",
    fontSize: 13,
    fontWeight: "bold",
    marginBottom: 6,
    marginTop: 8
  },
  input: {
    width: "100%",
    backgroundColor: "#020617",
    color: "#f8fafc",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 14,
    padding: 14,
    fontSize: 15,
    marginBottom: 12
  },
  textArea: {
    minHeight: 90,
    textAlignVertical: "top"
  },
  primaryButton: {
    backgroundColor: "#0ea5e9",
    borderRadius: 14,
    paddingVertical: 15,
    paddingHorizontal: 18,
    alignItems: "center",
    marginTop: 8,
    marginBottom: 10
  },
  primaryButtonText: {
    color: "#f8fafc",
    fontWeight: "bold",
    fontSize: 15
  },
  secondaryButton: {
    backgroundColor: "#1e293b",
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 18,
    alignItems: "center",
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#334155"
  },
  secondaryButtonText: {
    color: "#38bdf8",
    fontWeight: "bold",
    fontSize: 15
  },
  footer: {
    color: "#64748b",
    marginTop: 24,
    fontSize: 13,
    textAlign: "center"
  },
  metricGrid: {
    gap: 12,
    marginBottom: 16
  },
  metricCard: {
    backgroundColor: "#020617",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: "#1e293b"
  },
  metricLabel: {
    color: "#94a3b8",
    fontSize: 13,
    marginBottom: 6
  },
  metricValue: {
    color: "#22c55e",
    fontSize: 28,
    fontWeight: "bold"
  },
  resultBox: {
    backgroundColor: "#020617",
    borderRadius: 16,
    padding: 16,
    marginTop: 12,
    borderWidth: 1,
    borderColor: "#334155"
  },
  resultTitle: {
    color: "#f8fafc",
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10
  },
  resultText: {
    color: "#cbd5e1",
    fontSize: 14,
    lineHeight: 21,
    marginBottom: 6
  },
  smallText: {
    color: "#94a3b8",
    fontSize: 12,
    marginTop: 8
  },
  errorText: {
    color: "#f87171",
    fontSize: 14,
    fontWeight: "bold",
    lineHeight: 21
  },
  badge: {
    alignSelf: "flex-start",
    backgroundColor: "#7f1d1d",
    borderRadius: 999,
    paddingVertical: 8,
    paddingHorizontal: 14,
    marginBottom: 10
  },
  badgeText: {
    color: "#fecaca",
    fontWeight: "bold",
    fontSize: 13
  },
  statusList: {
    marginTop: 18,
    gap: 10
  },
  statusItem: {
    color: "#22c55e",
    backgroundColor: "#020617",
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#1e293b"
  }
});