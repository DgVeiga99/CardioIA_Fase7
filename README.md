# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="../../../assets/logo-fiap.png" 
       alt="FIAP - Faculdade de Informática e Administração Paulista" 
       width="40%">
</a>
</p>

<br>

# CardioIA — Plataforma Inteligente de Monitoramento Cardíaco com IoT, Chatbot, Visão Computacional e Inteligência Artificial

## 👨‍🎓 Integrantes

* <a href="https://www.linkedin.com/in/diego-veiga-5b884317b">Diego Nunes Veiga</a>

## 👩‍🏫 Professores

### Coordenador(a)

* André Godoi Chiovato

---

## 📜 Descrição

O **CardioIA** é uma Prova de Conceito (POC/MVP) desenvolvida para a Fase 7 da FIAP, com foco na integração de tecnologias de **Inteligência Artificial**, **Internet das Coisas**, **visão computacional**, **chatbot conversacional**, **análise de risco cardíaco**, **backend integrador**, **aplicação Web** e **aplicação Mobile**.

A proposta do projeto é demonstrar como sinais vitais simulados, dados clínicos, modelos inteligentes e interfaces digitais podem ser utilizados em conjunto para apoiar processos de triagem, monitoramento preventivo e análise preliminar de risco cardíaco. O sistema foi projetado para receber ou simular dados de sensores, classificar o estado geral do paciente, calcular um score de risco, gerar recomendações clínicas e disponibilizar uma experiência integrada ao usuário por meio de interface Web e Mobile.

O MVP utiliza sinais vitais como **batimentos cardíacos**, **temperatura corporal** e **oxigenação**. Esses dados podem ser inseridos manualmente pelo usuário na interface Web ou simulados por meio de uma camada IoT inspirada em um dispositivo **ESP32 com MicroPython**, utilizando sensores e componentes como DHT22, potenciômetro, chave digital, LED e display OLED. A lógica de captura e processamento dos sensores foi estruturada em MicroPython para simular a execução em dispositivos embarcados no ambiente Wokwi.

A análise de risco cardíaco foi implementada por meio de regras explicáveis, que classificam individualmente cada sinal vital e calculam um score geral do paciente. A partir desse score, o sistema define níveis como **baixo**, **baixo monitorado**, **moderado** e **alto**, gerando recomendações preventivas conforme o estado identificado. Essa abordagem permite que o usuário compreenda os motivos que levaram à classificação do risco.

Além da análise de sinais vitais, o projeto integra um **chatbot conversacional**, preparado para utilizar o **IBM Watson Assistant** quando configurado. Caso as credenciais do Watson não estejam disponíveis, o sistema utiliza um fallback local, mantendo a funcionalidade básica do assistente. O chatbot foi pensado para responder dúvidas sobre sinais vitais, risco cardíaco, sensores, oxigenação, temperatura, batimentos cardíacos, funcionamento da plataforma e análise de raio X.

O sistema também conta com um módulo de **visão computacional**, utilizando **TensorFlow/Keras** para classificação de imagens de raio X de tórax. O usuário pode selecionar uma imagem no frontend, visualizar uma prévia antes do envio e encaminhá-la ao backend para análise. O modelo retorna a classe prevista, o percentual de confiança, uma interpretação e um ranking das classes detectadas.

A arquitetura do projeto foi desenvolvida com uma **API em FastAPI**, responsável por centralizar os serviços de análise de risco, sensores, recomendações, chatbot, visão computacional, dados das fases anteriores e integração geral da aplicação. O frontend Web foi desenvolvido em **React com Vite**, publicado na **Vercel**, com suporte a rotas SPA por meio do arquivo `vercel.json`. O aplicativo Mobile foi desenvolvido com **React Native + Expo**, configurado para build em nuvem com **Expo EAS**, permitindo a geração de um arquivo `.apk` funcional.

Como impacto positivo, o CardioIA demonstra como soluções digitais inteligentes podem apoiar a saúde preventiva, a educação tecnológica e a tomada de decisão inicial em cenários simulados. Embora o projeto não tenha finalidade diagnóstica real, ele apresenta uma arquitetura expansível que pode evoluir futuramente com sensores físicos reais, banco de dados em nuvem, autenticação, histórico clínico e integração com serviços médicos.

---

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

* <b>backend</b>: Pasta responsável pela API do projeto, desenvolvida com FastAPI. Contém o arquivo `main.py`, que centraliza as rotas de análise de risco, sensores, recomendações, chatbot, visão computacional, integração de dados e status geral da plataforma.

* <b>backend/services</b>: Pasta que contém os serviços principais da aplicação. Cada arquivo concentra uma responsabilidade específica, como análise de risco, simulação de sensores, recomendações, chatbot, visão computacional, dados das fases anteriores, base de conhecimento e integração geral.

* <b>backend/vision</b>: Pasta destinada aos scripts relacionados ao treinamento do modelo de visão computacional. Contém o arquivo `train_xray_model.py`, responsável por treinar o modelo TensorFlow/Keras para classificação de imagens de raio X.

* <b>backend/models</b>: Pasta responsável por armazenar os modelos treinados e arquivos auxiliares. Contém o modelo `xray_chest_model.keras`, o mapeamento `xray_class_indices.json` e o histórico de treinamento `xray_training_history.json`.

* <b>backend/data</b>: Pasta destinada aos dados utilizados pelo backend. Inclui dados de visão computacional, arquivos de integração das fases anteriores e bases auxiliares utilizadas pelos serviços da aplicação.

* <b>backend/data/vision</b>: Pasta utilizada para o treinamento e execução do módulo de raio X. Contém o arquivo `metadata.csv`, a pasta `images` com as imagens de treinamento e a pasta de uploads utilizada durante a análise.

* <b>frontend-web</b>: Pasta responsável pela aplicação Web desenvolvida com React e Vite. Contém a interface principal do usuário, incluindo login demonstrativo, dashboard, análise de risco, chatbot, raio X, arquitetura e descrição do projeto.

* <b>frontend-web/src</b>: Pasta com os arquivos principais do frontend Web. Contém `App.jsx`, `main.jsx` e `styles.css`.

* <b>frontend-web/vercel.json</b>: Arquivo de configuração utilizado para o deploy na Vercel, garantindo suporte a rotas SPA em aplicações React.

* <b>mobile</b>: Pasta destinada ao aplicativo Mobile desenvolvido com Expo/React Native. Representa a camada móvel da solução, preparada para consumir a mesma API utilizada pelo frontend Web.

* <b>mobile/app.json</b>: Arquivo de configuração do aplicativo Expo, contendo informações como nome, slug e pacote Android em formato de domínio invertido.

* <b>mobile/eas.json</b>: Arquivo de configuração do Expo EAS Build, contendo o perfil `preview` utilizado para gerar o APK funcional na nuvem.

* <b>iot</b>: Pasta destinada ao código MicroPython do projeto. Contém o script `.py` utilizado para simular a captura e o processamento de sinais vitais em um dispositivo como ESP32 no ambiente Wokwi.

* <b>docs</b>: Pasta destinada à documentação complementar do projeto, incluindo relatório técnico, diagrama de arquitetura, prints comprobatórios, evidências de deploy, evidências do APK e link do vídeo demonstrativo.

* <b>README.md</b>: Arquivo de documentação geral do projeto, contendo descrição, estrutura, tecnologias, execução, endpoints, deploy, build Mobile, Wokwi, evidências e observações importantes.

---

## 📎 Links e Observações

* <b>Listagem de Links</b>:

  * Repositório GitHub privado: `INSERIR_LINK_DO_REPOSITORIO_PRIVADO`
  * URL pública da aplicação Web na Vercel: `INSERIR_URL_PUBLICA_DA_VERCEL`
  * Link do build APK no Expo: `INSERIR_LINK_DO_BUILD_APK_EXPO`
  * Link direto para download do APK: `INSERIR_LINK_DIRETO_DO_APK`
  * Link público do projeto Wokwi: `INSERIR_LINK_PUBLICO_DO_WOKWI`
  * Vídeo demonstrativo no YouTube/Drive: `INSERIR_LINK_DO_VIDEO_DEMONSTRATIVO`
  * Documentação Swagger da API local: `http://127.0.0.1:8000/docs`
  * Frontend Web local: `http://localhost:5173`

* <b>Explicação de decisões técnicas</b>:

  * O projeto utiliza sinais vitais simulados para viabilizar a construção do MVP sem depender de sensores físicos reais durante a fase de desenvolvimento.
  * A análise de risco cardíaco foi desenvolvida com regras explicáveis para facilitar a interpretação do resultado e dos motivos associados ao risco.
  * O backend foi desenvolvido com FastAPI por ser leve, performático e adequado para criação de APIs REST em Python.
  * O backend funciona como núcleo integrador entre as interfaces Web/Mobile, os motores de IA, o chatbot, o modelo de visão computacional e os dados das fases anteriores.
  * O frontend foi desenvolvido com React e Vite para permitir uma interface moderna, modular e de rápida execução local.
  * A aplicação Web foi preparada para deploy na Vercel com suporte a rotas SPA por meio do arquivo `vercel.json`.
  * O aplicativo Mobile foi desenvolvido com Expo e configurado com `app.json` e `eas.json` para geração de APK em nuvem pelo Expo EAS.
  * A simulação IoT foi estruturada em MicroPython, representando a execução em um ESP32 dentro do ambiente Wokwi.
  * O chatbot utiliza IBM Watson Assistant quando configurado e fallback local quando as credenciais não estão disponíveis.
  * O módulo de raio X utiliza TensorFlow/Keras para demonstrar o uso de visão computacional aplicada à saúde.
  * A prévia da imagem no frontend foi implementada para melhorar a experiência do usuário antes do envio ao modelo.
  * A arquitetura foi dividida em serviços para facilitar manutenção, testes e evolução do projeto.

* <b>Observações Gerais</b>:

  * O projeto é uma Prova de Conceito acadêmica e não deve ser utilizado como sistema médico real.
  * As análises geradas pelo CardioIA não substituem avaliação médica, exames clínicos, laudos ou diagnóstico profissional.
  * Toda interpretação clínica deve ser realizada por profissionais da saúde habilitados.
  * A solução pode ser evoluída futuramente com sensores físicos, banco de dados, autenticação, histórico de pacientes, nuvem e integração com serviços reais de saúde.
  * O repositório GitHub deve permanecer privado, porém compartilhado com o tutor responsável pela avaliação.

---

## 🚀 Deploy, Distribuição e Evidências da Entrega

### 🌐 Aplicação Web publicada na Vercel

A aplicação Web desenvolvida em React + Vite foi preparada para publicação na plataforma Vercel, com suporte a rotas SPA configurado por meio do arquivo `vercel.json`.

* URL pública da aplicação Web: `INSERIR_URL_PUBLICA_DA_VERCEL`
* Plataforma de deploy: Vercel
* Integração CI/CD: GitHub conectado à Vercel
* Repositório: Privado, compartilhado com o tutor
* Status: Deploy automático a cada push no GitHub

Arquivo `frontend-web/vercel.json` utilizado:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 📱 Aplicativo Mobile e APK

O aplicativo Mobile foi desenvolvido com React Native + Expo e configurado para build em nuvem utilizando o Expo EAS.

O arquivo `app.json` contém o campo `android.package` no formato de domínio invertido, conforme solicitado na atividade.

* Link do build APK no Expo: `INSERIR_LINK_DO_BUILD_APK_EXPO`
* Link direto para download do APK: `INSERIR_LINK_DIRETO_DO_APK`
* Tipo de build: APK
* Perfil utilizado: `preview`
* Plataforma: Android

O arquivo `eas.json` contém o perfil de build `preview`, utilizado para gerar um APK funcional para instalação em dispositivo real.

### 🔌 Projeto IoT com MicroPython no Wokwi

A camada IoT foi implementada em MicroPython, simulando a execução em dispositivo ESP32 no ambiente Wokwi.

O projeto simula a captura e o processamento de sinais vitais, como temperatura e batimentos cardíacos, com feedback visual por LED/OLED.

* Link público do projeto Wokwi: `INSERIR_LINK_PUBLICO_DO_WOKWI`

### 🎥 Vídeo Demonstrativo

O vídeo demonstrativo apresenta o fluxo fim-a-fim da solução, desde a simulação dos sensores no Wokwi até a atualização e visualização dos dados cardíacos na aplicação Web publicada na Vercel e/ou no APK instalado em um dispositivo real.

* Link do vídeo demonstrativo: `INSERIR_LINK_DO_VIDEO_DEMONSTRATIVO`
* Duração máxima prevista: até 5 minutos

### 📸 Prints comprobatórios

As evidências visuais da entrega devem ser armazenadas na pasta `docs/prints`.

Prints recomendados:

* Deploy concluído na Vercel
* Build APK concluído no Expo
* Aplicativo instalado em dispositivo real
* Tela de login da aplicação Web
* Dashboard com dados cardíacos
* Simulação Wokwi em MicroPython
* Status do backend FastAPI
* Teste de raio X com prévia de imagem

Estrutura sugerida:

```bash
docs/
└── prints/
    ├── 01-vercel-deploy.png
    ├── 02-expo-build-apk.png
    ├── 03-app-instalado.png
    ├── 04-login-web.png
    ├── 05-dashboard-cardioia.png
    ├── 06-raio-x-preview.png
    ├── 07-wokwi-micropython.png
    └── 08-swagger-backend.png
```

### 📄 Relatório Técnico

O relatório técnico em PDF apresenta o diagrama da arquitetura final e descreve o fluxo de dados da solução:

```txt
Sensor → MicroPython → Backend Python → APIs de IA → UI Web/Mobile
```

Arquivo esperado:

```bash
docs/relatorio-tecnico-cardioia.pdf
```

O relatório deve possuir no máximo cinco páginas e contemplar:

* Objetivo do projeto
* Diagrama de arquitetura final
* Explicação do fluxo de dados
* Integração entre IoT, Backend, IA e interfaces
* Evidências de validação e conclusão

---

## 🔧 Como executar o código

### Pré-requisitos

Para executar o projeto localmente, recomenda-se utilizar:

* Python 3.10 ou superior
* Node.js
* npm
* Visual Studio Code
* Git
* Ambiente virtual Python (`venv`)
* Navegador web atualizado
* Expo CLI, caso deseje executar o aplicativo Mobile
* Conta Expo para geração do APK via EAS Build
* Conta Vercel para publicação da aplicação Web
* TensorFlow instalado no ambiente Python para uso do módulo de visão computacional

---

### Bibliotecas e tecnologias utilizadas

As principais bibliotecas e tecnologias utilizadas no projeto são:

* fastapi
* uvicorn
* tensorflow
* keras
* numpy
* pillow
* python-multipart
* ibm-watson
* python-dotenv
* React
* Vite
* JavaScript
* CSS
* Expo
* React Native
* MicroPython
* Wokwi

---

### 1. Clonar o repositório

Após o projeto estar publicado no GitHub, clone o repositório com:

```bash
git clone URL_DO_REPOSITORIO
cd CardioIA-Fase7
```

Caso o projeto já esteja localmente no computador, basta abrir a pasta no Visual Studio Code.

---

### 2. Criar e ativar o ambiente virtual do backend

Acesse a pasta do backend:

```bash
cd backend
```

No Windows, execute:

```bash
python -m venv venv
venv\Scripts\activate
```

Caso esteja utilizando PowerShell e ocorra bloqueio de script, execute:

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois ative com:

```bash
.\venv\Scripts\Activate.ps1
```

No Linux ou macOS, execute:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Instalar as dependências do backend

Com o ambiente virtual ativo, execute:

```bash
pip install -r requirements.txt
```

---

### 4. Executar a API FastAPI

Dentro da pasta `backend`, execute:

```bash
python -m uvicorn main:app --reload
```

A API ficará disponível em:

```bash
http://127.0.0.1:8000
```

A documentação Swagger pode ser acessada em:

```bash
http://127.0.0.1:8000/docs
```

---

### 5. Testar o status da API

Com o backend em execução, acesse:

```bash
http://127.0.0.1:8000/api/health
```

Também podem ser testados os principais status da plataforma:

```bash
http://127.0.0.1:8000/api/integration/status
http://127.0.0.1:8000/api/chatbot/status
http://127.0.0.1:8000/api/vision/status
```

---

### 6. Executar o frontend Web

Abra um segundo terminal e acesse a pasta do frontend:

```bash
cd frontend-web
```

Instale as dependências:

```bash
npm install
```

Execute o frontend:

```bash
npm run dev
```

O frontend será aberto em:

```bash
http://localhost:5173
```

---

### 7. Executar o projeto completo localmente

Para demonstrar o MVP completo em ambiente local, mantenha pelo menos dois terminais abertos:

Terminal 1 — Backend FastAPI:

```bash
cd backend
python -m uvicorn main:app --reload
```

Terminal 2 — Frontend Web:

```bash
cd frontend-web
npm run dev
```

Acesse no navegador:

```bash
http://localhost:5173
```

---

### 8. Executar o treinamento do modelo de raio X

A estrutura esperada para treinamento é:

```bash
backend/data/vision/
├── metadata.csv
└── images/
```

Exemplo de `metadata.csv`:

```csv
filename,label
imagem_001.png,normal
imagem_002.png,pneumonia
imagem_003.png,cardiomegalia
```

Para treinar o modelo, acesse a pasta do backend e execute:

```bash
python vision/train_xray_model.py
```

Após o treinamento, os arquivos serão gerados em:

```bash
backend/models/xray_chest_model.keras
backend/models/xray_class_indices.json
backend/models/xray_training_history.json
```

---

### 9. Executar o aplicativo Mobile

Acesse a pasta do aplicativo Mobile:

```bash
cd mobile
```

Instale as dependências:

```bash
npm install
```

Execute o projeto Expo:

```bash
npx expo start
```

O aplicativo poderá ser aberto no navegador, emulador ou dispositivo físico com Expo Go.

---

### 10. Gerar APK com Expo EAS

Acesse a pasta do aplicativo Mobile:

```bash
cd mobile
```

Faça login no Expo:

```bash
eas login
```

Execute o build Android utilizando o perfil `preview`:

```bash
eas build -p android --profile preview
```

Ao final do processo, o Expo exibirá um link para o build no dashboard. Esse link deverá ser inserido no campo:

```bash
INSERIR_LINK_DO_BUILD_APK_EXPO
```

---

### 11. Publicar o frontend na Vercel

Acesse a pasta do frontend:

```bash
cd frontend-web
```

Instale a CLI da Vercel, caso necessário:

```bash
npm install -g vercel
```

Execute o deploy:

```bash
vercel
```

Para publicar em produção:

```bash
vercel --prod
```

Após a publicação, a URL pública gerada pela Vercel deverá ser inserida no campo:

```bash
INSERIR_URL_PUBLICA_DA_VERCEL
```

---

## 🌐 Principais Endpoints da API

### Status geral

```http
GET /api/health
```

Verifica se o backend está online.

---

### Status de integração

```http
GET /api/integration/status
```

Retorna o status geral da plataforma e dos módulos integrados.

---

### Simulação IoT

```http
GET /api/iot/simulate?cenario=normal
```

Cenários disponíveis:

```bash
normal
atencao
critico
offline_buffer
aleatorio
```

---

### Simulação IoT em lote

```http
GET /api/iot/simulate/batch?cenario=aleatorio&quantidade=10
```

Gera múltiplas leituras simuladas de sensores.

---

### Normalização dos sensores

```http
POST /api/sensors/normalize
```

Recebe um payload de sensores e retorna os dados normalizados.

---

### Análise de risco cardíaco

```http
POST /api/analyze
```

Exemplo de envio:

```json
{
  "patient_id": "PACIENTE_WEB_001",
  "heart_rate": 88,
  "temperature": 36.8,
  "oxygen_level": 97,
  "source": "frontend_web"
}
```

---

### Recomendação preventiva

```http
POST /api/recommendation
```

Gera uma recomendação com base no resultado da análise de risco.

---

### Status do chatbot

```http
GET /api/chatbot/status
```

Verifica se o IBM Watson Assistant está configurado ou se o fallback local será utilizado.

---

### Enviar mensagem ao chatbot

```http
POST /api/chatbot/message
```

Exemplo de envio:

```json
{
  "message": "Minha oxigenação está baixa. O que devo fazer?",
  "session_id": null
}
```

---

### Reiniciar conversa do chatbot

```http
POST /api/chatbot/restart
```

Reinicia a sessão conversacional do assistente.

---

### Status da visão computacional

```http
GET /api/vision/status
```

Verifica se o modelo de raio X e o mapeamento de classes foram encontrados.

---

### Análise de raio X

```http
POST /api/vision/xray
```

Recebe uma imagem de raio X e retorna a classificação realizada pelo modelo de machine learning.

---

### Consulta à base de conhecimento

```http
POST /api/knowledge/search
```

Consulta informações estruturadas na base de conhecimento do projeto.

---

### Resposta baseada em conhecimento

```http
POST /api/knowledge/answer
```

Gera uma resposta com base nas informações disponíveis na base de conhecimento local.

---

## 🫀 Análise de Risco Cardíaco

A análise de risco do CardioIA considera três sinais principais:

* Batimentos cardíacos
* Temperatura corporal
* Oxigenação

Cada sinal é classificado individualmente, permitindo identificar alterações como:

* Batimentos normais
* Batimentos elevados
* Batimentos baixos
* Batimentos críticos
* Temperatura normal
* Febre
* Febre alta
* Oxigenação normal
* Oxigenação leve
* Oxigenação moderada
* Oxigenação grave

Com base nessas classificações, o sistema calcula um score de risco e define o estado geral do paciente.

Os níveis de risco possíveis são:

```bash
baixo
baixo_monitorado
moderado
alto
```

A partir do nível identificado, o sistema gera uma recomendação preventiva para o usuário.

---

## 📡 Simulação de Sensores IoT

O projeto utiliza uma simulação baseada no comportamento esperado de sensores conectados a um ESP32.

Sensores simulados:

* DHT22 para temperatura
* DHT22 para umidade utilizada como oxigenação simulada
* Potenciômetro para batimentos cardíacos
* Chave digital para estado do paciente
* LED para alerta visual
* Display OLED para exibição local

Os cenários simulados pelo backend são:

* `normal`
* `atencao`
* `critico`
* `offline_buffer`
* `aleatorio`

Essa simulação permite testar a plataforma mesmo sem sensores físicos conectados.

---

## 🔌 MicroPython e Wokwi

A lógica de sensores foi convertida para MicroPython para simular a execução em dispositivos como ESP32 ou Raspberry Pi no ambiente Wokwi.

O fluxo simulado contempla:

```txt
Leitura dos sensores → Processamento local → Classificação simples → Feedback visual → Envio/representação dos dados
```

O projeto Wokwi deve demonstrar:

* Leitura simulada de temperatura
* Leitura simulada de batimentos cardíacos
* Processamento dos valores
* Indicação visual por LED e/ou OLED
* Representação do estado do paciente

Link público da simulação:

```bash
INSERIR_LINK_PUBLICO_DO_WOKWI
```

---

## 🤖 Chatbot

O chatbot foi desenvolvido para auxiliar o usuário com perguntas relacionadas a:

* Sinais vitais
* Risco cardíaco
* Temperatura corporal
* Oxigenação
* Batimentos cardíacos
* Sensores IoT
* Funcionamento da plataforma
* Análise de raio X

Quando as credenciais do IBM Watson Assistant estão configuradas, o sistema utiliza o Watson. Caso contrário, utiliza um fallback local.

Variáveis de ambiente esperadas:

```env
WATSON_API_KEY=
WATSON_SERVICE_URL=
WATSON_ASSISTANT_ID=
WATSON_VERSION=2024-08-25
```

---

## 🩻 Visão Computacional e Raio X

O módulo de visão computacional utiliza um modelo TensorFlow/Keras treinado para classificar imagens de raio X de tórax.

Arquivos esperados:

```bash
backend/models/xray_chest_model.keras
backend/models/xray_class_indices.json
backend/models/xray_training_history.json
```

O treinamento é realizado pelo arquivo:

```bash
backend/vision/train_xray_model.py
```

Na aplicação Web, o usuário pode:

* Selecionar uma imagem de raio X
* Visualizar uma prévia da imagem antes do envio
* Enviar a imagem para análise
* Consultar a classe prevista
* Verificar o percentual de confiança
* Visualizar o ranking de classes
* Ler uma interpretação gerada pelo sistema

---

## 🧩 Arquitetura Final

A arquitetura final do CardioIA foi consolidada para integrar sensores, backend, modelos de IA, chatbot e interfaces de usuário.

Fluxo principal:

```txt
Sensor → MicroPython → Backend Python → APIs de IA → UI Web/Mobile
```

Fluxo detalhado:

```txt
ESP32 / Wokwi / MicroPython
        ↓
Captura de sinais vitais simulados
        ↓
Processamento inicial dos dados
        ↓
Backend FastAPI Integrador
        ↓
Normalização dos sinais vitais
        ↓
Motor de análise de risco cardíaco
        ↓
Motor de recomendações clínicas
        ↓
Chatbot IBM Watson / Fallback local
        ↓
Modelo TensorFlow/Keras para raio X
        ↓
Frontend Web React + Vite
        ↓
Aplicativo Mobile React Native + Expo
```

---

## 🧪 Fluxo de Teste da Plataforma

Para validar o funcionamento completo do MVP:

1. Abrir o backend FastAPI.
2. Abrir o frontend Web local ou URL pública da Vercel.
3. Fazer login demonstrativo.
4. Verificar se o backend aparece online.
5. Simular sensores em cenário normal.
6. Simular sensores em cenário crítico.
7. Verificar a mudança de cores nos cards.
8. Executar uma análise de risco manual.
9. Acessar o chatbot.
10. Enviar uma pergunta.
11. Reiniciar a conversa.
12. Acessar a aba de raio X.
13. Selecionar uma imagem.
14. Confirmar a prévia da imagem.
15. Enviar para análise.
16. Verificar classe prevista, confiança e ranking.
17. Abrir o app Mobile instalado via APK.
18. Validar login e visualização dos dados cardíacos.
19. Abrir o projeto Wokwi.
20. Validar o fluxo MicroPython e feedback visual.

---

## 🗃 Histórico de lançamentos

* 1.0.0 - 12/06/2026

  * Deploy completo da solução final após testes operacionais e validação dos módulos de backend, frontend, sensores simulados, chatbot, visão computacional, Mobile, MicroPython e análise de risco cardíaco.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/SabrinaOtoni/TEMPLATE-FIAP-GRAD-ON-IA">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
