//====================================================================
// ATIVIDADE FIAP - CardioIA_Fase3  |  PARTE 2 (MQTT + Cloud)
//====================================================================
// Autor.....: Diego Nunes Veiga
// RM........: 560658
// Turma.....: Graduação - 2TIAOR
// Data......: 22/10/2025
//====================================================================

//----------- BIBLIOTECAS --------------------------------------------
#include <DHT.h>
#include <math.h>
#include <FS.h>
#include <SPIFFS.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

//--------------------------------------------------------------------
//----------- DESIGNAÇÃO DOS IO's E PARÂMETROS -----------------------


// S1 - Sensor de temperatura DHT22
#define pinoDHT 23
#define modelo DHT22
DHT dht(pinoDHT, modelo);

// S2 - Potenciômetro (Oximetro)
#define oxim 34

// B1 - Chave simulando o Wifi
#define btWifi 22

// Arquivo e política do buffer offline (SPIFFS)
const char* FILE_BUFFER = "/buffer.txt";
const size_t MAX_BUFFER_BYTES = 300 * 1024;

//--------------------------------------------------------------------
//----------- SUBALGORITMOS ------------------------------------------

// Leitura do wifi (nível direto da chave)
bool LeituraWifi(int input){
  return digitalRead(input);
}

// Realiza leitura do sensor DHT
float LeituraTemperatura() {
  return dht.readTemperature();
}

// Realiza a leitura analógica do oximetro
float LeituraOximetro(int input) {
  float leitura = analogRead(input);      // 0..4095
  float porcentagem = (leitura / 4095.0) * 100.0;
  return porcentagem;
}

// Analisa status de temperatura
const char* AnaliseTemperatura(float temp) {
  if (temp <= 36.0) return "baixa";
  else if (temp <= 37.4) return "normal";
  else if (temp <= 38.5) return "febre";
  else return "febre alta";
}

// Analisa status de oxigênio
const char* AnaliseOxigenio(float oxig) {
  if (oxig >= 95.0) return "normal";
  else if (oxig >= 93.0) return "leve";
  else if (oxig >= 90.0) return "moderada";
  else return "grave";
}

// Apresentação da temperatura e status
void StatusTemperatura(float temp, const char* status) {
  Serial.println("==== TEMPERATURA DO PACIENTE ====");
  Serial.print("Temperatura: ");
  Serial.print(temp);
  Serial.println("°C");
  Serial.print("Status: ");
  Serial.print(status);
}

// Apresentação da oxigenação e status
void StatusOxigenio(float oxi, const char* status) {
  Serial.println("==== OXIGENAÇÃO DO PACIENTE ====");
  Serial.print("Oxigenação: ");
  Serial.print(oxi);
  Serial.println("%");
  Serial.print("Status: ");
  Serial.print(status);
}

// Empurra conteúdo para cima -> "limpa tela"
void LimpaSerial() {
  for (int i = 0; i < 20; i++) Serial.println();
}


// Inicia o processo do SPIFFS
bool FS_Init() {
  if (!SPIFFS.begin(true)) {
    Serial.println("ERRO: SPIFFS nao montado.");
    return false;
  }
  return true;
}

// Abre o arquivo do SPIFFS
size_t FS_FileSize(const char* path) {
  File f = SPIFFS.open(path, "r");
  if (!f) return 0;
  size_t s = f.size();
  f.close();
  return s;
}

//Tenta realizar a abertura do arquivo
bool FS_AppendLine(const char* path, const String& line) {
  File f = SPIFFS.open(path, FILE_APPEND);
  if (!f) f = SPIFFS.open(path, FILE_WRITE);
  if (!f) {
    Serial.println("ERRO: nao foi possivel abrir o buffer para escrita.");
    return false;
  }
  f.println(line);
  f.close();
  return true;
}

// Estratégia simples de limite: se exceder, zera o arquivo
void FS_EnforceLimit(const char* path, size_t maxBytes) {
  size_t s = FS_FileSize(path);
  if (s > maxBytes) {
    Serial.printf("Buffer excedeu limite (%u > %u). Limpando arquivo...\n",
                  (unsigned)s, (unsigned)maxBytes);
    SPIFFS.remove(path);
  }
}

// Lê o buffer e envia para a nuvem
void SyncBufferParaNuvem(const char* path) {
  File f = SPIFFS.open(path, "r");
  if (!f) {
    Serial.println("Sem dados pendentes para sincronizar.");
    return;
  }

  Serial.println("=== SINCRONIZACAO: ENVIANDO DADOS ARMAZENADOS ===");

  while (f.available()) {
    String linha = f.readStringUntil('\n');
    if (linha.length() > 0) {
      Serial.println(linha);
    }
  }
  f.close();

  SPIFFS.remove(path);
  Serial.println("=== SINCRONIZACAO CONCLUIDA. BUFFER LIMPO. ===");
}

// Monta registro JSON por linha
String MontaRegistroJSON(float temp, const char* stTemp, float oxi, const char* stOxi) {
  if (isnan(temp)) temp = -99.9;
  if (isnan(oxi))  oxi  = -1.0;

  unsigned long ts = millis();
  String json = "{";
  json += "\"ts\":" + String(ts);
  json += ",\"temp\":" + String(temp, 1);
  json += ",\"temp_status\":\"" + String(stTemp) + "\"";
  json += ",\"oxi\":" + String(oxi, 1);
  json += ",\"oxi_status\":\"" + String(stOxi) + "\"";
  json += "}";
  return json;
}


// Estabelece ou encerra a conexão Wi-Fi conforme o estado da chave física
void wifiConnectIfNeeded(bool shouldConnect) {
  if (!shouldConnect) {           // OFFLINE por chave física
    if (WiFi.status() == WL_CONNECTED) WiFi.disconnect(true, true);
    return;
  }
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("Conectando ao Wi-Fi: "); Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - t0) < 15000) {
    Serial.print("."); delay(300);
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi OK. IP: "); Serial.println(WiFi.localIP());
  } else {
    Serial.println("Falha no Wi-Fi (timeout). Mantendo modo OFFLINE.");
  }
}

// Garante que o cliente MQTT esteja conectado ao broker HiveMQ Cloud
bool mqttEnsureConnected() {
  if (mqtt.connected()) return true;
  if (WiFi.status() != WL_CONNECTED) return false;

  net.setInsecure(); // TLS sem verificação de certificado (ambiente de teste)

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  String clientId = String("ESP32-CardioIA-") + String(560658);

  Serial.print("Conectando ao MQTT/TLS @ ");
  Serial.print(MQTT_HOST); Serial.print(":"); Serial.println(MQTT_PORT);

  if (mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASS)) {
    Serial.println("MQTT conectado.");
    return true;
  } else {
    Serial.print("MQTT falhou, rc="); Serial.println(mqtt.state());
    return false;
  }
}

// Publica um pacote JSON no broker MQTT
bool mqttPublish(const String& payload) {
  if (!mqttEnsureConnected()) return false;
  bool ok = mqtt.publish(MQTT_TOPIC, payload.c_str(), true);
  if (!ok) Serial.println("Falha ao publicar MQTT.");
  return ok;
}

// Lê o buffer SPIFFS e publica cada linha pendente no MQTT
void SyncBufferParaMQTT(const char* path) {
  File f = SPIFFS.open(path, "r");
  if (!f) { Serial.println("Sem dados pendentes para sincronizar."); return; }

  Serial.println("=== SINCRONIZACAO MQTT: enviando buffer offline ===");
  bool allOk = true;
  while (f.available()) {
    String linha = f.readStringUntil('\n');
    linha.trim();
    if (linha.length() == 0) continue;
    if (!mqttPublish(linha)) { allOk = false; break; }
  }
  f.close();

  if (allOk) {
    SPIFFS.remove(path);
    Serial.println("=== SINCRONIZACAO OK. Buffer limpo. ===");
  } else {
    Serial.println("=== SINCRONIZACAO PARCIAL. Manter buffer para nova tentativa. ===");
  }
}


//--------------------------------------------------------------------
// STARTUP INICIAL
//--------------------------------------------------------------------
void setup() {

  // IOs
  pinMode(btWifi, INPUT);

  // Serial
  Serial.begin(115200);
  delay(100);

  // Sensores
  dht.begin();

  // SPIFFS
  if (FS_Init()) {
    Serial.println("SPIFFS montado com sucesso.");
  } else {
    Serial.println("Falha ao montar SPIFFS.");
  }

  Serial.println("Chave de conectividade: OFF (LOW) = OFFLINE | ON (HIGH) = ONLINE");
}


//--------------------------------------------------------------------
// LOOP
//--------------------------------------------------------------------
void loop(){

  // Leitura do estado da chave física
  bool conectado = LeituraWifi(btWifi);

  // Gerenciamento de conexão Wi-Fi e MQTT
  wifiConnectIfNeeded(conectado);

  // Se acabou de ficar ONLINE, envia o buffer pendente
  if (!conectadoAnterior && conectado) {
    if (mqttEnsureConnected()) {
      SyncBufferParaMQTT(FILE_BUFFER);
    }
  }
  conectadoAnterior = conectado;

  // Coleta dos sensores
  LimpaSerial();
  float temperatura = LeituraTemperatura();
  float oxigenio    = LeituraOximetro(oxim);

  StatusTemperatura(temperatura, AnaliseTemperatura(temperatura));
  Serial.println(); Serial.println();
  StatusOxigenio(oxigenio, AnaliseOxigenio(oxigenio));
  Serial.println();

  // Exibe estado atual
  Serial.print("Conexao: ");
  bool online = (WiFi.status() == WL_CONNECTED) && mqttEnsureConnected();
  Serial.println( online ? "ONLINE (Wi-Fi + MQTT)" : (conectado ? "Wi-Fi tentando..." : "OFFLINE") );

  // Monta registro JSON e decide destino
  String linha = MontaRegistroJSON(
    temperatura, AnaliseTemperatura(temperatura),
    oxigenio,    AnaliseOxigenio(oxigenio)
  );

  // Se onlue realiza a publicação do MQTT
  if (online) {
    if (mqttPublish(linha)) {
      Serial.println("-> MQTT publish OK:");
      Serial.println(linha);
    } else {
      Serial.println("-> MQTT publish FAIL. Gravando no buffer.");
      FS_AppendLine(FILE_BUFFER, linha);
      FS_EnforceLimit(FILE_BUFFER, MAX_BUFFER_BYTES);
    }
    mqtt.loop();
    SyncBufferParaMQTT(FILE_BUFFER);
  } else {
    FS_AppendLine(FILE_BUFFER, linha);
    FS_EnforceLimit(FILE_BUFFER, MAX_BUFFER_BYTES);
    Serial.println("OFFLINE: dado gravado no buffer.");
  }

  delay(1000);
}
