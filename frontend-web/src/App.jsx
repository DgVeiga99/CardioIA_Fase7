import { useEffect, useMemo, useRef, useState } from "react";
import "./styles.css";

const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

const initialForm = {
  patient_id: "PACIENTE_WEB_001",
  heart_rate: 88,
  temperature: 36.8,
  oxygen_level: 97,
  source: "frontend_web"
};

const sensorScenarios = [
  { value: "normal", label: "Normal" },
  { value: "atencao", label: "Atenção" },
  { value: "critico", label: "Crítico" },
  { value: "offline_buffer", label: "Buffer Offline" },
  { value: "aleatorio", label: "Aleatório" }
];

function App() {
  const [isLogged, setIsLogged] = useState(false);
  const [loginName, setLoginName] = useState("Diego Veiga");
  const [password, setPassword] = useState("cardioia");

  const [activeTab, setActiveTab] = useState("dashboard");

  const [apiStatus, setApiStatus] = useState("verificando");
  const [backendStatus, setBackendStatus] = useState(null);
  const [chatbotStatus, setChatbotStatus] = useState(null);
  const [visionStatus, setVisionStatus] = useState(null);
  const [integrationStatus, setIntegrationStatus] = useState(null);

  const [scenario, setScenario] = useState("normal");
  const [sensorSimulation, setSensorSimulation] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [analysis, setAnalysis] = useState(null);

  const [chatSessionId, setChatSessionId] = useState(null);
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([
    {
      role: "assistant",
      text:
        "Olá, sou o assistente da CardioIA. Posso ajudar com sinais vitais, risco cardíaco, sensores IoT e análise de raio X."
    }
  ]);

  const chatEndRef = useRef(null);

  const [xrayFile, setXrayFile] = useState(null);
  const [xrayPreview, setXrayPreview] = useState(null);
  const [xrayResult, setXrayResult] = useState(null);
  const [xrayError, setXrayError] = useState("");

  const [loading, setLoading] = useState({
    status: false,
    sensors: false,
    analysis: false,
    chatbot: false,
    restartChat: false,
    vision: false
  });

  const [globalError, setGlobalError] = useState("");

  useEffect(() => {
    loadPlatformStatus();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end"
    });
  }, [chatHistory]);

  useEffect(() => {
    if (apiStatus === "online" && isLogged) {
      restartChatSession(true);
    }
  }, [apiStatus, isLogged]);

  useEffect(() => {
    return () => {
      if (xrayPreview) {
        URL.revokeObjectURL(xrayPreview);
      }
    };
  }, [xrayPreview]);

  const currentSensorData = useMemo(() => {
    return sensorSimulation?.sensor_data || analysis?.sensor_data || form;
  }, [sensorSimulation, analysis, form]);

  function setLoadingKey(key, value) {
    setLoading((prev) => ({
      ...prev,
      [key]: value
    }));
  }

  function handleLogin(event) {
    event.preventDefault();

    if (!loginName.trim()) {
      setGlobalError("Digite o nome do usuário.");
      return;
    }

    if (!password.trim()) {
      setGlobalError("Digite a senha demonstrativa.");
      return;
    }

    setGlobalError("");
    setIsLogged(true);
  }

  function logout() {
    setIsLogged(false);
    setActiveTab("dashboard");
  }

  async function safeFetchJson(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Erro HTTP ${response.status}`);
    }

    return response.json();
  }

  async function loadPlatformStatus() {
    try {
      setGlobalError("");
      setLoadingKey("status", true);
      setApiStatus("verificando");

      const [health, chatbot, vision, integration] = await Promise.allSettled([
        safeFetchJson(`${API_URL}/api/health`),
        safeFetchJson(`${API_URL}/api/chatbot/status`),
        safeFetchJson(`${API_URL}/api/vision/status`),
        safeFetchJson(`${API_URL}/api/integration/status`)
      ]);

      if (health.status === "fulfilled") {
        setBackendStatus(health.value);
        setApiStatus("online");
      } else {
        setBackendStatus(null);
        setApiStatus("offline");
      }

      if (chatbot.status === "fulfilled") {
        setChatbotStatus(chatbot.value);
      }

      if (vision.status === "fulfilled") {
        setVisionStatus(vision.value);
      }

      if (integration.status === "fulfilled") {
        setIntegrationStatus(integration.value);
      }
    } catch (error) {
      console.error(error);
      setApiStatus("offline");
      setGlobalError("Não foi possível consultar o backend FastAPI.");
    } finally {
      setLoadingKey("status", false);
    }
  }

  async function simulateSensors() {
    try {
      setGlobalError("");
      setLoadingKey("sensors", true);

      const data = await safeFetchJson(
        `${API_URL}/api/iot/simulate?cenario=${scenario}`
      );

      setSensorSimulation(data);
      setAnalysis(data);

      if (data?.sensor_data) {
        setForm({
          patient_id: data.sensor_data.patient_id,
          heart_rate: data.sensor_data.heart_rate,
          temperature: data.sensor_data.temperature,
          oxygen_level: data.sensor_data.oxygen_level,
          source: data.sensor_data.source || "iot_simulado"
        });
      }
    } catch (error) {
      console.error(error);
      setGlobalError(
        "Erro ao simular sensores. Verifique se o backend está online."
      );
    } finally {
      setLoadingKey("sensors", false);
    }
  }

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]:
        name === "patient_id" || name === "source"
          ? value
          : Number(value)
    }));
  }

  async function analyzeRisk(event) {
    event.preventDefault();

    try {
      setGlobalError("");
      setLoadingKey("analysis", true);

      const data = await safeFetchJson(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
      });

      setAnalysis(data);
    } catch (error) {
      console.error(error);
      setGlobalError("Erro ao analisar risco no backend.");
    } finally {
      setLoadingKey("analysis", false);
    }
  }

  async function restartChatSession(automatic = false) {
    try {
      setLoadingKey("restartChat", true);

      const data = await safeFetchJson(`${API_URL}/api/chatbot/restart`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: chatSessionId
        })
      });

      const newSessionId =
        data.new_session_id ||
        data.session_id ||
        data.welcome?.session_id ||
        "LOCAL_FALLBACK_SESSION";

      setChatSessionId(newSessionId);

      setChatHistory([
        {
          role: "assistant",
          text: automatic
            ? "Backend online. Sessão do assistente reiniciada automaticamente."
            : "Sessão reiniciada. Como posso ajudar na CardioIA?"
        }
      ]);
    } catch (error) {
      console.error(error);

      if (!automatic) {
        setChatHistory((prev) => [
          ...prev,
          {
            role: "assistant",
            text:
              "Não foi possível reiniciar a sessão do chatbot. Verifique o backend ou as credenciais do Watson."
          }
        ]);
      }
    } finally {
      setLoadingKey("restartChat", false);
    }
  }

  async function sendChatMessage(event) {
    event.preventDefault();

    if (!chatMessage.trim()) return;

    const userText = chatMessage.trim();

    setChatHistory((prev) => [
      ...prev,
      { role: "user", text: userText }
    ]);

    setChatMessage("");

    try {
      setLoadingKey("chatbot", true);

      const data = await safeFetchJson(`${API_URL}/api/chatbot/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: userText,
          session_id: chatSessionId
        })
      });

      if (data.session_id) {
        setChatSessionId(data.session_id);
      }

      setChatHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            data.answer ||
            "Resposta recebida pela CardioIA, mas sem texto retornado."
        }
      ]);
    } catch (error) {
      console.error(error);

      setChatHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            "Não consegui acessar o chatbot no backend. Verifique o endpoint /api/chatbot/message."
        }
      ]);
    } finally {
      setLoadingKey("chatbot", false);
    }
  }

  function handleXrayFileChange(event) {
    const file = event.target.files?.[0] || null;

    if (xrayPreview) {
      URL.revokeObjectURL(xrayPreview);
    }

    setXrayFile(file);
    setXrayResult(null);
    setXrayError("");

    if (!file) {
      setXrayPreview(null);
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    setXrayPreview(previewUrl);
  }

  function clearXrayImage() {
    if (xrayPreview) {
      URL.revokeObjectURL(xrayPreview);
    }

    setXrayFile(null);
    setXrayPreview(null);
    setXrayResult(null);
    setXrayError("");
  }

  async function uploadXrayImage(event) {
    event.preventDefault();

    if (!xrayFile) {
      setXrayError("Selecione uma imagem de raio X antes de enviar.");
      return;
    }

    try {
      setXrayError("");
      setLoadingKey("vision", true);

      const formData = new FormData();
      formData.append("file", xrayFile);

      const data = await safeFetchJson(`${API_URL}/api/vision/xray`, {
        method: "POST",
        body: formData
      });

      setXrayResult(data);
    } catch (error) {
      console.error(error);
      setXrayResult(null);
      setXrayError(
        error.message ||
          "Erro ao consultar o modelo de machine learning do raio X."
      );
    } finally {
      setLoadingKey("vision", false);
    }
  }

  function getRiskClass(level) {
    if (level === "alto") return "risk-high";
    if (level === "moderado") return "risk-medium";
    if (level === "baixo_monitorado") return "risk-monitor";
    return "risk-low";
  }

  function getStatusText() {
    if (apiStatus === "online") return "Backend Online";
    if (apiStatus === "offline") return "Backend Offline";
    return "Verificando Backend";
  }

  function renderTab() {
    if (activeTab === "dashboard") {
      return (
        <>
          <section className="grid indicators-grid">
            <IndicatorCard
              icon="❤️"
              title="Batimentos"
              value={`${currentSensorData.heart_rate || 0} bpm`}
              description="Dado simulado pelo potenciômetro no ESP32/Wokwi"
            />

            <IndicatorCard
              icon="🌡️"
              title="Temperatura"
              value={`${currentSensorData.temperature || 0} °C`}
              description="Temperatura corporal simulada pelo DHT22"
            />

            <IndicatorCard
              icon="💧"
              title="Oxigenação"
              value={`${currentSensorData.oxygen_level || 0}%`}
              description="Oxigenação simulada pela umidade do DHT22"
            />

            <IndicatorCard
              icon="📊"
              title="Score de Risco"
              value={analysis?.risk_analysis?.risk_score ?? "--"}
              description={
                analysis?.risk_analysis?.risk_level
                  ? `Nível atual: ${analysis.risk_analysis.risk_level}`
                  : "Aguardando análise"
              }
            />
          </section>

          <section className="grid status-grid">
            <StatusCard
              icon="🖥️"
              title="Backend FastAPI"
              status={apiStatus}
              value={getStatusText()}
              description={API_URL}
            />

            <StatusCard
              icon="🤖"
              title="Chatbot"
              status={chatbotStatus?.configured ? "online" : "verificando"}
              value={
                chatbotStatus?.configured
                  ? "IBM Watson configurado"
                  : "Fallback local"
              }
              description="Assistente conversacional para apoio ao usuário"
            />

            <StatusCard
              icon="📡"
              title="Sensores IoT"
              status="online"
              value="Simulação ativa"
              description="ESP32, DHT22, potenciômetro, chave e OLED"
            />

            <StatusCard
              icon="🧠"
              title="ML Raio X"
              status={
                visionStatus?.model_found && visionStatus?.class_indices_found
                  ? "online"
                  : "offline"
              }
              value={
                visionStatus?.model_found && visionStatus?.class_indices_found
                  ? "Modelo carregável"
                  : "Aguardando treinamento"
              }
              description="Modelo TensorFlow/Keras para classificação de raio X"
            />
          </section>

          <section className="panel">
            <div className="panel-title-row">
              <div>
                <h2>Apresentação real dos sensores simulados</h2>
                <p>
                  A plataforma consulta o backend e gera o mesmo tipo de payload
                  que seria enviado pelo ESP32 no Wokwi.
                </p>
              </div>

              <button type="button" onClick={simulateSensors}>
                {loading.sensors ? "Atualizando..." : "🔄 Simular leitura"}
              </button>
            </div>

            <div className="sensor-toolbar">
              <label>
                Cenário dos sensores
                <select
                  value={scenario}
                  onChange={(event) => setScenario(event.target.value)}
                >
                  {sensorScenarios.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <SensorPayload data={sensorSimulation} />
          </section>
        </>
      );
    }

    if (activeTab === "analise") {
      return (
        <section className="panel two-columns">
          <div>
            <h2>Análise de risco cardíaco</h2>
            <p>
              Ajuste os sinais vitais manualmente ou use uma leitura simulada
              do ESP32.
            </p>

            <form className="risk-form" onSubmit={analyzeRisk}>
              <label>ID do Paciente</label>
              <input
                name="patient_id"
                value={form.patient_id}
                onChange={handleChange}
              />

              <div className="form-row">
                <div>
                  <label>Batimentos cardíacos</label>
                  <input
                    name="heart_rate"
                    type="number"
                    value={form.heart_rate}
                    onChange={handleChange}
                  />
                </div>

                <div>
                  <label>Temperatura</label>
                  <input
                    name="temperature"
                    type="number"
                    step="0.1"
                    value={form.temperature}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="form-row">
                <div>
                  <label>Oxigenação</label>
                  <input
                    name="oxygen_level"
                    type="number"
                    step="0.1"
                    value={form.oxygen_level}
                    onChange={handleChange}
                  />
                </div>

                <div>
                  <label>Origem</label>
                  <input
                    name="source"
                    value={form.source}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <button type="submit">
                {loading.analysis ? "Analisando..." : "⚠️ Analisar risco"}
              </button>
            </form>
          </div>

          <RiskResult analysis={analysis} getRiskClass={getRiskClass} />
        </section>
      );
    }

    if (activeTab === "chatbot") {
      return (
        <section className="panel chatbot-panel">
          <div className="chat-header chat-header-centered">
            <div className="chat-icon">🤖</div>
            <div>
              <h2>Assistente Conversacional CardioIA</h2>
              <p>
                Converse com o IBM Watson Assistant ou fallback local para tirar
                dúvidas sobre sinais vitais, risco cardíaco, sensores e raio X.
              </p>
            </div>
          </div>

          <div className="chat-session-bar chat-session-bar-only-button">
            <div>
              <strong>Conversa com o Assistente CardioIA</strong>
              <p>
                A sessão é gerenciada automaticamente pelo backend e pelo IBM
                Watson.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={() => restartChatSession(false)}
            >
              {loading.restartChat ? "Reiniciando..." : "🔄 Reiniciar conversa"}
            </button>
          </div>

          <div className="chat-box">
            {chatHistory.map((message, index) => (
              <div key={index} className={`chat-message ${message.role}`}>
                {message.text}
              </div>
            ))}

            <div ref={chatEndRef} />
          </div>

          <form className="chat-form" onSubmit={sendChatMessage}>
            <input
              value={chatMessage}
              onChange={(event) => setChatMessage(event.target.value)}
              placeholder="Pergunte sobre risco, batimentos, febre, oxigenação ou raio X..."
            />

            <button type="submit">Enviar</button>
          </form>
        </section>
      );
    }

    if (activeTab === "raiox") {
      return (
        <section className="panel two-columns">
          <div>
            <div className="section-title-with-icon">
              <span>🩻</span>
              <div>
                <h2>Consulta de raio X do tórax</h2>
                <p>
                  O usuário pode enviar uma imagem de raio X para consulta no
                  modelo de machine learning configurado no backend.
                </p>
              </div>
            </div>

            <form className="risk-form" onSubmit={uploadXrayImage}>
              <label>Imagem de raio X</label>

              <input
                type="file"
                accept=".jpg,.jpeg,.png,.bmp,.webp"
                onChange={handleXrayFileChange}
              />

              {xrayPreview && (
                <div className="xray-preview-card">
                  <div className="xray-preview-header">
                    <div>
                      <strong>Imagem selecionada</strong>
                      <span>{xrayFile?.name}</span>
                    </div>

                    <button
                      type="button"
                      className="secondary-button xray-clear-button"
                      onClick={clearXrayImage}
                    >
                      Remover imagem
                    </button>
                  </div>

                  <div className="xray-preview-image-box">
                    <img
                      src={xrayPreview}
                      alt="Prévia do raio X selecionado"
                      className="xray-preview-image"
                    />
                  </div>

                  <p>
                    Confira se a imagem está correta antes de enviar para análise
                    do modelo de machine learning.
                  </p>
                </div>
              )}

              <button type="submit">
                {loading.vision ? "Consultando modelo..." : "📤 Enviar imagem"}
              </button>
            </form>

            {xrayError && (
              <div className="error-box">
                <strong>Retorno da visão computacional:</strong>
                <p>{xrayError}</p>
              </div>
            )}

            <div className="ml-status-box">
              <h3>Status do modelo de machine learning</h3>

              <VisionStatusLine
                label="Modelo TensorFlow/Keras"
                active={Boolean(visionStatus?.model_found)}
                activeText="Modelo encontrado"
                inactiveText="Modelo ainda não encontrado"
              />

              <VisionStatusLine
                label="Mapeamento de classes"
                active={Boolean(visionStatus?.class_indices_found)}
                activeText="Classes encontradas"
                inactiveText="Arquivo de classes não encontrado"
              />

              <VisionStatusLine
                label="Endpoint de visão"
                active={apiStatus === "online"}
                activeText="Backend disponível"
                inactiveText="Backend indisponível"
              />

              <div className="ml-description">
                <strong>Modo:</strong>{" "}
                {visionStatus?.mode || "xray_chest_classification"}
              </div>

              <div className="ml-description">
                <strong>Descrição:</strong>{" "}
                {visionStatus?.description ||
                  "Módulo preparado para receber imagem de raio X de tórax e retornar classificação por machine learning."}
              </div>
            </div>
          </div>

          <XrayResult result={xrayResult} />
        </section>
      );
    }

    if (activeTab === "arquitetura") {
      return (
        <>
          <section className="panel architecture-panel">
            <h2>Arquitetura integrada do MVP</h2>

            <p>
              A CardioIA foi organizada em camadas para demonstrar uma solução
              completa de saúde digital. A proposta integra aquisição de dados,
              processamento em backend, análise de risco, chatbot, visão
              computacional, aplicação Web e aplicativo Mobile.
            </p>

            <p>
              Na camada de IoT, o ESP32 executa um firmware em MicroPython e
              simula sinais vitais usando DHT22, potenciômetro, chave de estado
              e display OLED. Como o Wokwi possui limitações para comunicação
              direta com um backend local, a API FastAPI replica o mesmo payload
              do dispositivo por meio de endpoints de simulação.
            </p>

            <p>
              No backend, os dados são normalizados, analisados por regras
              explicáveis de risco cardíaco e enviados para serviços auxiliares,
              como recomendações preventivas, chatbot IBM Watson, consulta às
              bases das fases anteriores e visão computacional com TensorFlow.
            </p>

            <div className="architecture-flow">
              <span>ESP32 + MicroPython</span>
              <strong>→</strong>
              <span>Sensores simulados</span>
              <strong>→</strong>
              <span>FastAPI</span>
              <strong>→</strong>
              <span>Análise de Risco</span>
              <strong>→</strong>
              <span>Recomendações</span>
              <strong>→</strong>
              <span>Watson Assistant</span>
              <strong>→</strong>
              <span>TensorFlow Raio X</span>
              <strong>→</strong>
              <span>React Web</span>
              <strong>→</strong>
              <span>Expo Mobile</span>
            </div>
          </section>

          <section className="grid architecture-cards">
            <InfoCard
              icon="📡"
              title="Camada IoT"
              text="Responsável pela origem dos sinais vitais. No MVP, os valores são simulados para representar temperatura, oxigenação e batimentos cardíacos."
            />

            <InfoCard
              icon="🖥️"
              title="Backend FastAPI"
              text="Centraliza as rotas da aplicação, recebe os dados dos sensores, executa análise de risco, conecta chatbot, visão computacional e bases integradas."
            />

            <InfoCard
              icon="🧠"
              title="Machine Learning"
              text="Módulo de visão computacional preparado para carregar modelo Keras, processar imagem de raio X e retornar classe prevista com confiança."
            />

            <InfoCard
              icon="🌐"
              title="Integração Web/Mobile"
              text="Permite que usuários acessem os recursos da CardioIA por dashboard Web e futuramente por aplicativo Mobile conectado à mesma API."
            />
          </section>
        </>
      );
    }

    return (
      <section className="panel project-panel">
        <h2>Sobre o projeto CardioIA</h2>

        <p>
          A CardioIA é uma plataforma acadêmica desenvolvida para demonstrar
          como diferentes tecnologias de inteligência artificial, IoT e
          desenvolvimento de software podem ser integradas em uma solução de
          apoio à saúde.
        </p>

        <p>
          O projeto não tem a finalidade de substituir médicos, laudos ou
          diagnóstico profissional. Seu objetivo é atuar como uma ferramenta de
          apoio à triagem, educação, monitoramento preventivo e análise
          preliminar de dados clínicos simulados.
        </p>

        <p>
          A solução combina sinais vitais, análise de risco cardíaco, consulta
          conversacional por chatbot, processamento de imagem de raio X e
          integração de bases das fases anteriores.
        </p>

        <div className="grid project-grid">
          <InfoCard
            icon="🩺"
            title="Objetivo"
            text="Apoiar a triagem e o acompanhamento preventivo por meio de sinais vitais, análise de risco e inteligência artificial aplicada."
          />

          <InfoCard
            icon="🛡️"
            title="Uso responsável"
            text="O sistema apresenta recomendações de apoio e reforça que toda interpretação clínica deve ser validada por profissional de saúde."
          />

          <InfoCard
            icon="🗃️"
            title="Dados integrados"
            text="A plataforma consulta dados clínicos, mapas de conhecimento, intents do chatbot, sensores simulados e imagens enviadas pelo usuário."
          />

          <InfoCard
            icon="📱"
            title="Entrega final"
            text="O MVP integra backend FastAPI, frontend React, aplicativo Mobile, chatbot, IoT simulado, visão computacional e análise de risco."
          />
        </div>

        <div className="project-summary">
          <h3>Status de integração</h3>

          <p>
            Plataforma:{" "}
            <strong>{integrationStatus?.platform || "CardioIA"}</strong>
          </p>

          <p>
            Fase: <strong>{integrationStatus?.phase || "Fase 7"}</strong>
          </p>

          <p>
            Status:{" "}
            <strong>{integrationStatus?.status || "aguardando backend"}</strong>
          </p>

          <p>
            Backend: <strong>{getStatusText()}</strong>
          </p>

          <p>
            Chatbot:{" "}
            <strong>
              {chatbotStatus?.configured
                ? "IBM Watson configurado"
                : "Fallback local disponível"}
            </strong>
          </p>

          <p>
            Visão computacional:{" "}
            <strong>
              {visionStatus?.model_found && visionStatus?.class_indices_found
                ? "Modelo de raio X disponível"
                : "Aguardando treinamento do modelo"}
            </strong>
          </p>
        </div>
      </section>
    );
  }

  if (!isLogged) {
    return (
      <main className="login-page">
        <section className="login-card">
          <div className="brand-icon">❤️</div>

          <h1>CardioIA</h1>
          <p>
            Plataforma inteligente para monitoramento cardíaco, análise de risco,
            chatbot e consulta de raio X por machine learning.
          </p>

          {globalError && (
            <div className="login-error">
              ⚠️ {globalError}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <label>Usuário</label>
            <input
              type="text"
              value={loginName}
              onChange={(event) => setLoginName(event.target.value)}
              placeholder="Digite seu nome"
            />

            <label>Senha</label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Senha demonstrativa"
            />

            <button type="submit">
              Entrar no Dashboard
            </button>
          </form>

          <span className="demo-info">
            Acesso demonstrativo do MVP. Sugestão de senha: cardioia.
          </span>
        </section>
      </main>
    );
  }

  return (
    <main className="app-page">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">❤️</div>
          <div>
            <h2>CardioIA</h2>
            <span>Fase 7 MVP</span>
          </div>
        </div>

        <nav>
          <button
            type="button"
            className={activeTab === "dashboard" ? "active" : ""}
            onClick={() => setActiveTab("dashboard")}
          >
            📊 Dashboard
          </button>

          <button
            type="button"
            className={activeTab === "analise" ? "active" : ""}
            onClick={() => setActiveTab("analise")}
          >
            ❤️ Análise de Risco
          </button>

          <button
            type="button"
            className={activeTab === "chatbot" ? "active" : ""}
            onClick={() => setActiveTab("chatbot")}
          >
            🤖 Chatbot
          </button>

          <button
            type="button"
            className={activeTab === "raiox" ? "active" : ""}
            onClick={() => setActiveTab("raiox")}
          >
            🩻 Raio X
          </button>

          <button
            type="button"
            className={activeTab === "arquitetura" ? "active" : ""}
            onClick={() => setActiveTab("arquitetura")}
          >
            🧩 Arquitetura
          </button>

          <button
            type="button"
            className={activeTab === "projeto" ? "active" : ""}
            onClick={() => setActiveTab("projeto")}
          >
            📄 Projeto
          </button>
        </nav>

        <div className={`api-status ${apiStatus}`}>
          Backend: {apiStatus}
        </div>

        <button type="button" className="refresh-button" onClick={loadPlatformStatus}>
          {loading.status ? "Verificando..." : "Atualizar status"}
        </button>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <h1>Dashboard CardioIA</h1>
            <p>
              Bem-vindo, {loginName}. Monitoramento inteligente de sinais vitais,
              risco cardíaco e raio X.
            </p>
          </div>

          <div className="topbar-actions">
            <div className="topbar-badge">
              👤 {loginName}
            </div>

            <button type="button" className="logout-button" onClick={logout}>
              Sair
            </button>
          </div>
        </header>

        {globalError && (
          <section className="error-box">
            <strong>Atenção:</strong>
            <p>{globalError}</p>
          </section>
        )}

        {renderTab()}
      </section>
    </main>
  );
}

function IndicatorCard({ icon, title, value, description }) {
  return (
    <article className="indicator-card">
      <div className="indicator-icon">{icon}</div>
      <span>{title}</span>
      <strong>{value}</strong>
      <p>{description}</p>
    </article>
  );
}

function StatusCard({ icon, title, status, value, description }) {
  const online = status === "online";
  const offline = status === "offline";

  return (
    <article className="status-card">
      <div className="status-card-header">
        <div className="indicator-icon">{icon}</div>
        <div
          className={
            online
              ? "status-dot-card ok"
              : offline
              ? "status-dot-card bad"
              : "status-dot-card warn"
          }
        />
      </div>

      <span>{title}</span>
      <strong>{value}</strong>
      <p>{description}</p>
    </article>
  );
}

function getSignalClass(status, score = 0) {
  if (["critico", "grave", "febre_alta", "alto"].includes(status)) {
    return "sensor-danger";
  }

  if (["elevado", "baixo", "febre", "moderada", "leve", "moderado"].includes(status)) {
    return "sensor-warning";
  }

  if (score >= 70) return "sensor-danger";
  if (score >= 40) return "sensor-warning";

  return "sensor-success";
}

function SensorPayload({ data }) {
  if (!data) {
    return (
      <div className="sensor-empty">
        <h3>Aguardando leitura simulada</h3>
        <p>
          Clique em “Simular leitura” para consultar o backend e gerar uma
          amostra dos sensores.
        </p>
      </div>
    );
  }

  const sensor = data.sensor_data;
  const risk = data.risk_analysis;
  const signals = risk?.signals || {};

  const bpm = signals.heart_rate || {};
  const temperature = signals.temperature || {};
  const oxygen = signals.oxygen_level || {};

  return (
    <div className="sensor-details-enhanced">
      <SensorSignalCard
        label="Batimentos"
        value={`${sensor?.heart_rate} bpm`}
        status={bpm.status || "normal"}
        reason={bpm.reason || "Batimentos dentro da faixa esperada."}
        className={getSignalClass(bpm.status, bpm.score)}
      />

      <SensorSignalCard
        label="Temperatura"
        value={`${sensor?.temperature} °C`}
        status={temperature.status || "normal"}
        reason={temperature.reason || "Temperatura dentro da faixa esperada."}
        className={getSignalClass(temperature.status, temperature.score)}
      />

      <SensorSignalCard
        label="Oxigenação"
        value={`${sensor?.oxygen_level}%`}
        status={oxygen.status || "normal"}
        reason={oxygen.reason || "Oxigenação dentro da faixa esperada."}
        className={getSignalClass(oxygen.status, oxygen.score)}
      />

      <SensorSignalCard
        label="Score"
        value={risk?.risk_score ?? "--"}
        status={risk?.risk_level || "baixo"}
        reason={risk?.interpretation || "Aguardando interpretação."}
        className={getSignalClass(risk?.risk_level, risk?.risk_score)}
      />

      <SensorSignalCard
        label="Status Geral"
        value={risk?.general_status || "--"}
        status={risk?.alert ? "alerta" : "monitoramento"}
        reason={`Origem dos dados: ${sensor?.source || "simulado"}`}
        className={risk?.alert ? "sensor-danger" : "sensor-success"}
      />

      <SensorSignalCard
        label="Paciente"
        value={sensor?.patient_id || "--"}
        status="identificação"
        reason="Identificador do paciente monitorado pela plataforma."
        className="sensor-neutral"
      />
    </div>
  );
}

function SensorSignalCard({ label, value, status, reason, className }) {
  return (
    <article className={`sensor-signal-card ${className}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{status}</small>
      <p>{reason}</p>
    </article>
  );
}

function RiskResult({ analysis, getRiskClass }) {
  if (!analysis) {
    return (
      <div className="risk-result empty">
        <h3>Aguardando análise</h3>
        <p>Preencha os sinais vitais e execute a análise de risco.</p>
      </div>
    );
  }

  const risk = analysis.risk_analysis;
  const recommendation = analysis.recommendation;

  return (
    <div className={`risk-result ${getRiskClass(risk?.risk_level)}`}>
      <span className="risk-label">Nível de risco</span>
      <h3>{String(risk?.risk_level || "indefinido").toUpperCase()}</h3>

      <div className="score">
        <span>Score</span>
        <strong>{risk?.risk_score}</strong>
      </div>

      <div className="score">
        <span>Status geral</span>
        <strong>{risk?.general_status || "--"}</strong>
      </div>

      <div className="recommendation">
        <strong>Prioridade: {recommendation?.priority}</strong>
        <p>{recommendation?.message}</p>
      </div>

      <div className="reasons">
        <strong>Motivos detectados:</strong>

        {risk?.reasons?.length > 0 ? (
          <ul>
            {risk.reasons.map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
        ) : (
          <p>Nenhum fator crítico detectado.</p>
        )}
      </div>
    </div>
  );
}

function VisionStatusLine({
  label,
  active,
  activeText,
  inactiveText
}) {
  return (
    <div className={`vision-status-line ${active ? "online" : "offline"}`}>
      <div>{active ? "✅" : "❌"}</div>

      <section>
        <strong>{label}</strong>
        <p>{active ? activeText : inactiveText}</p>
      </section>
    </div>
  );
}

function XrayResult({ result }) {
  if (!result) {
    return (
      <div className="risk-result empty">
        <h3>Aguardando imagem</h3>
        <p>
          Envie uma imagem de raio X de tórax para consultar o modelo de machine
          learning.
        </p>
      </div>
    );
  }

  const analysis = result.analysis;

  return (
    <div className="xray-result">
      <span className="risk-label">Resultado do raio X</span>

      <h3>{analysis?.predicted_class || "Classe indefinida"}</h3>

      <div className="score">
        <span>Confiança</span>
        <strong>{analysis?.confidence_percentage}%</strong>
      </div>

      <div className="recommendation">
        <strong>Interpretação</strong>
        <p>{analysis?.interpretation?.message}</p>
        <p>{analysis?.interpretation?.recommendation}</p>
      </div>

      <div className="reasons">
        <strong>Ranking de classes:</strong>

        <ul>
          {analysis?.ranking?.map((item, index) => (
            <li key={index}>
              {item.class}: {item.percentage}%
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function InfoCard({ icon, title, text }) {
  return (
    <article className="info-card">
      <div className="indicator-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

export default App;