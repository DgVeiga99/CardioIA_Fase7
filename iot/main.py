# ============================================================
# CardioIA - Fase 7
# IoT com ESP32 + MicroPython + OLED I2C
#
# Conversão da lógica C/C++ da Fase 3 para MicroPython,
# com evolução para feedback visual em display OLED SSD1306.
#
# Componentes:
# - ESP32 DevKit
# - DHT22 simulando temperatura corporal e oxigenação
# - Potenciômetro simulando batimentos cardíacos
# - Chave slide simulando conexão online/offline
# - Display OLED SSD1306 I2C 128x64
#
# Pinos:
# - DHT22 DATA          -> GPIO 23
# - Potenciômetro SIG   -> GPIO 34
# - Chave conexão       -> GPIO 19
# - OLED SDA            -> GPIO 21
# - OLED SCL            -> GPIO 22
# ============================================================

from machine import Pin, ADC, I2C
from time import sleep, ticks_ms
import dht
import json
import os
import ssd1306

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

PATIENT_ID = "PACIENTE_IOT_001"

# Quando o backend estiver publicado, substitua None pela URL real:
# Exemplo:
# API_URL = "https://cardioia-backend.onrender.com/api/analyze"
API_URL = None

FILE_BUFFER = "buffer.txt"
MAX_BUFFER_BYTES = 300 * 1024


# ============================================================
# CONFIGURAÇÃO DOS PINOS
# ============================================================

# S1 - Sensor DHT22
# Temperatura do DHT22 = temperatura corporal simulada
# Umidade do DHT22     = oxigenação simulada
PINO_DHT = 23
sensor_dht = dht.DHT22(Pin(PINO_DHT))

# S2 - Potenciômetro simulando batimentos cardíacos
PINO_BATIMENTO = 34
pot_batimento = ADC(Pin(PINO_BATIMENTO))
pot_batimento.atten(ADC.ATTN_11DB)
pot_batimento.width(ADC.WIDTH_12BIT)

# B1 - Chave slide simulando conexão online/offline
# GPIO 22 foi liberado para o SCL do I2C.
PINO_WIFI = 19
chave_wifi = Pin(PINO_WIFI, Pin.IN, Pin.PULL_DOWN)

# OLED SSD1306 I2C
PINO_I2C_SDA = 21
PINO_I2C_SCL = 22
# Endereço padrão do OLED no Wokwi: 0x3C
OLED_ADDR = 0x3C



# Configurações de comunicação I2C
i2c = I2C( 0, scl=Pin(PINO_I2C_SCL), sda=Pin(PINO_I2C_SDA), freq=400000)
oled = ssd1306.SSD1306_I2C(128,64,i2c,addr=OLED_ADDR)




# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

# Conversor de escala 
def mapear(valor, in_min, in_max, out_min, out_max):
    return ((valor - in_min) * (out_max - out_min)/(in_max - in_min) + out_min)

# ============================================================
# FUNÇÕES DE LEITURA
# ============================================================


# Verifica a chave slide que simula a conectividade wifi
def leitura_conexao():
    return chave_wifi.value() == 1


# Leitura o DHT22 e retorna temperatura(°C) e umidade(%).
def leitura_dht22():
    try:
        sensor_dht.measure()

        temperatura = round(sensor_dht.temperature(), 1)
        umidade = round(sensor_dht.humidity(), 1)

        return temperatura, umidade

    except Exception as erro:
        print("Erro na leitura do DHT22:", erro)
        return -99.9, 0.0


# Realiza leitura do potênciometro (BPM Simulado)
def leitura_batimento():

    valor_adc = pot_batimento.read()
    bpm = mapear(valor_adc, 0, 4095, 45, 160)

    return int(round(bpm, 0))


# ============================================================
# FUNÇÕES DE ANÁLISE LOCAL
# ============================================================


# Classifica a temperatura corporal
def classificar_temperatura(temp):

    if temp <= 36.0: return "baixa"
    if temp <= 37.4: return "normal"
    if temp <= 38.5: return "febre"
    return "febre alta"


# Classifica a oxigenação do paciente
def classificar_oxigenacao(oxi):

    if oxi >= 95.0: return "normal"
    if oxi >= 93.0: return "leve"
    if oxi >= 90.0: return "moderada"
    return "grave"


# Classifica os batimentos do paciente
def classificar_batimento(bpm):

    if bpm < 50:    return "baixo"
    if bpm <= 100:  return "normal"
    if bpm <= 120:  return "elevado"
    return "critico"


# Gera o status geral do paciente
def classificar_status_geral(temp_status, oxi_status, bpm_status):

    if temp_status == "febre alta" or oxi_status == "grave" or bpm_status == "critico":
        return "RISCO_ALTO"

    if temp_status == "febre" or oxi_status in ["leve", "moderada"] or bpm_status in ["baixo", "elevado"]:
        return "ATENCAO"

    return "NORMAL"


# Status curto para apresentação no OLED
def status_curto(status):

    if status == "GRAVE":   return "GRAVE"
    if status == "ATENCAO": return "ATENCAO"
    return "NORMAL"


# ============================================================
# BUFFER OFFLINE
# ============================================================


# Tamanho do arquivo de buffer
def tamanho_arquivo(path):
    try:
        return os.stat(path)[6]
    except OSError:
        return 0


# Grava uma linha JSON no buffer local.
def gravar_buffer(path, linha):
    try:
        with open(path, "a") as arquivo:
            arquivo.write(linha + "\n")
        return True

    except Exception as erro:
        print("ERRO: falha ao gravar buffer:", erro)
        return False


# Limita o tamanho do buffer local.
def limitar_buffer(path, max_bytes):

    tamanho = tamanho_arquivo(path)

    if tamanho > max_bytes:
        print("Buffer excedeu o limite configurado. Limpando arquivo...")

        try:
            os.remove(path)
        except OSError:
            pass

# Simula o envio dos registros offline quando a conexão volta.
def sincronizar_buffer(path):
    try:
        with open(path, "r") as arquivo:
            linhas = arquivo.readlines()

    except OSError:
        print("Sem dados pendentes para sincronizar.")
        return

    print("=== SINCRONIZACAO CLOUD/API: DADOS PENDENTES ===")

    for linha in linhas:
        linha = linha.strip()

        if linha:
            print("SYNC:", linha)

    try:
        os.remove(path)
    except OSError:
        pass

    print("=== BUFFER SINCRONIZADO E LIMPO ===")


# ============================================================
# PAYLOADS
# ============================================================

# Processamento dos dados e monta exibição local no OLED
def montar_payload():

    temperatura, oxigenacao = leitura_dht22()
    bpm = leitura_batimento()

    temp_status = classificar_temperatura(temperatura)
    oxi_status = classificar_oxigenacao(oxigenacao)
    bpm_status = classificar_batimento(bpm)

    status_geral = classificar_status_geral(
        temp_status,
        oxi_status,
        bpm_status
    )

    payload = {
        "ts": ticks_ms(),
        "patient_id": PATIENT_ID,
        "heart_rate": bpm,
        "heart_rate_status": bpm_status,
        "temperature": temperatura,
        "oxygen_level": oxigenacao,
        "temperature_status": temp_status,
        "oxygen_status": oxi_status,
        "status": status_geral,
        "source": "iot_micropython_oled"
    }

    return payload


# Reduz o payload ao formato esperado pelo backend FastAPI.
#    Endpoint:
#    POST /api/analyze
def payload_para_backend(payload):

    return {
        "patient_id": payload["patient_id"],
        "heart_rate": payload["heart_rate"],
        "temperature": payload["temperature"],
        "oxygen_level": payload["oxygen_level"],
        "source": payload["source"]
    }


# ============================================================
# ENVIO CLOUD/API
# ============================================================

# Envio preparado para integração com API pública.
def enviar_para_cloud(payload_backend):

    if API_URL is None:
        print("-> Envio Cloud/API simulado:")
        print(json.dumps(payload_backend))
        return

    try:
        import urequests

        resposta = urequests.post(
            API_URL,
            data=json.dumps(payload_backend),
            headers={"Content-Type": "application/json"}
        )

        print("HTTP Status:", resposta.status_code)
        print("Resposta API:", resposta.text)

        resposta.close()

    except Exception as erro:
        print("ERRO no envio para API:", erro)
        print("Gravando payload no buffer offline.")
        gravar_buffer(FILE_BUFFER, json.dumps(payload_backend))


# ============================================================
# EXIBIÇÃO SERIAL
# ============================================================

# Limpeza do terminal serial
def limpar_terminal():
    for _ in range(8):
        print()


# Exibe os dados no Serial Monitor
def exibir_dados_serial(payload, conectado):

    print("==== CARDIOIA IOT - MICROPYTHON + OLED ====")
    print("Paciente:", payload["patient_id"])
    print("Conexao:", "ONLINE" if conectado else "OFFLINE")
    print()

    print("Temperatura:", payload["temperature"], "C")
    print("Status temperatura:", payload["temperature_status"])
    print()

    print("Oxigenacao simulada:", payload["oxygen_level"], "%")
    print("Status oxigenacao:", payload["oxygen_status"])
    print()

    print("Batimento simulado:", payload["heart_rate"], "bpm")
    print("Status batimento:", payload["heart_rate_status"])
    print()

    print("Status geral:", payload["status"])
    print()


# ============================================================
# EXIBIÇÃO OLED
# ============================================================


# Atualiza o OLED SSD1306 com os principais indicadores.
def atualizar_oled(payload, conectado):
  
    try:
        oled.fill(0)

        oled.text("CardioIA", 0, 0)

        if conectado:
            oled.text("ON", 108, 0)
        else:
            oled.text("OFF", 98, 0)

        oled.text("BPM: {}".format(payload["heart_rate"]), 0, 12)
        oled.text("Temp: {} C".format(payload["temperature"]), 0, 24)
        oled.text("O2: {} %".format(payload["oxygen_level"]), 0, 36)
        oled.text("St: {}".format(status_curto(payload["status"])), 0, 48)

        oled.show()

    except Exception as erro:
        print("ERRO ao atualizar OLED:", erro)


# Tela inicial exibida ao ligar o dispositivo.
def tela_inicial_oled():

    try:
        oled.fill(0)
        oled.text("CardioIA", 0, 0)
        oled.text("Fase 7", 0, 14)
        oled.text("DHT + BPM", 0, 28)
        oled.text("Inicializando", 0, 46)
        oled.show()

    except Exception as erro:
        print("ERRO na tela inicial OLED:", erro)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

print("CardioIA IoT - MicroPython + OLED iniciado.")
print("DHT22 DATA = GPIO 23")
print("DHT22 temperatura = temperatura corporal simulada")
print("DHT22 umidade = oxigenacao simulada")
print("POTENCIOMETRO ADC = GPIO 34")
print("POTENCIOMETRO = batimentos cardiacos simulados")
print("CHAVE ONLINE/OFFLINE = GPIO 19")
print("OLED SDA = GPIO 21")
print("OLED SCL = GPIO 22")
print("OLED ADDR = 0x3C")
print("OFF = buffer local | ON = envio Cloud/API simulado")

if oled is not None:
    print("OLED inicializado com sucesso.")
    tela_inicial_oled()
    sleep(1)
else:
    print("OLED indisponivel. Sistema seguira apenas pelo Serial.")
    print("Se estiver no Wokwi, adicione o arquivo ssd1306.py caso o import falhe.")

conectado_anterior = False

while True:
    conectado = leitura_conexao()

    if not conectado_anterior and conectado:
        sincronizar_buffer(FILE_BUFFER)

    conectado_anterior = conectado

    limpar_terminal()

    payload = montar_payload()
    payload_backend = payload_para_backend(payload)

    exibir_dados_serial(payload, conectado)
    atualizar_oled(payload, conectado)

    linha_backend = json.dumps(payload_backend)

    if conectado:
        enviar_para_cloud(payload_backend)
    else:
        gravar_buffer(FILE_BUFFER, linha_backend)
        limitar_buffer(FILE_BUFFER, MAX_BUFFER_BYTES)

        print("OFFLINE: payload gravado no buffer local.")
        print(linha_backend)

        sleep(1)