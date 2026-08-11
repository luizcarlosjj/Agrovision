# AgroVision — o projeto explicado

> Documento didático. Se você nunca ouviu falar de "rede neural" e mesmo assim
> quer entender o que este projeto faz e por que ele importa, comece por aqui.

---

## 1. O problema

O milho é uma das culturas mais plantadas do Brasil. Três doenças foliares
comuns podem devastar uma lavoura se não forem identificadas cedo:

- **Helmintosporiose** (Blight)
- **Ferrugem-comum** (Common Rust)
- **Mancha-cinzenta** (Gray Leaf Spot)

O diagnóstico correto exige que um profissional (engenheiro agrônomo) vá até
a lavoura, examine as folhas, e decida. Isso é caro, lento e nem sempre
disponível — principalmente para o pequeno produtor.

## 2. O que o AgroVision faz

Um aplicativo de celular que:

1. **Fotografa uma folha** de milho.
2. **Envia a imagem pela internet** para um modelo de inteligência artificial.
3. **Recebe o diagnóstico** em segundos: qual doença (ou "saudável"), quão
   confiante é a IA, e recomendações práticas de manejo.

Não substitui o agrônomo — funciona como um **apoio à decisão**, permitindo
uma primeira triagem barata e rápida.

## 3. Como funciona (sem entrar em matemática)

### 3.1. O olho da IA
A IA usada é uma **rede neural convolucional**. Você pode pensar nela como um
sistema de filtros em camadas: as primeiras camadas enxergam bordas e cores,
as camadas mais profundas enxergam padrões complexos (formato da lesão,
textura, distribuição na folha). No final, a rede diz "isso parece 92%
ferrugem-comum".

Esse modelo foi treinado no **Roboflow** com milhares de fotos de folhas de
milho, já classificadas por especialistas. O aplicativo simplesmente **envia
a foto** para o modelo publicado no Roboflow e recebe a resposta.

### 3.2. O ciclo dentro do app
```
[Foto]  →  [Envio pela internet]  →  [Roboflow classifica]
                                            │
                                            ▼
                              [Resultado + recomendações]
                                            │
                                            ▼
                              [Salvo no celular (histórico)]
```

## 4. O diferencial científico — por que é um TCC

Um sistema que só diz "é ferrugem" é útil, mas **ninguém sabe por quê**. Se
a IA errar, não temos como auditar. E confiar cegamente em uma "caixa preta"
para decisões que envolvem defensivos agrícolas é arriscado.

O AgroVision resolve isso com uma segunda camada: **Explicabilidade (XAI —
eXplainable Artificial Intelligence)**.

### 4.1. Grad-CAM — "mostra onde você olhou"
O **Grad-CAM** (Gradient-weighted Class Activation Mapping) é uma técnica
que produz um **mapa de calor** sobre a foto original, destacando as regiões
que mais influenciaram a decisão da rede.

Exemplo: se a IA disse "Ferrugem-comum", o Grad-CAM colore em vermelho as
pústulas alaranjadas específicas da doença. Se a rede tivesse olhado, por
engano, para uma sombra no fundo da imagem, veríamos o vermelho fora da
folha — sinal de que o modelo não é confiável para aquela foto.

### 4.2. Duas métricas quantitativas
Não basta olhar o mapa de calor com os olhos. O projeto calcula duas métricas
que dão um número objetivo:

- **AFS (Attention Focus Score)** — de 0 a 1. Quanto da atenção do modelo
  ficou dentro da folha. Quanto mais perto de 1, mais "focado" o modelo estava.
- **AL (Attention Leakage)** — de 0 a 1. O oposto: quanto da atenção "vazou"
  para o fundo da imagem (folhas vizinhas, solo, sombra). Quanto mais próximo
  de 0, melhor.

Um diagnóstico com **AFS alto** e **AL baixo** é mais confiável que um com
o inverso, mesmo que ambos apontem a mesma classe com a mesma confiança.

### 4.3. Por que isso é intervenção científica
- Traz **transparência** para decisões automatizadas em agricultura.
- Permite **auditar o modelo** sem precisar reprogramar nada — o próprio app
  tem um modo "Auditar Modelo" e um "Modo Científico (lote)" que gera CSV
  com AL/AFS de várias imagens de uma vez.
- É reprodutível: qualquer pesquisador pode rodar o app com fotos próprias
  e comparar resultados.

## 5. Arquitetura em duas caixas

```
┌──────────────────────────┐      ┌──────────────────────────────┐
│   Celular (React Native) │      │  Servidor (FastAPI, Railway) │
│                          │      │                              │
│  • Câmera / Galeria      │─────▶│  • /ws/classify → Roboflow   │
│  • Tela de resultado     │◀─────│  • /ws/gradcam  → Keras+XAI  │
│  • Histórico local       │      │                              │
│  • Auditar Modelo (XAI)  │      │  Autenticação por API Key    │
└──────────────────────────┘      └──────────────────────────────┘
```

**Por que dois lugares?** Porque:
- A classificação é rápida e o Roboflow faz melhor que qualquer coisa que
  eu conseguiria treinar localmente.
- O Grad-CAM precisa acesso aos "cálculos internos" da rede (gradientes),
  que o Roboflow não expõe. Então o servidor guarda uma cópia do modelo em
  formato Keras só para gerar as explicações.

## 6. Segurança básica
Como é um TCC (não um sistema bancário), a segurança é proporcional:

- Toda requisição precisa de uma **chave de API** de pelo menos 16 caracteres.
- O servidor **recusa qualquer request se a chave não estiver configurada** —
  não existe modo "aberto" em produção.
- Comparação da chave é feita em **tempo constante** para evitar ataques de
  timing.
- Existe limite de tamanho de imagem (5 MB por padrão) para evitar sobrecarga.
- Chaves e segredos ficam em variáveis de ambiente — **nada é commitado**
  no repositório.

## 7. Como testar em 5 minutos
1. Instale o app pelo Expo Go, escaneando o QR Code após rodar `npx expo start`.
2. Aponte a câmera para uma folha de milho.
3. Toque em "Diagnosticar Doença".
4. Espere 2–3 segundos.
5. Veja o resultado + recomendação. Toque em "Auditar Modelo" para ver o
   mapa de calor e as métricas AFS/AL.

## 8. Limitações (que o TCC assume e discute)
- Modelo treinado só para as 4 classes acima — não identifica outras culturas
  ou doenças fora dessa lista.
- Depende de conexão com a internet (é online-first).
- Fotos com iluminação ruim, foco desalinhado ou várias folhas na mesma
  imagem podem tirar o AFS pra baixo — o app avisa quando isso acontece.
- O diagnóstico é **orientativo**, não substitui a inspeção presencial de
  um profissional.

## 9. Glossário rápido
- **IA / Rede Neural** — programa que aprende padrões a partir de exemplos.
- **Classificação** — dizer "esta foto pertence à categoria X".
- **Roboflow** — plataforma na internet que hospeda o modelo já treinado.
- **Grad-CAM** — técnica que gera um mapa de calor mostrando onde a rede
  "olhou" para tomar a decisão.
- **AFS / AL** — dois números que quantificam se a atenção do modelo ficou
  no lugar certo (folha) ou vazou para o fundo.
- **XAI** — sigla em inglês para "Inteligência Artificial Explicável".
- **API Key** — senha que o app manda junto para o servidor confirmar quem
  é quem está pedindo.

---

*Detalhes técnicos, código e endpoints: ver [README.md](README.md) e
[agrovision-ml-service/README.md](agrovision-ml-service/README.md).*
