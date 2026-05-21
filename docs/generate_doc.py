"""
Gera o documento de estudo completo do AgroVision (PDF).
Rodar: python docs/generate_doc.py
Saida: AgroVision_Documentacao_Completa.pdf na raiz do projeto.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_PATH = Path(__file__).resolve().parent.parent / "AgroVision_Documentacao_Completa.pdf"

# ============================================================================
# Estilos
# ============================================================================
styles = getSampleStyleSheet()

PRIMARY = colors.HexColor("#2D7A4F")
SECONDARY = colors.HexColor("#1C3D29")
TEXT = colors.HexColor("#1F2A1F")
SOFT = colors.HexColor("#5C6B5C")
BG_LIGHT = colors.HexColor("#F3F7F2")
BORDER = colors.HexColor("#D7E1D8")

title_style = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontSize=28,
    leading=34,
    alignment=TA_CENTER,
    textColor=PRIMARY,
    spaceAfter=18,
)

subtitle_style = ParagraphStyle(
    "SubtitleCustom",
    parent=styles["Normal"],
    fontSize=14,
    leading=18,
    alignment=TA_CENTER,
    textColor=SOFT,
    spaceAfter=8,
)

h1 = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=20,
    leading=26,
    textColor=PRIMARY,
    spaceBefore=20,
    spaceAfter=12,
)

h2 = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=15,
    leading=20,
    textColor=SECONDARY,
    spaceBefore=14,
    spaceAfter=8,
)

h3 = ParagraphStyle(
    "H3",
    parent=styles["Heading3"],
    fontSize=12,
    leading=16,
    textColor=SECONDARY,
    spaceBefore=10,
    spaceAfter=6,
)

body = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontSize=10.5,
    leading=15.5,
    alignment=TA_JUSTIFY,
    textColor=TEXT,
    spaceAfter=8,
)

bullet = ParagraphStyle(
    "BulletCustom",
    parent=body,
    leftIndent=18,
    bulletIndent=4,
    spaceAfter=4,
)

code = ParagraphStyle(
    "Code",
    parent=styles["Code"],
    fontSize=9,
    leading=12,
    textColor=SECONDARY,
    leftIndent=10,
    backColor=BG_LIGHT,
    borderColor=BORDER,
    borderWidth=0.5,
    borderPadding=6,
    spaceBefore=4,
    spaceAfter=8,
)

formula = ParagraphStyle(
    "Formula",
    parent=body,
    fontSize=11,
    leading=16,
    alignment=TA_CENTER,
    textColor=SECONDARY,
    spaceBefore=4,
    spaceAfter=8,
    backColor=BG_LIGHT,
    borderColor=BORDER,
    borderWidth=0.5,
    borderPadding=6,
)

caption = ParagraphStyle(
    "Caption",
    parent=body,
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
    textColor=SOFT,
    spaceAfter=10,
)


# ============================================================================
# Helpers
# ============================================================================
def P(text, style=body):
    return Paragraph(text, style)


def B(text):
    return P(f"&bull; &nbsp; {text}", bullet)


def boxed_table(rows, col_widths=None):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


# ============================================================================
# Conteudo
# ============================================================================
def build_story():
    s = []

    # --------------------------------------------------------------------
    # CAPA
    # --------------------------------------------------------------------
    s.append(Spacer(1, 6 * cm))
    s.append(P("AgroVision", title_style))
    s.append(P("Identificacao de Doencas Foliares do Milho com IA Auditavel", subtitle_style))
    s.append(Spacer(1, 1.5 * cm))
    s.append(
        P(
            "Documentacao tecnica e cientifica do projeto",
            ParagraphStyle("CapaInfo", parent=body, alignment=TA_CENTER, fontSize=12, textColor=SOFT),
        )
    )
    s.append(Spacer(1, 4 * cm))
    s.append(
        P(
            "Trabalho de Conclusao de Curso<br/>"
            "Engenharia de Software / Sistemas de Informacao<br/><br/>"
            "Luiz Carlos Junior &amp; Equipe AgroVision<br/>"
            "Maio de 2026",
            ParagraphStyle("Authors", parent=body, alignment=TA_CENTER, fontSize=11, textColor=TEXT, leading=18),
        )
    )
    s.append(PageBreak())

    # --------------------------------------------------------------------
    # SUMARIO EXECUTIVO
    # --------------------------------------------------------------------
    s.append(P("1. Sumario Executivo", h1))
    s.append(
        P(
            "O <b>AgroVision</b> e um aplicativo movel desenvolvido em React Native que utiliza "
            "Inteligencia Artificial para identificar doencas em folhas de milho (Zea mays L.) a partir de "
            "uma fotografia. O diferencial do projeto e a inclusao de uma <b>camada de auditoria visual</b> "
            "baseada em Grad-CAM e duas metricas quantitativas inspiradas em literatura de Explainable AI "
            "(XAI): <b>Attention Leakage (AL)</b> e <b>Attention Focus Score (AFS)</b>. Essas metricas "
            "permitem ao usuario nao apenas receber uma classificacao, mas tambem entender em quais regioes "
            "da folha o modelo se baseou para decidir e quanto dessa atencao esta efetivamente sobre a "
            "regiao de interesse."
        )
    )
    s.append(
        P(
            "O projeto cobre quatro classes-alvo: <b>Helmintosporiose</b> (Exserohilum turcicum), "
            "<b>Ferrugem-Comum</b> (Puccinia sorghi), <b>Mancha-Cinzenta</b> (Cercospora zeae-maydis) e "
            "<b>Milho Saudavel</b>. O backend de inferencia esta hospedado no Railway (FastAPI + WebSocket), "
            "com o modelo de identificacao servido pelo Roboflow Serverless API e o modelo de auditoria "
            "(Grad-CAM) executado localmente em TensorFlow/Keras 3."
        )
    )

    # --------------------------------------------------------------------
    # MOTIVACAO E CONTEXTO
    # --------------------------------------------------------------------
    s.append(P("2. Motivacao e Contexto", h1))

    s.append(P("2.1. O problema no campo", h2))
    s.append(
        P(
            "Doencas foliares causam perdas significativas na producao mundial de milho. Estudos da Embrapa "
            "indicam que doencas como ferrugem-comum, helmintosporiose e mancha-cinzenta podem reduzir a "
            "produtividade em ate 60% quando nao detectadas e tratadas no estagio inicial. O diagnostico "
            "tradicional depende de visita tecnica e inspecao visual presencial, o que e custoso e demorado "
            "para o pequeno e medio produtor."
        )
    )
    s.append(
        P(
            "Aplicativos baseados em redes neurais convolucionais (CNNs) ja foram propostos como solucao "
            "para esse problema. No entanto, a maioria oferece apenas o resultado da classificacao, sem "
            "permitir que o agricultor entenda <i>por que</i> o sistema chegou aquele diagnostico. Esse "
            "comportamento de \"caixa-preta\" gera desconfianca legitima por parte do usuario final, que "
            "muitas vezes precisa tomar decisoes financeiras (aplicar fungicida, replantar) com base "
            "naquele resultado."
        )
    )

    s.append(P("2.2. A dor que o AgroVision resolve", h2))
    s.append(
        P(
            "O AgroVision endereca tres dores especificas:"
        )
    )
    s.append(B("<b>Falta de transparencia</b> em modelos de IA agricola: o usuario nao consegue inspecionar a decisao do modelo."))
    s.append(B("<b>Dificuldade de validacao cientifica</b>: pesquisadores e tecnicos agronomicos precisam de metricas para avaliar se o modelo realmente \"olha o lugar certo\"."))
    s.append(B("<b>Limitacao do diagnostico remoto</b>: regioes rurais com pouca cobertura tecnica precisam de uma ferramenta de triagem confiavel antes de mobilizar um agronomo."))

    s.append(P("2.3. Idealizacao", h2))
    s.append(
        P(
            "A proposta nasceu da combinacao de dois conhecimentos: visao computacional aplicada e a "
            "necessidade pratica do agronegocio brasileiro de ferramentas de diagnostico foliar precisas e "
            "<b>explicaveis</b>. O recorte para milho foi escolhido por tres motivos: (i) e a segunda cultura "
            "mais produzida no Brasil; (ii) ha disponibilidade publica de datasets anotados de qualidade "
            "(PlantVillage e PRMSU); (iii) o numero reduzido de classes (4) permite que o estudo seja "
            "executavel no escopo de um TCC sem perder rigor cientifico."
        )
    )

    # --------------------------------------------------------------------
    # OBJETIVOS
    # --------------------------------------------------------------------
    s.append(P("3. Objetivos", h1))
    s.append(P("3.1. Objetivo geral", h2))
    s.append(
        P(
            "Desenvolver um sistema movel de identificacao de doencas foliares no milho que integre, alem da "
            "classificacao, uma camada de auditoria visual e quantitativa do modelo de IA, permitindo ao "
            "usuario validar a confiabilidade da resposta antes de agir."
        )
    )
    s.append(P("3.2. Objetivos especificos", h2))
    s.append(B("Construir um pipeline movel completo (captura -> classificacao -> diagnostico) usando arquitetura mobile-first."))
    s.append(B("Treinar e servir um modelo de classificacao de quatro classes (Blight, Common_Rust, Gray_Leaf_Spot, Healthy)."))
    s.append(B("Implementar Grad-CAM (Selvaraju et al., 2017) para geracao de mapas de saliencia visuais."))
    s.append(B("Definir e implementar as metricas Attention Leakage (AL) e Attention Focus Score (AFS) como instrumento de auditoria do modelo."))
    s.append(B("Garantir reprodutibilidade cientifica: dataset publico, codigo versionado, dependencias fixadas, modelo exportavel."))
    s.append(B("Oferecer uma experiencia de usuario simples o suficiente para ser usada em campo, sem treinamento previo."))

    s.append(PageBreak())

    # --------------------------------------------------------------------
    # STACK
    # --------------------------------------------------------------------
    s.append(P("4. Stack Tecnologica", h1))

    s.append(P("4.1. Frontend (app movel)", h2))
    s.append(boxed_table(
        [
            ["Camada", "Tecnologia", "Funcao"],
            ["UI/Runtime", "React Native (Expo SDK 52)", "Aplicativo iOS/Android single-codebase"],
            ["Linguagem", "TypeScript", "Tipagem estatica e contratos claros entre camadas"],
            ["Navegacao", "React Navigation (native-stack)", "Stack de telas: Home, Camera, Result, AuditarModelo"],
            ["Estado", "Context API (AnalysisContext)", "Gerenciamento de estado de analise em andamento"],
            ["Camera", "expo-camera", "Captura de foto em alta resolucao"],
            ["FS", "expo-file-system", "Leitura/escrita base64 e cache temporario"],
            ["Share", "expo-sharing", "Exportacao do heatmap pos-auditoria"],
            ["Storage local", "SQLite (expo-sqlite)", "Historico de analises offline"],
        ],
        col_widths=[3 * cm, 5 * cm, 8.5 * cm],
    ))

    s.append(P("4.2. Backend (servico de IA)", h2))
    s.append(boxed_table(
        [
            ["Camada", "Tecnologia", "Funcao"],
            ["API", "FastAPI 0.110 + Uvicorn", "REST + WebSocket para progresso em tempo real"],
            ["ML runtime", "TensorFlow 2.20 (CPU) + Keras 3.13", "Inferencia do modelo de auditoria"],
            ["Visao", "OpenCV (cv2)", "Pre-processamento, mascaras, overlay"],
            ["Numerica", "NumPy", "Operacoes sobre heatmaps e mascaras binarias"],
            ["Hospedagem", "Railway (Hobby plan)", "Container Linux com Python 3.12, deploy via Nixpacks"],
            ["Identificacao", "Roboflow Serverless API", "Modelo principal de classificacao"],
        ],
        col_widths=[3 * cm, 5 * cm, 8.5 * cm],
    ))

    s.append(P("4.3. Treinamento e dados", h2))
    s.append(boxed_table(
        [
            ["Recurso", "Detalhe"],
            ["Ambiente", "Google Colab (T4 GPU gratuita)"],
            ["Framework", "TensorFlow/Keras 3"],
            ["Dataset", "Corn-Maize-Leaf-Disease (PRMSU/PlantVillage) via Roboflow Universe"],
            ["Volume", "~4.180 imagens originais, 7.200 apos augmentation"],
            ["Classes", "4 (Blight, Common_Rust, Gray_Leaf_Spot, Healthy)"],
            ["Acuracia (Roboflow)", "95,8% no conjunto de teste"],
            ["Acuracia (Keras local)", "Aproximadamente 93-96% (varia por execucao)"],
        ],
        col_widths=[5 * cm, 11.5 * cm],
    ))

    # --------------------------------------------------------------------
    # ARQUITETURA
    # --------------------------------------------------------------------
    s.append(P("5. Arquitetura do Sistema", h1))
    s.append(
        P(
            "O sistema e dividido em tres camadas independentes que se comunicam por HTTPS/WSS. Essa "
            "separacao foi escolhida para permitir que cada camada evolua sem afetar as demais e para que o "
            "backend de IA pudesse ser servido em uma infraestrutura adequada (GPU/CPU dedicada), enquanto "
            "o app movel mantem-se leve."
        )
    )

    s.append(P("5.1. Diagrama de fluxo logico", h2))
    s.append(P(
        "<b>[Camera no celular]</b> --(captura JPEG)--> <b>[App React Native]</b> --(base64 via WebSocket)--> "
        "<b>[Backend FastAPI no Railway]</b> --(resize + base64)--> <b>[Roboflow Serverless]</b><br/><br/>"
        "Retorno: classificacao -&gt; usuario.<br/><br/>"
        "Quando o usuario clica em <b>Auditar Modelo</b>:<br/>"
        "<b>[App]</b> --(imagem base64)--> <b>[Backend]</b> --(forward pass + GradientTape)--> "
        "<b>[Keras local]</b> --(heatmap + AL/AFS)--> <b>[App]</b> --(render)--> usuario.",
        code,
    ))

    s.append(P("5.2. Por que dois modelos separados?", h2))
    s.append(
        P(
            "A API serverless do Roboflow expoe apenas o forward pass (predicao final), o que torna "
            "impossivel calcular gradientes em camadas intermediarias. Como o Grad-CAM exige acesso ao "
            "<b>tape de gradientes</b>, mantemos um segundo modelo Keras local (MobileNetV2 treinado no "
            "mesmo dataset) cuja unica funcao e gerar o heatmap. Os dois modelos sao da mesma familia, "
            "treinados no mesmo dataset, o que garante coerencia entre identificacao e auditoria."
        )
    )

    s.append(PageBreak())

    # --------------------------------------------------------------------
    # FLUXO DO USUARIO
    # --------------------------------------------------------------------
    s.append(P("6. Fluxo do Usuario no App", h1))

    s.append(P("6.1. Passo a passo", h2))
    s.append(B("<b>1. Home:</b> usuario abre o app e ve o cartao principal \"Identificar Especie\"."))
    s.append(B("<b>2. Camera:</b> ele captura uma foto da folha (preferencialmente em luz natural, sem sombras fortes)."))
    s.append(B("<b>3. Identificacao automatica:</b> o app envia a foto via WebSocket para o backend, que repassa ao Roboflow."))
    s.append(B("<b>4. Resultado:</b> a tela ResultScreen exibe nome da doenca em PT-BR, confianca, descricao patologica e recomendacoes de manejo."))
    s.append(B("<b>5. Auditoria (opcional):</b> usuario clica em \"Auditar Modelo (Grad-CAM)\" para validar cientificamente o resultado."))
    s.append(B("<b>6. Visualizacao:</b> a tela AuditarModelo mostra heatmap sobreposto a imagem, AFS, AL, tempo de processamento e camada usada."))
    s.append(B("<b>7. Salvar/Exportar:</b> usuario pode rotular o enquadramento, salvar no historico cientifico e exportar o overlay como PNG."))

    s.append(P("6.2. Telas principais", h2))
    s.append(boxed_table(
        [
            ["Tela", "Funcao"],
            ["HomeScreen", "Ponto de entrada com CTA principal"],
            ["CameraScreen", "Wrapper sobre expo-camera, captura JPEG"],
            ["ResultScreen", "Identificacao + recomendacoes (Roboflow)"],
            ["AuditarModeloScreen", "Grad-CAM + metricas (Keras local)"],
            ["InstitucionalScreen", "Texto sobre o projeto / contato"],
        ],
        col_widths=[5 * cm, 11.5 * cm],
    ))

    # --------------------------------------------------------------------
    # MODELOS DE IA
    # --------------------------------------------------------------------
    s.append(P("7. Modelos de IA", h1))

    s.append(P("7.1. Modelo de identificacao (Roboflow)", h2))
    s.append(
        P(
            "O modelo principal foi treinado na plataforma Roboflow utilizando ResNet50 com transfer "
            "learning a partir de pesos pre-treinados no ImageNet. A escolha por ResNet (He et al., 2016) "
            "se justifica pelo bom desempenho em classificacao de imagens com datasets de tamanho "
            "moderado (4-10 mil imagens) e pela capacidade dos blocos residuais de evitar o problema do "
            "<i>vanishing gradient</i> em redes profundas. Acuracia obtida no conjunto de teste: 95,8%."
        )
    )

    s.append(P("7.2. Modelo de auditoria (Keras local)", h2))
    s.append(
        P(
            "Para o Grad-CAM utilizamos MobileNetV2 (Sandler et al., 2018) com transfer learning. A "
            "arquitetura foi escolhida por tres razoes: <b>(i)</b> tamanho reduzido (~14 MB) compativel "
            "com o limite de memoria do plano Hobby do Railway; <b>(ii)</b> presenca explicita de blocos "
            "convolucionais nomeados (Conv_1, block_16_*) que facilitam a selecao da camada-alvo do "
            "Grad-CAM; <b>(iii)</b> performance comparavel a redes maiores em datasets de folhas (varios "
            "papers de plant disease usam MobileNet)."
        )
    )
    s.append(P("Arquitetura final usada:", body))
    s.append(P(
        "Input (224x224x3)<br/>"
        "  -> mobilenet_v2.preprocess_input (normalizacao [-1, 1])<br/>"
        "  -> MobileNetV2(include_top=False, weights='imagenet')<br/>"
        "  -> GlobalAveragePooling2D()<br/>"
        "  -> Dropout(0.5)<br/>"
        "  -> Dense(4, activation='softmax')",
        code,
    ))
    s.append(P(
        "Treinamento em duas fases: (1) 15 epocas com base congelada, lr=1e-3; (2) 10 epocas de fine-tune "
        "das ultimas 50 camadas, lr=1e-4.",
        body,
    ))

    s.append(P("7.3. Dataset", h2))
    s.append(
        P(
            "Utilizamos o dataset <b>Corn-Maize-Leaf-Disease</b> publicado pela Pampanga State Agricultural "
            "University (PRMSU) e disponivel no Roboflow Universe. As imagens originais sao do projeto "
            "<i>PlantVillage</i> (Hughes &amp; Salathe, 2015), referencia em pesquisas de plant disease "
            "detection. O dataset tem 4.186 imagens distribuidas entre as quatro classes, com particao "
            "padrao em train/valid/test."
        )
    )

    s.append(PageBreak())

    # --------------------------------------------------------------------
    # XAI E GRAD-CAM
    # --------------------------------------------------------------------
    s.append(P("8. Explainable AI (XAI) - Conceitos Essenciais", h1))
    s.append(
        P(
            "<b>Explainable AI</b> e um campo da IA dedicado a tornar as decisoes de modelos de aprendizado "
            "de maquina compreensiveis para seres humanos. Em redes neurais profundas (especialmente CNNs), "
            "as decisoes sao tomadas a partir de milhoes de parametros que interagem de forma nao-linear, "
            "o que torna impossivel entender o porque da resposta apenas inspecionando os pesos."
        )
    )
    s.append(
        P(
            "O termo \"explainable\" se opoe a \"black-box\". Segundo Adadi &amp; Berrada (2018), as "
            "tecnicas de XAI buscam responder pelo menos uma das tres perguntas: <i>(1) Por que o modelo "
            "tomou essa decisao? (2) Como ele tomaria uma decisao diferente? (3) Quando o modelo erra "
            "sistematicamente?</i> O AgroVision se concentra na primeira pergunta, usando uma tecnica "
            "<b>post-hoc</b> e <b>baseada em gradientes</b>: o Grad-CAM."
        )
    )

    s.append(P("8.1. Taxonomia rapida", h2))
    s.append(B("<b>Intrinsica vs post-hoc:</b> modelos intrinsicamente explicaveis (arvores, regressao linear) vs metodos aplicados depois (LIME, SHAP, Grad-CAM)."))
    s.append(B("<b>Global vs local:</b> explicar o modelo como um todo vs explicar uma predicao individual. Grad-CAM e <b>local</b>."))
    s.append(B("<b>Model-specific vs model-agnostic:</b> Grad-CAM e especifico para CNNs; LIME e SHAP sao agnosticos."))

    s.append(P("9. Grad-CAM: Mapeamento de Atencao Visual", h1))
    s.append(
        P(
            "<b>Gradient-weighted Class Activation Mapping (Grad-CAM)</b> foi proposto por Selvaraju et al. "
            "em 2017 (ICCV). E uma generalizacao do CAM original (Zhou et al., 2016) que removeu a "
            "limitacao de exigir uma arquitetura especifica com GAP no final."
        )
    )

    s.append(P("9.1. Intuicao", h2))
    s.append(
        P(
            "A ultima camada convolucional de uma CNN contem mapas de caracteristicas (feature maps) que "
            "preservam informacao espacial. Cada canal desses mapas e sensivel a um padrao visual "
            "diferente (textura, borda, formato). O Grad-CAM pergunta: <i>\"para a classe predita, quanto "
            "cada canal contribuiu? E onde esses canais estao mais ativos?\"</i> A resposta combinada "
            "produz um mapa de calor que indica quais regioes da imagem foram decisivas."
        )
    )

    s.append(P("9.2. Formulacao matematica", h2))
    s.append(P("Seja:", body))
    s.append(P(
        "A^k(i,j) = ativacao do canal k na posicao (i,j) da ultima camada convolucional<br/>"
        "y^c = score (logit ou probabilidade) da classe c<br/>"
        "Z = numero de pixels da feature map (largura x altura)",
        code,
    ))
    s.append(P("Passo 1 - calcular o peso de importancia de cada canal:", body))
    s.append(P("alpha_k^c = (1/Z) * &Sigma;_i &Sigma;_j (&part;y^c / &part;A^k(i,j))", formula))
    s.append(P("Passo 2 - somar os mapas ponderados e aplicar ReLU:", body))
    s.append(P("L_GradCAM^c(i,j) = ReLU( &Sigma;_k alpha_k^c &middot; A^k(i,j) )", formula))
    s.append(
        P(
            "O ReLU final descarta contribuicoes negativas (pixels que <i>diminuiriam</i> a confianca da "
            "classe). O mapa resultante e normalizado para o intervalo [0, 1] e aumentado (upsample) para "
            "o tamanho da imagem original."
        )
    )

    s.append(P("9.3. Implementacao no projeto", h2))
    s.append(
        P(
            "No arquivo <font color='#1C3D29'><b>api/xai/gradcam.py</b></font> a funcao "
            "<font color='#1C3D29'><b>generate_gradcam</b></font> usa <b>tf.GradientTape()</b> para "
            "registrar o forward pass, obtem o gradiente do score da classe em relacao aos feature maps "
            "da camada-alvo (por padrao, <b>Conv_1</b> do MobileNetV2), faz o pooling global dos "
            "gradientes para obter os pesos alpha_k, multiplica pelos feature maps e aplica ReLU + "
            "normalizacao."
        )
    )

    s.append(PageBreak())

    # --------------------------------------------------------------------
    # AL E AFS - FOCO PRINCIPAL
    # --------------------------------------------------------------------
    s.append(P("10. Metricas Quantitativas: AL e AFS", h1))
    s.append(
        P(
            "O Grad-CAM por si so e <b>qualitativo</b>: produz uma imagem que o ser humano olha e "
            "interpreta. Para criar uma <b>auditoria quantitativa</b>, o AgroVision introduz duas "
            "metricas calculadas sobre o heatmap em conjunto com uma <b>regiao de interesse (ROI)</b> "
            "definida por uma bounding box."
        )
    )
    s.append(
        P(
            "A ideia central: dado que o heatmap mostra <i>onde o modelo olhou</i>, e que a bbox mostra "
            "<i>onde o modelo deveria olhar</i> (a regiao da folha que importa), podemos medir o quanto "
            "essas duas regioes coincidem. Se o modelo olha para fora da folha (fundo, sombra, mao do "
            "usuario), isso e um sinal de aprendizado espurio."
        )
    )

    s.append(P("10.1. Attention Leakage (AL)", h2))
    s.append(
        P(
            "<b>Attention Leakage</b> (literalmente, \"vazamento de atencao\") mede a fracao da atencao do "
            "modelo que esta <b>fora</b> da regiao de interesse. Quanto maior o AL, mais o modelo se "
            "distraiu com elementos irrelevantes."
        )
    )
    s.append(P("AL = &Sigma;(H &times; (1 - M)) / &Sigma;(H)", formula))
    s.append(P(
        "onde:<br/>"
        "H = heatmap binarizado pelo threshold tau (apenas pixels com atencao &ge; tau contam)<br/>"
        "M = mascara binaria da regiao de interesse (1 dentro da bbox, 0 fora)",
        body,
    ))

    s.append(P("10.2. Attention Focus Score (AFS)", h2))
    s.append(
        P(
            "<b>Attention Focus Score</b> e o complemento do AL: mede a fracao da atencao que esta "
            "<b>dentro</b> da regiao de interesse. E uma metrica de qualidade: AFS alto = modelo focado."
        )
    )
    s.append(P("AFS = 1 - AL = &Sigma;(H &times; M) / &Sigma;(H)", formula))

    s.append(P("10.3. Threshold e por que ele importa", h2))
    s.append(
        P(
            "Antes de calcular AL e AFS, o heatmap passa por um <b>threshold</b> (limite minimo de "
            "intensidade) configuravel - por padrao tau = 0.5. Pixels com ativacao abaixo desse valor "
            "sao zerados. Isso evita que ruido de fundo (pixels com ativacao 0.05 espalhados pela "
            "imagem) contamine o calculo, garantindo que so a atencao <b>relevante</b> (acima do "
            "threshold) seja contabilizada."
        )
    )

    s.append(P("10.4. Implementacao real", h2))
    s.append(P(
        "# api/xai/metrics.py<br/>"
        "active = np.where(heatmap >= threshold, heatmap, 0.0)<br/>"
        "inside  = float((active * mask).sum())<br/>"
        "outside = float((active * (1 - mask)).sum())<br/>"
        "total   = inside + outside<br/>"
        "<br/>"
        "AL  = outside / total<br/>"
        "AFS = 1 - AL",
        code,
    ))

    s.append(P("10.5. Como a bbox e definida", h2))
    s.append(B("<b>Fixed (padrao):</b> bbox centralizada cobrindo 80% da imagem. Assume que o usuario enquadrou a folha minimamente bem."))
    s.append(B("<b>Green segmentation:</b> segmenta tons de verde no espaco HSV e usa a bounding box do maior blob como ROI. Util quando o enquadramento e ruim."))
    s.append(B("<b>Manual:</b> usuario informa coordenadas (modo cientifico)."))

    s.append(P("10.6. Casos praticos (interpretacao)", h2))
    s.append(P("<b>Caso 1 - Modelo focado e correto</b>", h3))
    s.append(
        P(
            "AFS = 92%, AL = 8%, predicao = Common_Rust (confianca 99%). Heatmap concentra-se exatamente "
            "sobre as pustulas marrom-alaranjadas tipicas da ferrugem, dentro da folha. <b>Interpretacao:</b> "
            "o modelo aprendeu o feature visual correto e nao se distraiu com bordas/fundo. Confianca alta "
            "na resposta."
        )
    )
    s.append(P("<b>Caso 2 - Modelo correto mas com atencao dispersa</b>", h3))
    s.append(
        P(
            "AFS = 51%, AL = 49%, predicao = Ferrugem-Comum (confianca 99%). Heatmap se distribui pela "
            "folha mas tambem ativa bordas e parte do fundo. <b>Interpretacao:</b> a classificacao esta "
            "correta, mas o modelo usou tambem informacao contextual (cor de fundo, textura ao redor). "
            "Para o agronegocio, ainda e aceitavel - mas indica que o modelo se beneficiaria de mais "
            "amostras com fundos variados."
        )
    )
    s.append(P("<b>Caso 3 - Modelo \"acertou por sorte\"</b>", h3))
    s.append(
        P(
            "AFS = 25%, AL = 75%, predicao = Healthy (confianca 87%). Heatmap concentra-se quase todo "
            "fora da folha (canto da imagem). <b>Interpretacao:</b> mesmo que a predicao final possa ser "
            "correta, o modelo nao se baseou em caracteristicas da folha. Esse e um caso de <b>shortcut "
            "learning</b> (Geirhos et al., 2020). O sistema deve sinalizar a resposta como nao confiavel, "
            "apesar da confianca alta."
        )
    )
    s.append(P("<b>Caso 4 - Modelo errado e com atencao errada</b>", h3))
    s.append(
        P(
            "AFS = 18%, AL = 82%, predicao = Blight (confianca 65%) mas a folha era saudavel. Heatmap "
            "ativa principalmente uma sombra escura no canto inferior. <b>Interpretacao:</b> o modelo "
            "confundiu a sombra com lesao. AL alto + confianca media = forte indicio de que a resposta "
            "deve ser descartada. Idealmente, o app sugere ao usuario recapturar a foto."
        )
    )

    s.append(P("10.7. Por que essas duas metricas e nao outras?", h2))
    s.append(
        P(
            "Existem metricas tradicionais de qualidade de explicacao na literatura (Pointing Game, "
            "Deletion/Insertion - Petsiuk et al., 2018; Sanity Checks - Adebayo et al., 2018). Algumas "
            "envolvem perturbacoes iterativas custosas, outras exigem ground-truth de saliencia (que "
            "exigiria anotacao manual pixel-a-pixel das lesoes - inviavel no nosso escopo)."
        )
    )
    s.append(
        P(
            "AL e AFS sao deliberadamente <b>simples</b>: requerem apenas uma bbox por imagem (que pode "
            "ser inferida automaticamente ou fixada) e uma comparacao set-theoretic. Sao computaveis em "
            "milisegundos, interpretaveis e ja capturam o sinal mais importante: <i>onde a atencao do "
            "modelo esta concentrada</i>. A simplicidade tambem favorece a comunicacao com o agronomo "
            "leigo em IA, que entende facilmente \"o modelo olhou 80% da hora pra dentro da folha\"."
        )
    )

    s.append(PageBreak())

    # --------------------------------------------------------------------
    # FUNCIONALIDADES
    # --------------------------------------------------------------------
    s.append(P("11. Funcionalidades do Aplicativo", h1))
    s.append(P("11.1. Identificacao", h2))
    s.append(
        P(
            "Fluxo principal. Captura ou seleciona uma foto, envia ao backend, exibe doenca identificada, "
            "confianca, descricao da patologia e recomendacoes de manejo. Suporte a quatro classes: "
            "Helmintosporiose, Ferrugem-Comum, Mancha-Cinzenta, Milho Saudavel."
        )
    )

    s.append(P("11.2. Auditoria (Grad-CAM + AL/AFS)", h2))
    s.append(
        P(
            "Tela acessada pelo botao \"Auditar Modelo\" na ResultScreen. Executa Grad-CAM no backend, "
            "renderiza heatmap sobre a imagem, exibe os valores numericos de AL e AFS com barra de "
            "progresso colorida (verde &ge; 70%, amarelo entre 40-70%, vermelho &lt; 40% para AFS)."
        )
    )

    s.append(P("11.3. Rotulagem de enquadramento", h2))
    s.append(
        P(
            "Dentro da auditoria, o usuario pode classificar a imagem como bem enquadrada / mal "
            "enquadrada / nao classificada. Esse rotulo e salvo junto com a analise, criando um conjunto "
            "de dados rotulados para estudos futuros de robustez do modelo."
        )
    )

    s.append(P("11.4. Historico cientifico", h2))
    s.append(
        P(
            "Todas as analises auditadas e salvas vao para um banco SQLite local. Estrutura permite "
            "consulta posterior, geracao de estatisticas e exportacao em batch."
        )
    )

    s.append(P("11.5. Exportar resultado", h2))
    s.append(
        P(
            "Apos salvar, o usuario pode exportar o heatmap como PNG via expo-sharing (compartilhamento "
            "nativo do iOS/Android). Util para documentar diagnosticos ou compartilhar com um agronomo "
            "consultor."
        )
    )

    s.append(P("11.6. Modulo institucional", h2))
    s.append(
        P(
            "Tela com informacoes sobre o projeto, autores, contato e referencias academicas. Funciona "
            "tambem como vitrine cientifica caso o app seja apresentado publicamente."
        )
    )

    # --------------------------------------------------------------------
    # LIMITACOES
    # --------------------------------------------------------------------
    s.append(P("12. Limitacoes e Trabalhos Futuros", h1))
    s.append(B("<b>Dois modelos paralelos</b>: identificacao usa Roboflow, auditoria usa Keras local. Sao da mesma familia (treinados no mesmo dataset), mas tem pesos diferentes - a auditoria explica o que o modelo Keras olharia, nao necessariamente o que o Roboflow olhou."))
    s.append(B("<b>Bbox padrao e generica</b>: a estrategia \"fixed\" cobre 80% central da imagem. Se a folha estiver descentralizada ou a foto incluir muito fundo, o AL/AFS pode ser pessimista. Trabalho futuro: segmentacao automatica via U-Net ou SAM."))
    s.append(B("<b>Apenas quatro classes</b>: o sistema nao detecta deficiencias nutricionais, pragas (insetos) ou outras doencas alem das tres modeladas. Expansao requer novo dataset."))
    s.append(B("<b>Sem fallback offline</b>: a versao atual depende de conexao para classificar. TFLite local foi removido durante o pivot para milho - pode ser re-introduzido em uma proxima versao."))
    s.append(B("<b>AL/AFS nao consideram a forma do heatmap</b>: dois heatmaps com mesma quantidade de atencao mas distribuicoes diferentes (concentrada vs dispersa) tem o mesmo AFS. Trabalho futuro: incorporar metricas de entropia espacial."))

    # --------------------------------------------------------------------
    # REFERENCIAS
    # --------------------------------------------------------------------
    s.append(PageBreak())
    s.append(P("13. Referencias Bibliograficas", h1))

    refs = [
        ("Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., &amp; Batra, D.",
         "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. ICCV 2017."),
        ("Zhou, B., Khosla, A., Lapedriza, A., Oliva, A., &amp; Torralba, A.",
         "Learning Deep Features for Discriminative Localization (CAM). CVPR 2016."),
        ("Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., &amp; Chen, L.",
         "MobileNetV2: Inverted Residuals and Linear Bottlenecks. CVPR 2018."),
        ("He, K., Zhang, X., Ren, S., &amp; Sun, J.",
         "Deep Residual Learning for Image Recognition (ResNet). CVPR 2016."),
        ("Adadi, A., &amp; Berrada, M.",
         "Peeking Inside the Black-Box: A Survey on Explainable Artificial Intelligence (XAI). IEEE Access, 2018."),
        ("Hughes, D. P., &amp; Salathe, M.",
         "An open access repository of images on plant health to enable the development of mobile disease diagnostics (PlantVillage). arXiv, 2015."),
        ("Geirhos, R., et al.",
         "Shortcut Learning in Deep Neural Networks. Nature Machine Intelligence, 2020."),
        ("Adebayo, J., et al.",
         "Sanity Checks for Saliency Maps. NeurIPS 2018."),
        ("Petsiuk, V., Das, A., &amp; Saenko, K.",
         "RISE: Randomized Input Sampling for Explanation of Black-box Models. BMVC 2018."),
        ("Pan, S. J., &amp; Yang, Q.",
         "A Survey on Transfer Learning. IEEE Transactions on Knowledge and Data Engineering, 2009."),
        ("LeCun, Y., Bottou, L., Bengio, Y., &amp; Haffner, P.",
         "Gradient-Based Learning Applied to Document Recognition. Proceedings of the IEEE, 1998."),
        ("Embrapa Milho e Sorgo",
         "Doencas da cultura do milho. Circular Tecnica, varios anos."),
        ("Pampanga State Agricultural University (PRMSU)",
         "Corn-Maize Leaf Disease Dataset. Roboflow Universe, 2023."),
    ]
    for author, title in refs:
        s.append(P(f"<b>{author}</b>. {title}", body))

    s.append(Spacer(1, 1 * cm))
    s.append(
        P(
            "<i>Documento gerado automaticamente para fins de estudo e referencia interna do projeto "
            "AgroVision. Para citacao academica formal, consulte o repositorio oficial e o trabalho "
            "completo de conclusao de curso.</i>",
            caption,
        )
    )

    return s


# ============================================================================
# Build
# ============================================================================
def main():
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="AgroVision - Documentacao Completa",
        author="Luiz Carlos Junior",
    )
    story = build_story()
    doc.build(story)
    print(f"OK -> {OUT_PATH}")


if __name__ == "__main__":
    main()
