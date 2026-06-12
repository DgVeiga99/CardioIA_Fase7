//====================================================================
// ATIVIDADE FIAP - CardioIA_Fase3
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
// PROGRAMA PRINCIPAL
//--------------------------------------------------------------------

// Verifica conexão se existe uma conexão anterior
bool conectadoAnterior = false;

void loop() {
  //Verifica status do wifi
  bool conectado = LeituraWifi(btWifi);

  // Sincroniza o buffer quando o equipamento acaba de ficar online
  if (!conectadoAnterior && conectado) {
    SyncBufferParaNuvem(FILE_BUFFER);
  }
  conectadoAnterior = conectado;

  // Limpeza visual do terminal
  LimpaSerial();

  // Leitura dos medidores
  float temperatura = LeituraTemperatura();
  float oxigenio    = LeituraOximetro(oxim);

  // Apresenta o status
  StatusTemperatura(temperatura, AnaliseTemperatura(temperatura));
  Serial.println();
  Serial.println();
  StatusOxigenio(oxigenio, AnaliseOxigenio(oxigenio));
  Serial.println();
  Serial.println();
  Serial.print("Conexao: ");
  Serial.println(conectado ? "ONLINE" : "OFFLINE");

  // Monta JSON e registra no buffer
  String linha = MontaRegistroJSON(
    temperatura,
    AnaliseTemperatura(temperatura),
    oxigenio,
    AnaliseOxigenio(oxigenio)
  );
  FS_AppendLine(FILE_BUFFER, linha);
  FS_EnforceLimit(FILE_BUFFER, MAX_BUFFER_BYTES);

  // Envio em tempo real (simulado) quando ONLINE
  if (conectado) {
    Serial.println("-> Envio em tempo real (simulado):");
    Serial.println(linha);
  } else {
    Serial.println("OFFLINE: dado gravado no buffer.");
  }

  delay(1000);
}

