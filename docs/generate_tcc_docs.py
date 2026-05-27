"""
Gera 10 PDFs separados em TCC-docs/, cada um focado em um tema do projeto.
Rodar: python docs/generate_tcc_docs.py
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "TCC-docs"
OUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# Estilos compartilhados
# ============================================================================
styles = getSampleStyleSheet()
PRIMARY = colors.HexColor("#2D7A4F")
SECONDARY = colors.HexColor("#1C3D29")
TEXT = colors.HexColor("#1F2A1F")
SOFT = colors.HexColor("#5C6B5C")
BG_LIGHT = colors.HexColor("#F3F7F2")
BORDER = colors.HexColor("#D7E1D8")

title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=24, leading=30,
                             alignment=TA_CENTER, textColor=PRIMARY, spaceAfter=12)
subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=13, leading=17,
                                alignment=TA_CENTER, textColor=SOFT, spaceAfter=8)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, leading=24,
                    textColor=PRIMARY, spaceBefore=16, spaceAfter=10)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, leading=19,
                    textColor=SECONDARY, spaceBefore=12, spaceAfter=7)
h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, leading=15,
                    textColor=SECONDARY, spaceBefore=8, spaceAfter=5)
body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15.5,
                      alignment=TA_JUSTIFY, textColor=TEXT, spaceAfter=8)
bullet = ParagraphStyle("Bullet", parent=body, leftIndent=18, bulletIndent=4, spaceAfter=4)
code = ParagraphStyle("Code", parent=styles["Code"], fontSize=9, leading=12,
                      textColor=SECONDARY, leftIndent=10, backColor=BG_LIGHT,
                      borderColor=BORDER, borderWidth=0.5, borderPadding=6,
                      spaceBefore=4, spaceAfter=8)
formula = ParagraphStyle("Formula", parent=body, fontSize=11, leading=16, alignment=TA_CENTER,
                         textColor=SECONDARY, spaceBefore=4, spaceAfter=8,
                         backColor=BG_LIGHT, borderColor=BORDER, borderWidth=0.5, borderPadding=6)


def P(t, st=body):
    return Paragraph(t, st)


def B(t):
    return P(f"&bull; &nbsp; {t}", bullet)


def boxed_table(rows, col_widths=None):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def cover(title, subtitle):
    return [
        Spacer(1, 5 * cm),
        P("AgroVision", title_style),
        P(f"<b>{title}</b>", ParagraphStyle("CT", parent=title_style, fontSize=18,
                                            textColor=SECONDARY, spaceAfter=10)),
        P(subtitle, subtitle_style),
        Spacer(1, 5 * cm),
        P("TCC-Docs &middot; Material de estudo<br/>Luiz Carlos Junior &amp; Equipe AgroVision<br/>Maio de 2026",
          ParagraphStyle("CA", parent=body, alignment=TA_CENTER, fontSize=10.5, textColor=SOFT, leading=16)),
        PageBreak(),
    ]


# ============================================================================
# 01 - ARQUITETURA COMPLETA
# ============================================================================
def build_arquitetura():
    s = cover("01 - Arquitetura Completa", "Visao geral do sistema de ponta a ponta")

    s.append(P("1. Visao Geral", h1))
    s.append(P(
        "O AgroVision e um sistema distribuido em tres camadas independentes, conectadas por "
        "protocolos HTTPS e WebSocket Secure (WSS). A separacao foi feita para permitir que cada camada "
        "tenha um ciclo de vida proprio: o app movel evolui sem precisar de redeploy do backend, e o "
        "backend pode ser substituido sem afetar a UI."
    ))

    s.append(P("2. As tres camadas", h1))
    s.append(boxed_table([
        ["Camada", "Local de execucao", "Responsabilidade"],
        ["App movel", "Dispositivo do usuario (iOS/Android)", "Captura, UI, persistencia local, exibicao do diagnostico"],
        ["Backend de IA", "Container Linux no Railway", "Inferencia Grad-CAM, calculo AL/AFS, proxy para Roboflow"],
        ["Servico de classificacao", "Roboflow Serverless (cloud)", "Classificacao ResNet50 de quatro classes"],
    ], col_widths=[3.5 * cm, 5 * cm, 8.5 * cm]))

    s.append(P("3. Fluxo de dados na requisicao tipica", h1))
    s.append(P(
        "1. Usuario captura uma foto da folha de milho com a camera do celular.<br/>"
        "2. App converte a imagem em base64 e abre um WebSocket para o backend (endpoint /ws/classify).<br/>"
        "3. Backend redimensiona a imagem (640px no maior lado), reencoda e envia ao Roboflow Serverless.<br/>"
        "4. Roboflow devolve {prediction, confidence, source: 'roboflow'} para o backend.<br/>"
        "5. Backend repassa pelo WebSocket; UI exibe a doenca identificada e descritivos.<br/>"
        "6. Usuario opcionalmente clica 'Auditar Modelo' &rarr; nova requisicao WSS para /ws/gradcam.<br/>"
        "7. Backend executa Grad-CAM no modelo Keras local + calcula AL/AFS sobre o heatmap.<br/>"
        "8. Backend devolve heatmap (PNG base64) + metricas; UI renderiza overlay + interpretacao.",
        code,
    ))

    s.append(P("4. Comunicacao entre camadas", h1))
    s.append(B("<b>App &harr; Backend:</b> WebSocket Secure (WSS) com payloads JSON. Headers de autenticacao por X-API-Key ou query string."))
    s.append(B("<b>Backend &harr; Roboflow:</b> HTTPS POST com base64 no body. URL: https://serverless.roboflow.com/{slug}/{version}?api_key=..."))
    s.append(B("<b>App &harr; SQLite local:</b> acesso sincrono via expo-sqlite, sem rede."))

    s.append(P("5. Por que essa topologia", h1))
    s.append(P(
        "<b>WebSocket em vez de REST puro</b> para o Grad-CAM porque a operacao demora alguns segundos no "
        "cold start do backend; o WebSocket envia eventos de progresso intermediarios "
        "(<i>preprocessing, building_model, computing_gradients, rendering_overlay</i>) que sao "
        "renderizados como barra de progresso na UI."
    ))
    s.append(P(
        "<b>Dois modelos separados</b> (Roboflow e Keras local) porque a API serverless do Roboflow nao "
        "expoe gradientes &mdash; condicao necessaria para Grad-CAM. Mantemos um segundo modelo "
        "MobileNetV2 treinado no mesmo dataset cuja unica funcao e gerar a auditoria visual."
    ))

    s.append(P("6. Deployment", h1))
    s.append(boxed_table([
        ["Item", "Configuracao"],
        ["Plataforma", "Railway (plano Hobby)"],
        ["Build system", "Nixpacks"],
        ["Python", "3.12"],
        ["Entry point", "uvicorn api.server:app --host 0.0.0.0 --port $PORT"],
        ["Modelo no container", "model_species.keras (24MB)"],
        ["Variaveis de ambiente", "ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID, AGROVISION_API_KEY"],
    ], col_widths=[5 * cm, 11.5 * cm]))

    return s


# ============================================================================
# 02 - BANCO DE DADOS
# ============================================================================
def build_banco():
    s = cover("02 - Banco de Dados", "Persistencia local offline-first com SQLite")

    s.append(P("1. Tipo e localizacao", h1))
    s.append(P(
        "O AgroVision utiliza <b>SQLite</b> embarcado no proprio dispositivo do usuario, atraves da "
        "biblioteca <font color='#1C3D29'><b>expo-sqlite</b></font>. Nao ha servidor de banco em nuvem, "
        "nem replicacao. Cada usuario tem seu proprio arquivo <code>agrovision.db</code> dentro do "
        "sandbox privado do app no sistema operacional movel."
    ))

    s.append(P("2. Por que local e nao remoto?", h1))
    s.append(B("<b>Conectividade incerta no campo</b>: o app precisa funcionar offline para consulta a historicos."))
    s.append(B("<b>Privacidade agronomica</b>: dados de safra/diagnostico sao sensiveis comercialmente. Nao centralizar reduz risco de vazamento."))
    s.append(B("<b>Custo zero de hospedagem</b>: sem servidor de DB, sem cobranca por uso."))
    s.append(B("<b>Latencia zero de leitura</b>: queries em milissegundos, sem round-trip de rede."))

    s.append(P("3. Schema (duas tabelas)", h1))

    s.append(P("3.1. Tabela <code>analyses</code>", h2))
    s.append(P("Armazena o historico de identificacoes feitas pelo usuario.", body))
    s.append(P(
        "CREATE TABLE analyses (<br/>"
        "&nbsp;&nbsp;id              TEXT PRIMARY KEY,<br/>"
        "&nbsp;&nbsp;type            TEXT NOT NULL,         -- 'species', 'disease', etc.<br/>"
        "&nbsp;&nbsp;result          TEXT NOT NULL,         -- nome PT-BR da classe<br/>"
        "&nbsp;&nbsp;confidence      REAL NOT NULL,         -- 0..1<br/>"
        "&nbsp;&nbsp;description     TEXT NOT NULL,         -- descritivo patologico<br/>"
        "&nbsp;&nbsp;recommendations TEXT NOT NULL,         -- JSON serializado de array<br/>"
        "&nbsp;&nbsp;imageUri        TEXT NOT NULL,         -- path local da foto<br/>"
        "&nbsp;&nbsp;timestamp       TEXT NOT NULL,         -- ISO 8601<br/>"
        "&nbsp;&nbsp;processingTime  INTEGER NOT NULL,      -- ms<br/>"
        "&nbsp;&nbsp;createdAt       TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;updatedAt       TEXT NOT NULL<br/>"
        ");<br/><br/>"
        "CREATE INDEX idx_analyses_type ON analyses(type);<br/>"
        "CREATE INDEX idx_analyses_timestamp ON analyses(timestamp);",
        code,
    ))

    s.append(P("3.2. Tabela <code>xai_tests</code>", h2))
    s.append(P("Armazena auditorias Grad-CAM salvas pelo usuario na tela cientifica.", body))
    s.append(P(
        "CREATE TABLE xai_tests (<br/>"
        "&nbsp;&nbsp;id            TEXT PRIMARY KEY,<br/>"
        "&nbsp;&nbsp;imageUri      TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;prediction    TEXT NOT NULL,         -- classe predita pelo modelo de auditoria<br/>"
        "&nbsp;&nbsp;confidence    REAL NOT NULL,<br/>"
        "&nbsp;&nbsp;al            REAL NOT NULL,         -- Attention Leakage<br/>"
        "&nbsp;&nbsp;afs           REAL NOT NULL,         -- Attention Focus Score<br/>"
        "&nbsp;&nbsp;threshold     REAL NOT NULL,         -- tau usado no calculo<br/>"
        "&nbsp;&nbsp;bboxJson      TEXT NOT NULL,         -- {x,y,w,h} serializado<br/>"
        "&nbsp;&nbsp;bboxStrategy  TEXT NOT NULL,         -- fixed | green | manual<br/>"
        "&nbsp;&nbsp;overlayB64    TEXT NOT NULL,         -- PNG do heatmap em base64<br/>"
        "&nbsp;&nbsp;label         TEXT NOT NULL,         -- enquadramento rotulado pelo usuario<br/>"
        "&nbsp;&nbsp;createdAt     TEXT NOT NULL<br/>"
        ");<br/><br/>"
        "CREATE INDEX idx_xai_tests_created ON xai_tests(createdAt);<br/>"
        "CREATE INDEX idx_xai_tests_label   ON xai_tests(label);",
        code,
    ))

    s.append(P("4. Padroes de acesso", h1))
    s.append(P(
        "A camada <code>src/services/storage/database.ts</code> expoe um singleton "
        "<code>databaseService</code> com metodos assincronos: <code>initialize()</code> (chamada uma "
        "vez no boot do app), <code>saveAnalysis()</code>, <code>getAllAnalyses()</code>, "
        "<code>saveXAITest()</code>, <code>getAllXAITests()</code>. Todas as queries usam parametros "
        "para evitar SQL injection."
    ))

    s.append(P("5. Como inspecionar o banco em desenvolvimento", h1))
    s.append(B("Android emulator: <code>adb root && adb pull /data/data/host.exp.exponent/databases/agrovision.db</code>"))
    s.append(B("iOS simulator: navegar ate <code>~/Library/Developer/CoreSimulator/Devices/{ID}/.../Documents/SQLite/agrovision.db</code>"))
    s.append(B("Inspecao visual: abrir o arquivo no <i>DB Browser for SQLite</i> (gratuito, multiplataforma)"))

    s.append(P("6. Limites e quando migrar", h1))
    s.append(P(
        "SQLite suporta confortavelmente dezenas de milhares de registros para o tamanho de dado deste "
        "projeto (overlays em base64 pesam ~50KB cada). O sinal de \"hora de migrar\" seria a "
        "necessidade de <b>sincronia entre dispositivos</b> ou <b>analise centralizada</b> &mdash; "
        "casos em que evoluiriamos para um backend com PostgreSQL e API REST de sincronizacao."
    ))

    return s


# ============================================================================
# 03 - ALGORITMO
# ============================================================================
def build_algoritmo():
    s = cover("03 - Algoritmo", "Pipeline completo de inferencia, do pixel ao diagnostico")

    s.append(P("1. Pipeline em alto nivel", h1))
    s.append(P(
        "1. <b>Captura:</b> camera produz JPEG (largura tipica 1500-3000 px, qualidade 80-95).<br/>"
        "2. <b>Encoding:</b> app le bytes e converte para base64.<br/>"
        "3. <b>Upload:</b> WebSocket envia ao backend Railway.<br/>"
        "4. <b>Decoding + preprocessing:</b> backend converte base64 &rarr; PIL Image &rarr; BGR (OpenCV) &rarr; resize 224x224.<br/>"
        "5. <b>Forward pass:</b> tensor (1, 224, 224, 3) entra no MobileNetV2 que tem o "
        "<code>preprocess_input</code> embarcado (normalizacao para [-1, 1]).<br/>"
        "6. <b>Logits:</b> camada Dense final produz vetor de 4 probabilidades softmax.<br/>"
        "7. <b>Top-1:</b> indice da maior probabilidade vira a classe predita.",
        code,
    ))

    s.append(P("2. Grad-CAM passo a passo", h1))
    s.append(P(
        "Em paralelo ao forward pass, o backend instrumenta uma <code>tf.GradientTape</code> que "
        "registra as ativacoes da camada-alvo (por padrao a ultima conv, <code>Conv_1</code>) e "
        "calcula os gradientes do score da classe em relacao a essas ativacoes:"
    ))
    s.append(P("&part;y^c / &part;A^k(i,j)", formula))
    s.append(P(
        "Pooling global desses gradientes:"
    ))
    s.append(P("alpha_k^c = (1/Z) &Sigma;_i &Sigma;_j (&part;y^c / &part;A^k(i,j))", formula))
    s.append(P(
        "Combinacao ponderada dos feature maps + ReLU:"
    ))
    s.append(P("L^c = ReLU( &Sigma;_k alpha_k^c &middot; A^k )", formula))
    s.append(P("Resultado: matriz 7x7 (resolucao espacial da camada-alvo) que e redimensionada bilinear para o tamanho original e normalizada para [0, 1]."))

    s.append(P("3. Calculo AL/AFS", h1))
    s.append(P(
        "Dada a matriz heatmap H (W x H, valores em [0,1]) e a mascara binaria M (mesmo shape, 1 dentro "
        "da bbox, 0 fora):"
    ))
    s.append(P(
        "ativo = H se H &ge; tau, senao 0 &nbsp;&nbsp;&nbsp;(threshold-cut)<br/>"
        "dentro  = soma(ativo &middot; M)<br/>"
        "fora    = soma(ativo &middot; (1 - M))<br/>"
        "total   = dentro + fora<br/>"
        "AL  = fora / total<br/>"
        "AFS = 1 - AL",
        code,
    ))

    s.append(P("4. Overlay visual", h1))
    s.append(P(
        "O heatmap final passa por <code>cv2.applyColorMap(heatmap*255, COLORMAP_JET)</code> e e "
        "alfa-misturado com a imagem original (alpha=0.45). A bbox usada e desenhada em verde sobre o "
        "overlay para que o usuario veja exatamente o recorte considerado no calculo."
    ))

    s.append(P("5. Complexidade computacional", h1))
    s.append(boxed_table([
        ["Etapa", "Custo tipico CPU"],
        ["Preprocessing (resize + cvtColor)", "~5 ms"],
        ["Forward pass MobileNetV2", "~80-150 ms"],
        ["Backward pass (gradientes)", "~150-250 ms"],
        ["Resize do heatmap + ReLU + norm", "~3 ms"],
        ["Calculo AL/AFS", "~1 ms"],
        ["Overlay + encode PNG", "~30 ms"],
        ["<b>Total tipico</b>", "<b>300-450 ms</b>"],
    ], col_widths=[8 * cm, 8.5 * cm]))

    return s


# ============================================================================
# 04 - INTELIGENCIA ARTIFICIAL
# ============================================================================
def build_ia():
    s = cover("04 - Inteligencia Artificial", "Conceitos, dataset, treinamento e avaliacao")

    s.append(P("1. Aprendizado de maquina supervisionado", h1))
    s.append(P(
        "O AgroVision e um exemplo classico de <b>aprendizado supervisionado</b>: dispomos de pares "
        "(imagem, classe) rotulados, e a tarefa do modelo e aprender a mapear pixel &rarr; classe. O "
        "treinamento minimiza uma funcao de perda (cross-entropy categorica) sobre o conjunto de "
        "treinamento e a generalizacao e avaliada num conjunto de validacao mantido a parte."
    ))

    s.append(P("2. Redes neurais convolucionais (CNNs)", h1))
    s.append(P(
        "CNNs (LeCun et al., 1998) sao o estado-da-arte para visao computacional. Diferentemente de "
        "redes totalmente conectadas, elas exploram <b>localidade espacial</b> (filtros que olham "
        "vizinhancas pequenas) e <b>compartilhamento de pesos</b> (o mesmo filtro varre toda a imagem). "
        "Isso reduz drasticamente o numero de parametros e captura padroes invariantes a translacao "
        "(uma lesao em qualquer parte da folha e detectada da mesma forma)."
    ))

    s.append(P("3. Transfer Learning", h1))
    s.append(P(
        "Treinar uma CNN do zero requer milhoes de imagens. Quando o dataset alvo e pequeno (4.180 "
        "imagens, no nosso caso), aplicamos <b>transfer learning</b> (Pan &amp; Yang, 2009): "
        "carregamos pesos pre-treinados no ImageNet (1.2 milhoes de imagens de uso geral) e "
        "re-treinamos somente as ultimas camadas para nosso dominio especifico."
    ))

    s.append(P("4. Arquiteturas escolhidas", h1))

    s.append(P("4.1. ResNet50 (modelo principal de identificacao)", h2))
    s.append(P(
        "Proposta por He et al. (2016), introduziu o conceito de <b>conexoes residuais</b> "
        "(<code>output = F(x) + x</code>) que permitem treinar redes muito profundas (50 a 152 camadas) "
        "sem o problema do vanishing gradient. Treinada no Roboflow, atinge 95,8% de acuracia no nosso "
        "test set."
    ))

    s.append(P("4.2. MobileNetV2 (modelo de auditoria local)", h2))
    s.append(P(
        "Proposta por Sandler et al. (2018), foi desenhada para ambientes restritos (mobile, edge "
        "devices). Usa <b>inverted residuals</b> e <b>depthwise separable convolutions</b>, atingindo "
        "performance comparavel a ResNets com 10x menos parametros. Treinada localmente no Colab, "
        "fica em ~24 MB &mdash; cabe no plano Hobby do Railway."
    ))

    s.append(P("5. Dataset", h1))
    s.append(boxed_table([
        ["Atributo", "Valor"],
        ["Nome", "Corn-Maize Leaf Disease Dataset"],
        ["Origem", "PlantVillage (Hughes &amp; Salathe, 2015) curado pela PRMSU"],
        ["Distribuicao", "Roboflow Universe (workspace apscivil, projeto corn-maize-leaf-disease-kmpiq)"],
        ["Volume original", "4.186 imagens"],
        ["Apos augmentation", "~7.200 imagens"],
        ["Classes", "4 (Blight, Common_Rust, Gray_Leaf_Spot, Healthy)"],
        ["Split", "train / valid / test (padrao Roboflow)"],
        ["Resolucao", "224x224 apos preprocessing"],
        ["Licenca", "CC BY 4.0"],
    ], col_widths=[5 * cm, 11.5 * cm]))

    s.append(P("6. Treinamento", h1))
    s.append(P(
        "<b>Fase 1 (15 epocas, lr=1e-3):</b> base MobileNetV2 congelada, treina apenas a cabeca "
        "(GAP + Dropout + Dense). Aprende a separacao das 4 classes a partir das features genericas "
        "do ImageNet.<br/><br/>"
        "<b>Fase 2 (10 epocas, lr=1e-4):</b> destrava as ultimas 50 camadas da base, fine-tune com "
        "learning rate baixa. Refina os filtros para reconhecer padroes especificos de doenca foliar."
    ))

    s.append(P("7. Augmentation", h1))
    s.append(P("Sequencia aplicada apenas no treino (nao no modelo final exportado):", body))
    s.append(B("RandomFlip horizontal e vertical &mdash; modelo aprende independente da orientacao"))
    s.append(B("RandomRotation(0.25) &mdash; folhas no campo nao estao sempre retas"))
    s.append(B("RandomZoom(0.15) &mdash; distancia variavel da camera"))
    s.append(B("RandomTranslation(0.1, 0.1) &mdash; enquadramento imperfeito"))
    s.append(B("RandomBrightness(0.2) &mdash; luz natural varia ao longo do dia"))
    s.append(B("RandomContrast(0.2) &mdash; idem"))

    s.append(P("8. Avaliacao", h1))
    s.append(P(
        "Metricas principais: <b>acuracia</b> (proporcao de acertos sobre o test set), <b>val_loss</b> "
        "ao longo do treino (monitor de overfitting). Para uso clinico real seriam necessarias tambem "
        "metricas por classe (precision, recall, F1) e matriz de confusao."
    ))

    return s


# ============================================================================
# 05 - VISAO COMPUTACIONAL
# ============================================================================
def build_visao():
    s = cover("05 - Visao Computacional", "Fundamentos de processamento de imagem usados no projeto")

    s.append(P("1. O que e visao computacional", h1))
    s.append(P(
        "Visao Computacional (VC) e o campo que estuda como extrair informacao significativa de imagens "
        "ou videos digitais. Distingue-se de <i>image processing</i> (que apenas transforma uma imagem "
        "em outra) porque o objetivo final e <b>compreensao</b>: identificar objetos, segmentar regioes, "
        "rastrear movimento. No AgroVision, VC e usada em duas frentes: preprocessamento das imagens "
        "para o modelo, e geracao da mascara binaria que delimita a regiao de interesse para AL/AFS."
    ))

    s.append(P("2. Imagem como tensor", h1))
    s.append(P(
        "Para um computador, uma imagem RGB e simplesmente um tensor 3D de formato <code>(altura, "
        "largura, canais)</code>, com valores inteiros 0-255 (uint8) ou float em [0,1] / [-1,1]. No "
        "AgroVision uma imagem capturada e tipicamente algo como (3000, 4000, 3); apos preprocessing "
        "vira (224, 224, 3) com valores [-1, 1] (espaco esperado pelo MobileNetV2)."
    ))

    s.append(P("3. Espacos de cor", h1))
    s.append(boxed_table([
        ["Espaco", "Descricao", "Uso no projeto"],
        ["RGB", "Padrao para exibicao em telas", "Saida do PIL.Image, entrada do modelo apos cvtColor"],
        ["BGR", "Ordem invertida do RGB, padrao do OpenCV", "Uso interno em cv2.imread, cv2.imencode"],
        ["HSV", "Matiz, Saturacao, Valor", "Usado na segmentacao verde (mask.py)"],
    ], col_widths=[2 * cm, 7 * cm, 7.5 * cm]))

    s.append(P("4. Operacoes basicas no projeto", h1))
    s.append(P("<b>Resize</b> (cv2.resize com INTER_AREA): downscale preservando energia &mdash; ideal para reducao.", body))
    s.append(P("<b>Color conversion</b> (cv2.cvtColor): troca entre espacos de cor.", body))
    s.append(P("<b>Padding com proporcao</b> (PIL.ImageOps.expand): redimensiona mantendo aspect ratio e preenche com branco.", body))
    s.append(P("<b>Threshold + morfologia</b> (cv2.inRange, cv2.morphologyEx): usado na segmentacao verde para limpar a mascara.", body))
    s.append(P("<b>Color map</b> (cv2.applyColorMap COLORMAP_JET): converte heatmap monocromatico para representacao em cores quentes-frias.", body))
    s.append(P("<b>Alpha blending</b> (cv2.addWeighted): sobrepoe o heatmap colorido a imagem original com transparencia.", body))

    s.append(P("5. Segmentacao por cor (mask.py)", h1))
    s.append(P(
        "A funcao <code>green_segmentation_bbox</code> e um classico exemplo de VC nao-aprendida: "
        "converte para HSV, aplica threshold no canal H (matiz) na faixa do verde (25-95), faz opening "
        "+ closing para remover ruido, e usa <code>connectedComponentsWithStats</code> para achar o "
        "maior blob conectado. Retorna o bounding box desse blob como ROI alternativa para o calculo "
        "de AL/AFS quando o enquadramento padrao fixo nao serve."
    ))

    s.append(P("6. Augmentation: VC para gerar dados sinteticos", h1))
    s.append(P(
        "As tecnicas de augmentation usadas no treinamento sao todas operacoes classicas de VC "
        "aplicadas de forma randomizada: flip, rotation, zoom, translation, brightness, contrast. O "
        "objetivo e ensinar o modelo que essas transformacoes <i>nao mudam a classe</i> &mdash; uma "
        "folha rotacionada 30 graus ainda e a mesma folha."
    ))

    return s


# ============================================================================
# 06 - INTERFACE
# ============================================================================
def build_interface():
    s = cover("06 - Interface", "Design, UX e organizacao visual do aplicativo")

    s.append(P("1. Filosofia de design", h1))
    s.append(P(
        "O AgroVision adota uma estetica <b>mobile-first agricola</b>: cores naturais (verde como "
        "primary), tipografia generosa, espacamento confortavel, foco no conteudo e nao em ornamentos. "
        "A premissa e que o usuario pode estar usando o app em plena luz solar do campo, com luvas, "
        "rapidamente &mdash; entao tudo precisa ser legivel, tocavel e auto-explicativo."
    ))

    s.append(P("2. Paleta de cores", h1))
    s.append(boxed_table([
        ["Token", "Hex", "Uso"],
        ["PRIMARY", "#2D7A4F", "Verde principal &mdash; botoes, destaques"],
        ["PRIMARY_DARK", "#1C3D29", "Sombras de elevacao do PRIMARY"],
        ["SURFACE", "#FFFFFF", "Fundo de cards"],
        ["SURFACE_2", "#F3F7F2", "Fundo neutro de secoes"],
        ["TEXT_PRIMARY", "#1F2A1F", "Texto principal"],
        ["TEXT_SECONDARY", "#5C6B5C", "Texto secundario, labels"],
        ["SUCCESS", "#2D7A4F", "AFS alto, status OK"],
        ["WARNING", "#F57C00", "AFS medio, alerta"],
        ["DANGER", "#D32F2F", "AFS baixo, erro critico"],
        ["BORDER", "#D7E1D8", "Bordas de cards e divisores"],
    ], col_widths=[4 * cm, 3 * cm, 9.5 * cm]))

    s.append(P("3. Tipografia", h1))
    s.append(P(
        "Escala definida em <code>src/utils/constants.ts</code> via tokens FONT_XS (10pt), FONT_SM "
        "(13pt), FONT_BASE (15pt), FONT_LG (17pt), FONT_XL (22pt), FONT_2XL (28pt). Fonte padrao do "
        "sistema operacional &mdash; reduz peso de bundle e usa kerning otimizado para cada SO."
    ))

    s.append(P("4. Estrutura de telas", h1))
    s.append(boxed_table([
        ["Tela", "Funcao"],
        ["HomeScreen", "Ponto de entrada; cartao principal 'Identificar Especie'"],
        ["CameraScreen", "Captura de foto (expo-camera)"],
        ["ResultScreen", "Resultado da identificacao + descricao + recomendacoes"],
        ["AuditarModeloScreen", "Grad-CAM + AL/AFS + texto explicativo dinamico"],
        ["InstitucionalScreen", "Sobre o projeto, contato, referencias"],
    ], col_widths=[5 * cm, 11.5 * cm]))

    s.append(P("5. Componentes reutilizaveis", h1))
    s.append(B("<b>SafeAreaWrapper</b>: respeita notch e barra de status em iOS/Android"))
    s.append(B("<b>Header</b>: cabecalho com botao voltar e titulo"))
    s.append(B("<b>Button, Card, LoadingSpinner, ErrorBanner, ImagePreview</b>: blocos visuais comuns"))
    s.append(B("<b>HeatmapOverlay</b>: imagem com toggle 'Ver original'"))
    s.append(B("<b>MetricsPanel</b>: card com AFS/AL e barra colorida"))
    s.append(B("<b>AuditExplanation</b>: texto dinamico de interpretacao dos resultados"))

    s.append(P("6. Hierarquia visual", h1))
    s.append(P(
        "Cada tela segue o padrao: <b>(1) cabecalho</b> com titulo e voltar, <b>(2) bloco de "
        "imagem</b> (foto ou heatmap), <b>(3) bloco de resultado</b> em destaque com confianca, "
        "<b>(4) blocos de informacao</b> em cards menores, <b>(5) botoes de acao</b> no rodape. "
        "Essa hierarquia mantem o usuario sempre orientado independente da tela."
    ))

    return s


# ============================================================================
# 07 - XAI E GRAD-CAM
# ============================================================================
def build_xai():
    s = cover("07 - XAI e Grad-CAM", "Selvaraju et al. (2017) e referencias cientificas")

    s.append(P("1. O que e XAI", h1))
    s.append(P(
        "<b>Explainable Artificial Intelligence (XAI)</b> e um sub-campo da IA dedicado a tornar as "
        "decisoes de modelos de aprendizado de maquina compreensiveis para humanos. O problema surge "
        "porque redes neurais profundas tem milhoes de parametros que interagem de forma nao-linear "
        "&mdash; e impossivel inferir o comportamento do modelo apenas olhando seus pesos."
    ))
    s.append(P(
        "Adadi &amp; Berrada (2018) sintetizam tres perguntas centrais que XAI busca responder: "
        "(1) Por que o modelo decidiu desse jeito? (2) Como ele decidiria diferente? (3) Quando ele "
        "erra sistematicamente? O AgroVision foca na pergunta (1) usando uma tecnica gradient-based."
    ))

    s.append(P("2. Taxonomia das tecnicas XAI", h1))
    s.append(boxed_table([
        ["Dimensao", "Opcoes", "Onde o Grad-CAM se encaixa"],
        ["Tempo", "Intrinseca / Post-hoc", "Post-hoc (aplicada depois do treino)"],
        ["Escopo", "Global / Local", "Local (uma predicao por vez)"],
        ["Generalidade", "Specific / Agnostic", "Specific (so funciona em CNNs)"],
        ["Base", "Gradient / Perturbation / Attention", "Gradient-based"],
    ], col_widths=[3 * cm, 5.5 * cm, 8 * cm]))

    s.append(P("3. CAM &mdash; precursor (Zhou et al., 2016)", h1))
    s.append(P(
        "<b>Class Activation Mapping</b>: a ideia original. Funcionava apenas para arquiteturas que "
        "terminavam em Global Average Pooling (GAP) + Dense. Para uma classe c, o CAM e a media "
        "ponderada das ativacoes da ultima camada conv pelos pesos do Dense correspondentes a c."
    ))
    s.append(P("CAM = &Sigma;_k w_k^c &middot; A^k", formula))
    s.append(P("Limitacao: nao funcionava em redes sem GAP no final, como VGG ou redes com fully-connected layers."))

    s.append(P("4. Grad-CAM &mdash; generalizacao (Selvaraju et al., 2017)", h1))
    s.append(P(
        "Selvaraju et al., no paper publicado no ICCV 2017, propuseram substituir os pesos do Dense "
        "(que so existem em arquiteturas com GAP no final) pelos <b>gradientes do score da classe em "
        "relacao aos feature maps</b>. Isso torna a tecnica aplicavel a qualquer CNN, "
        "independente da arquitetura terminal."
    ))
    s.append(P("alpha_k^c = (1/Z) &Sigma;_i &Sigma;_j (&part;y^c / &part;A^k(i,j))", formula))
    s.append(P("L_GradCAM^c = ReLU( &Sigma;_k alpha_k^c &middot; A^k )", formula))
    s.append(P(
        "O ReLU descarta contribuicoes negativas (pixels que <i>reduziriam</i> a confianca da classe)."
    ))

    s.append(P("5. Por que escolhemos Grad-CAM e nao outras tecnicas", h1))
    s.append(boxed_table([
        ["Tecnica", "Forca", "Por que nao no AgroVision"],
        ["LIME", "Model-agnostic, intuitiva", "Lenta: faz milhares de perturbacoes por imagem"],
        ["SHAP", "Base teorica solida (Shapley)", "Caro computacionalmente, melhor para tabular"],
        ["RISE", "Boa para black-box", "Requer 4000+ forward passes &mdash; inviavel mobile"],
        ["Integrated Gradients", "Atribuicoes pixel-a-pixel", "Mapas ruidosos em CNNs profundas"],
        ["Grad-CAM", "1 forward + 1 backward, rapido", "<b>Escolhido</b>"],
    ], col_widths=[3 * cm, 5 * cm, 8.5 * cm]))

    s.append(P("6. Implementacao no projeto", h1))
    s.append(P(
        "Arquivo: <code>api/xai/gradcam.py</code>. Funcao principal: <code>generate_gradcam()</code>. "
        "Usa <code>tf.GradientTape()</code> para gravar o forward pass, extrai gradientes via "
        "<code>tape.gradient()</code>, faz pooling com <code>tf.reduce_mean</code>, combina com "
        "<code>tf.reduce_sum</code> + ReLU e normaliza. Camada-alvo padrao: <b>Conv_1</b> (ultima "
        "conv do MobileNetV2 antes do GAP), tamanho espacial 7x7. Upsample bilinear para 224x224 e "
        "depois para a resolucao original da imagem."
    ))

    s.append(P("7. Referencias bibliograficas centrais", h1))
    s.append(P("<b>Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., &amp; Batra, D.</b> "
               "(2017). Grad-CAM: Visual Explanations from Deep Networks via Gradient-based "
               "Localization. <i>Proceedings of the IEEE International Conference on Computer "
               "Vision (ICCV)</i>, 618-626.", body))
    s.append(P("<b>Zhou, B., Khosla, A., Lapedriza, A., Oliva, A., &amp; Torralba, A.</b> (2016). "
               "Learning Deep Features for Discriminative Localization. <i>CVPR 2016</i>, 2921-2929.", body))
    s.append(P("<b>Adadi, A., &amp; Berrada, M.</b> (2018). Peeking Inside the Black-Box: A Survey on "
               "Explainable Artificial Intelligence (XAI). <i>IEEE Access</i>, 6, 52138-52160.", body))
    s.append(P("<b>Ribeiro, M. T., Singh, S., &amp; Guestrin, C.</b> (2016). \"Why Should I Trust You?\": "
               "Explaining the Predictions of Any Classifier (LIME). <i>KDD 2016</i>.", body))
    s.append(P("<b>Lundberg, S., &amp; Lee, S.-I.</b> (2017). A Unified Approach to Interpreting Model "
               "Predictions (SHAP). <i>NeurIPS 2017</i>.", body))

    return s


# ============================================================================
# 08 - AL e AFS
# ============================================================================
def build_al_afs():
    s = cover("08 - AL e AFS", "Intervencao cientifica do AgroVision &mdash; metricas quantitativas de auditoria")

    s.append(P("1. O problema que motivou as metricas", h1))
    s.append(P(
        "O Grad-CAM puro produz um mapa de calor &mdash; uma imagem que o ser humano olha e "
        "interpreta. Esse e seu maior valor (clareza visual) e tambem sua maior limitacao "
        "(<b>e qualitativo</b>). Para o AgroVision, queriamos algo que pudesse:"
    ))
    s.append(B("Quantificar a qualidade da explicacao em um numero (entre 0 e 1)"))
    s.append(B("Permitir comparar varias predicoes (\"esta foto teve auditoria melhor que aquela\")"))
    s.append(B("Servir de gatilho para alertas automaticos (\"AL alto demais, recapture a imagem\")"))
    s.append(B("Ser calculavel em tempo real (milissegundos) e nao requerer ground-truth anotado"))

    s.append(P("2. Definicoes", h1))

    s.append(P("2.1. Attention Leakage (AL)", h2))
    s.append(P(
        "Fracao da atencao do modelo que ficou <b>fora</b> da regiao de interesse (ROI). Alto AL = "
        "modelo \"vazou\" atencao para fundo/sombra/bordas. Baixo AL = modelo focado."
    ))
    s.append(P("AL = &Sigma;(H_tau &middot; (1 - M)) / &Sigma;(H_tau)", formula))

    s.append(P("2.2. Attention Focus Score (AFS)", h2))
    s.append(P("Complemento do AL. Mede a fracao de atencao <b>dentro</b> da ROI. Quanto maior, melhor."))
    s.append(P("AFS = 1 - AL = &Sigma;(H_tau &middot; M) / &Sigma;(H_tau)", formula))

    s.append(P("Onde:", body))
    s.append(P(
        "H = heatmap do Grad-CAM normalizado para [0, 1]<br/>"
        "H_tau = heatmap apos aplicar threshold tau (zera pixels com valor &lt; tau)<br/>"
        "M = mascara binaria da ROI (1 dentro da bbox, 0 fora)",
        code,
    ))

    s.append(P("3. Por que aplicar threshold antes", h1))
    s.append(P(
        "Sem o threshold, pixels com ativacao muito baixa (0.02, 0.05 &mdash; ruido) "
        "contaminam a soma. Aplicando tau (padrao 0.5), so contam pixels com ativacao significativa. "
        "Isso torna a metrica mais robusta e interpretavel: \"de toda a atencao <i>relevante</i> do "
        "modelo, quanto ficou dentro da folha?\""
    ))

    s.append(P("4. Estrategias de bounding box", h1))
    s.append(boxed_table([
        ["Estrategia", "Como funciona", "Quando usar"],
        ["fixed (padrao)", "Bbox centralizada cobrindo 80% da imagem", "Padrao, assume enquadramento decente"],
        ["green", "Segmenta verde em HSV e usa bbox do maior blob", "Folha descentralizada ou em fundo cheio"],
        ["manual", "Usuario informa (x,y,w,h)", "Modo cientifico, anotacao precisa"],
    ], col_widths=[3 * cm, 7 * cm, 6.5 * cm]))

    s.append(P("5. Casos praticos (interpretacao)", h1))

    s.append(P("5.1. Caso A &mdash; modelo focado, classe correta", h3))
    s.append(P(
        "AFS = 92%, AL = 8%, predicao = Common_Rust (99%). Heatmap concentrado sobre as pustulas "
        "da ferrugem. <b>Interpretacao:</b> aprendizado correto; o modelo realmente esta vendo o "
        "patogeno. Decisao de manejo (aplicar fungicida) confiavel."
    ))

    s.append(P("5.2. Caso B &mdash; classe correta com atencao dispersa", h3))
    s.append(P(
        "AFS = 51%, AL = 49%, predicao = Common_Rust (99%). Heatmap se espalha pela folha e tambem "
        "bordas/fundo. <b>Interpretacao:</b> diagnostico provavelmente correto, mas o modelo usou "
        "contexto. Util &mdash; mas uma foto mais limpa aumentaria a confianca."
    ))

    s.append(P("5.3. Caso C &mdash; modelo \"acertou por sorte\"", h3))
    s.append(P(
        "AFS = 25%, AL = 75%, predicao = Healthy (87%). Heatmap em canto da imagem, fora da folha. "
        "<b>Interpretacao:</b> classico exemplo de <b>shortcut learning</b> (Geirhos et al., 2020). "
        "A predicao pode ate estar correta, mas o modelo nao se baseou na folha. Sistema deve "
        "<b>desconfiar</b> da resposta apesar da confianca alta."
    ))

    s.append(P("5.4. Caso D &mdash; modelo errado e atencao errada", h3))
    s.append(P(
        "AFS = 18%, AL = 82%, predicao = Blight (65%) com folha saudavel. Heatmap sobre uma sombra. "
        "<b>Interpretacao:</b> falha clara &mdash; confundiu sombra com lesao. AL muito alto + "
        "confianca media = forte sinal de descartar e recapturar."
    ))

    s.append(P("6. Tabela de interpretacao usada no app", h1))
    s.append(boxed_table([
        ["Faixa AFS", "Rotulo", "Acao sugerida"],
        ["&ge; 70%", "Atencao focada", "Diagnostico confiavel"],
        ["40% - 70%", "Atencao moderada", "Aceitar com cautela; recapturar daria mais robustez"],
        ["&lt; 40%", "Atencao dispersa", "Recomendar recapturar"],
    ], col_widths=[3 * cm, 4 * cm, 9.5 * cm]))

    s.append(P("7. Relacao com metricas tradicionais", h1))
    s.append(P(
        "Existem na literatura metricas relacionadas: <b>Pointing Game</b> (Zhang et al., 2018) que "
        "mede se o pixel de maior ativacao esta dentro da ROI; <b>Deletion/Insertion</b> (Petsiuk et "
        "al., 2018) que mede degradacao iterativa da confianca; <b>IoU</b> para regioes de saliencia "
        "binarizadas. AL/AFS sao mais simples porque dependem apenas de uma soma ponderada &mdash; "
        "vantagem para uso embarcado em tempo real."
    ))

    s.append(P("8. Limitacoes conhecidas", h1))
    s.append(B("<b>Sensivel a definicao da bbox</b>: bbox muito apertada subestima AFS; muito larga superestima."))
    s.append(B("<b>Nao considera distribuicao espacial</b>: dois heatmaps com mesmo AFS mas formas diferentes (concentrado vs disperso dentro da ROI) sao tratados como iguais."))
    s.append(B("<b>Threshold tau e arbitrario</b>: 0.5 e razoavel mas nao otimo para todas as classes. Trabalho futuro: tau adaptativo por classe."))
    s.append(B("<b>Depende do Grad-CAM</b>: se o Grad-CAM for ruim (camada errada), AL/AFS sao ruidosos."))

    s.append(P("9. Contribuicao original do TCC", h1))
    s.append(P(
        "AL e AFS sao apresentadas como uma <b>intervencao cientifica original do AgroVision</b>: "
        "combinacao simples e interpretavel de duas tecnicas conhecidas (Grad-CAM + mascara binaria) "
        "para gerar metricas quantitativas operacionalmente uteis em campo. A defesa do TCC deve "
        "enfatizar dois pontos: (a) a metrica e <b>matematicamente correta</b> e bem definida; "
        "(b) ela <b>resolve um problema pratico</b> (gatilho automatico de recaptura) que metricas "
        "academicas tradicionais nao resolvem por serem caras de computar."
    ))

    return s


# ============================================================================
# 09 - REACT NATIVE APLICADO
# ============================================================================
def build_react():
    s = cover("09 - React Native Aplicado", "Stack mobile, libs, estrutura e patterns")

    s.append(P("1. Por que React Native e Expo", h1))
    s.append(P(
        "<b>React Native</b> permite escrever uma unica base de codigo TypeScript que roda nativamente "
        "em iOS e Android. <b>Expo</b> e um framework sobre o RN que prove um conjunto curado de APIs "
        "(camera, file system, sharing, sqlite) e um workflow de desenvolvimento sem precisar "
        "compilar Android Studio/Xcode localmente para a maior parte das tarefas."
    ))

    s.append(P("2. Estrutura de pastas", h1))
    s.append(P(
        "src/<br/>"
        "&nbsp;&nbsp;screens/         &mdash; telas (HomeScreen, ResultScreen, AuditarModeloScreen, ...)<br/>"
        "&nbsp;&nbsp;components/      &mdash; componentes reutilizaveis<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;ui/         &mdash; primitivos (Button, Card, LoadingSpinner)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;common/     &mdash; layout (SafeAreaWrapper, Header)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;xai/        &mdash; especificos da auditoria (HeatmapOverlay, MetricsPanel, AuditExplanation)<br/>"
        "&nbsp;&nbsp;services/        &mdash; integracao externa<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;ml/         &mdash; classifyService, xaiService (chamadas WebSocket)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;storage/    &mdash; databaseService (SQLite)<br/>"
        "&nbsp;&nbsp;context/         &mdash; AnalysisContext, AppContext<br/>"
        "&nbsp;&nbsp;hooks/           &mdash; useCamera, useAnalysis, ...<br/>"
        "&nbsp;&nbsp;models/          &mdash; tipos TypeScript<br/>"
        "&nbsp;&nbsp;navigation/      &mdash; configuracao do React Navigation<br/>"
        "&nbsp;&nbsp;utils/           &mdash; constants, logger, format",
        code,
    ))

    s.append(P("3. Libs principais e por que estao no projeto", h1))
    s.append(boxed_table([
        ["Lib", "Versao", "Funcao"],
        ["expo", "~52", "Framework principal"],
        ["react-native", "0.76+", "Runtime mobile"],
        ["typescript", "~5.x", "Tipagem estatica"],
        ["@react-navigation/native", "~7", "Navegacao entre telas"],
        ["@react-navigation/native-stack", "~7", "Stack de navegacao (push/pop)"],
        ["expo-camera", "~16", "Acesso a camera nativa"],
        ["expo-file-system", "~17", "Leitura/escrita de arquivos, base64"],
        ["expo-sqlite", "~14", "Banco de dados local"],
        ["expo-sharing", "~12", "Share nativo (iOS/Android)"],
        ["expo-image-picker", "~16", "Selecao de imagem da galeria"],
        ["axios", "~1.x", "Cliente HTTP (chamadas REST de fallback)"],
    ], col_widths=[5 * cm, 2.5 * cm, 9 * cm]))

    s.append(P("4. Padroes adotados", h1))

    s.append(P("4.1. Functional components + hooks", h2))
    s.append(P(
        "Nenhum componente de classe. Todo state usa <code>useState</code>, side effects "
        "<code>useEffect</code>, derivacoes <code>useMemo</code>, callbacks estaveis "
        "<code>useCallback</code>. Padrao moderno do React (post 2019)."
    ))

    s.append(P("4.2. Context API para estado global", h2))
    s.append(P(
        "<code>AnalysisContext</code> (em <code>src/context/AnalysisContext.tsx</code>) mantem o "
        "estado da analise em curso (foto, resultado, erro, loading). Implementado com "
        "<code>useReducer</code>, exposto via Provider envolvendo o app. Telas consomem com o hook "
        "<code>useAnalysisContext</code>."
    ))

    s.append(P("4.3. Path aliases", h2))
    s.append(P(
        "<code>tsconfig.json</code> define aliases (@components, @screens, @services, @utils, "
        "@models) para evitar imports relativos longos. Configurado via "
        "<code>babel-plugin-module-resolver</code>."
    ))

    s.append(P("4.4. Strict TypeScript", h2))
    s.append(P(
        "Modo strict ativo: <code>strictNullChecks</code>, <code>noImplicitAny</code>. Todas as "
        "interfaces de payload (ClassifyResult, XAIResult, Analysis) estao em <code>src/models/</code>."
    ))

    s.append(P("5. Comunicacao com o backend", h1))
    s.append(P(
        "Dois servicos cuidam disso:<br/>"
        "<b>classifyService.ts</b>: abre WebSocket em <code>/ws/classify</code>, envia imagem em "
        "base64, escuta eventos de progresso e resultado.<br/>"
        "<b>xaiService.ts</b>: idem para <code>/ws/gradcam</code>. Tem variante REST de fallback."
    ))

    s.append(P("6. Persistencia local", h1))
    s.append(P(
        "<code>databaseService</code> e um singleton inicializado no startup do app (em "
        "<code>App.tsx</code>). Cria as tabelas se nao existem, expoe metodos assincronos. Cada "
        "operacao de IO usa <code>execAsync</code> ou <code>getAllAsync</code> do expo-sqlite."
    ))

    return s


# ============================================================================
# 10 - BACKEND / INFRA
# ============================================================================
def build_backend():
    s = cover("10 - Backend / Infra", "FastAPI, Uvicorn, Railway e Roboflow Serverless")

    s.append(P("1. Stack do backend", h1))
    s.append(boxed_table([
        ["Camada", "Tecnologia", "Versao"],
        ["Framework web", "FastAPI", "0.110"],
        ["Servidor ASGI", "Uvicorn (com uvloop)", "0.29"],
        ["ML runtime", "TensorFlow (CPU)", "2.20.0"],
        ["Keras", "Keras 3 nativo", "3.13.2"],
        ["Visao computacional", "OpenCV (headless)", "4.8"],
        ["Numerica", "NumPy", "1.26"],
        ["HTTP client", "requests", "2.31"],
        ["Imagem", "Pillow", "10.1"],
        ["Python runtime", "CPython", "3.12"],
    ], col_widths=[4 * cm, 7.5 * cm, 5 * cm]))

    s.append(P("2. Por que FastAPI", h1))
    s.append(P(
        "FastAPI foi escolhida sobre Flask pelo suporte nativo a <b>async/await</b>, <b>WebSocket</b> "
        "(o Grad-CAM precisa de progresso em tempo real) e <b>validacao automatica de schemas</b> via "
        "Pydantic. Tambem gera automaticamente documentacao Swagger em /docs, util durante o "
        "desenvolvimento."
    ))

    s.append(P("3. Endpoints", h1))
    s.append(boxed_table([
        ["Rota", "Tipo", "Funcao"],
        ["/api/health", "GET", "Healthcheck + metadata do modelo"],
        ["/ws/classify", "WS", "Classificacao (Roboflow) com progresso"],
        ["/ws/gradcam", "WS", "Grad-CAM + AL/AFS com progresso"],
        ["/api/xai/gradcam", "POST", "Mesma funcao do WS, multipart/form-data (fallback)"],
    ], col_widths=[4.5 * cm, 2 * cm, 10 * cm]))

    s.append(P("4. Fluxo de uma requisicao WebSocket", h1))
    s.append(P(
        "1. Cliente abre WS com <code>?api_key=...</code>.<br/>"
        "2. Backend valida a chave. Se invalida, fecha com codigo 4003.<br/>"
        "3. Cliente envia primeira mensagem JSON com <code>image_b64</code> e parametros.<br/>"
        "4. Backend emite eventos {<i>preprocessing, classifying / building_model, computing_gradients, "
        "rendering_overlay, done</i>} com <code>pct</code>.<br/>"
        "5. Backend executa a operacao em threadpool (TF nao e async-friendly).<br/>"
        "6. Backend emite {<i>result, data</i>} com o payload final.<br/>"
        "7. Fecha o WS.",
        code,
    ))

    s.append(P("5. Autenticacao", h1))
    s.append(P(
        "Header <code>X-API-Key</code> (REST) ou query param <code>?api_key=...</code> (WS). A chave "
        "esperada vem da variavel de ambiente <code>AGROVISION_API_KEY</code> no Railway. Se a "
        "variavel nao estiver setada (ambiente local), o backend roda sem autenticacao."
    ))

    s.append(P("6. Roboflow Serverless", h1))
    s.append(P(
        "O backend funciona como <b>proxy</b> para o Roboflow Serverless quando "
        "<code>ROBOFLOW_API_KEY</code> e <code>ROBOFLOW_MODEL_ID</code> estao configurados. Fluxo "
        "interno em <code>_classify_sync</code>:"
    ))
    s.append(P(
        "1. Recebe bytes da imagem.<br/>"
        "2. Redimensiona para 640px no maior lado (evita erro 413 de payload muito grande).<br/>"
        "3. Encode em base64.<br/>"
        "4. POST para <code>https://serverless.roboflow.com/{slug}/{version}?api_key=...</code>.<br/>"
        "5. Parse do JSON, extrai top-1 prediction.<br/>"
        "6. Retorna {prediction, confidence, source: 'roboflow'}.",
        code,
    ))

    s.append(P("7. Deployment no Railway", h1))
    s.append(P(
        "<b>Build system:</b> Nixpacks (deteccao automatica de Python pelos arquivos "
        "<code>requirements.txt</code> + <code>runtime.txt</code>).<br/><br/>"
        "<b>Arquivos de config:</b><br/>"
        "&middot; <code>Procfile</code> &mdash; comando de start<br/>"
        "&middot; <code>runtime.txt</code> &mdash; <code>python-3.12</code><br/>"
        "&middot; <code>nixpacks.toml</code> &mdash; fases customizadas de build<br/>"
        "&middot; <code>requirements.txt</code> &mdash; dependencias fixadas<br/><br/>"
        "<b>Plano:</b> Hobby (US$ 5/mes), inclui ~US$ 5 de uso. Para um TCC com baixo trafego e "
        "suficiente."
    ))

    s.append(P("8. Variaveis de ambiente", h1))
    s.append(boxed_table([
        ["Variavel", "Funcao"],
        ["ROBOFLOW_API_KEY", "Chave para a API serverless"],
        ["ROBOFLOW_MODEL_ID", "Slug do modelo no formato workspace/slug/version"],
        ["AGROVISION_API_KEY", "Chave compartilhada entre app e backend"],
        ["PORT", "Setada automaticamente pelo Railway"],
    ], col_widths=[5 * cm, 11.5 * cm]))

    s.append(P("9. Limites e observacoes operacionais", h1))
    s.append(B("<b>Cold start:</b> primeira requisicao apos inatividade demora ~10s (TF carrega o modelo)."))
    s.append(B("<b>Memoria:</b> TF 2.20 + Keras + modelo carregado consomem ~800 MB &mdash; cabe confortavelmente no plano Hobby (8 GB)."))
    s.append(B("<b>CPU:</b> uma inferencia + Grad-CAM gasta ~300-450 ms em CPU. Sem GPU, mas suficiente para uso interativo."))
    s.append(B("<b>Logs:</b> stdout via Uvicorn, visivel no dashboard do Railway em tempo real."))

    return s


# ============================================================================
# Build final
# ============================================================================
def make_pdf(filename, story):
    path = OUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"AgroVision - {filename}",
        author="Luiz Carlos Junior",
    )
    doc.build(story)
    print(f"OK -> {path.name}")


def main():
    make_pdf("01-Arquitetura-Completa.pdf", build_arquitetura())
    make_pdf("02-Banco-de-Dados.pdf", build_banco())
    make_pdf("03-Algoritmo.pdf", build_algoritmo())
    make_pdf("04-Inteligencia-Artificial.pdf", build_ia())
    make_pdf("05-Visao-Computacional.pdf", build_visao())
    make_pdf("06-Interface.pdf", build_interface())
    make_pdf("07-XAI-e-GradCAM.pdf", build_xai())
    make_pdf("08-AL-e-AFS.pdf", build_al_afs())
    make_pdf("09-React-Native-Aplicado.pdf", build_react())
    make_pdf("10-Backend-Infra.pdf", build_backend())
    print(f"\nTodos os PDFs em: {OUT_DIR}")


if __name__ == "__main__":
    main()
