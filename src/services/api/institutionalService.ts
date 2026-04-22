import { WikiArticle } from '@models/institutional';

class InstitutionalService {
  private cache: Map<string, WikiArticle> = new Map();

  // Conhecimento local fallback para termos que não existem na Wikipedia
  private localKnowledge: Record<string, WikiArticle> = {
    'Cigarrinha': {
      title: 'Cigarrinha',
      summary: 'A cigarrinha é um inseto sugador que causa danos significativos às plantas agrícolas. Transmite viroses e enfraquece as plantas ao sugar a seiva. Controle através de inseticidas seletivos e manejo integrado de pragas.',
      imageUrl: undefined,
      pageUrl: 'https://pt.wikipedia.org/wiki/Cigarrinha',
      lastModified: new Date().toLocaleDateString('pt-BR'),
    },
    'Antracnose': {
      title: 'Antracnose',
      summary: 'Antracnose é uma doença fúngica que afeta diversos cultivos, caracterizada por lesões escuras nas folhas e frutos. O fungo Colletotrichum é o agente causador. Prevenção através de rotação de culturas e fungicidas apropriados.',
      imageUrl: undefined,
      pageUrl: 'https://pt.wikipedia.org/wiki/Antracnose',
      lastModified: new Date().toLocaleDateString('pt-BR'),
    },
    'Oídio': {
      title: 'Oídio',
      summary: 'Oídio é uma doença causada por fungos do gênero Erysiphe, resultando em pó branco nas folhas. Afeta principalmente em condições de baixa umidade. Tratamento com enxofre e fungicidas sistêmicos.',
      imageUrl: undefined,
      pageUrl: 'https://pt.wikipedia.org/wiki/O%C3%ADdio',
      lastModified: new Date().toLocaleDateString('pt-BR'),
    },
  };

  async fetchWikiSummary(searchTerm: string): Promise<WikiArticle> {
    const cleanTerm = searchTerm.trim();

    // Verifica cache primeiro
    if (this.cache.has(cleanTerm)) {
      return this.cache.get(cleanTerm)!;
    }

    try {
      // Nível 1: Tenta AGRIS (FAO) - principal
      console.log(`Trying AGRIS API for "${cleanTerm}"...`);
      return await this.fetchFromAGRIS(cleanTerm);
    } catch (agrisError) {
      console.log(`AGRIS failed for "${cleanTerm}", trying Open Agri Data...`);

      try {
        // Nível 2: Tenta Open Agri Data - secundário
        return await this.fetchFromOpenAgriData(cleanTerm);
      } catch (openAgriError) {
        console.log(`Open Agri Data failed for "${cleanTerm}", checking local knowledge...`);

        // Nível 3: Verifica conhecimento local
        if (this.localKnowledge[cleanTerm]) {
          const article = this.localKnowledge[cleanTerm];
          this.cache.set(cleanTerm, article);
          return article;
        }

        console.log(`Local knowledge not found for "${cleanTerm}", trying Wikipedia...`);

        try {
          // Nível 4: Tenta busca exata na Wikipedia
          return await this.fetchFromWikipediaExact(cleanTerm);
        } catch (exactError) {
          console.log(`Wikipedia exact search failed, trying Wikipedia search API...`);

          try {
            // Nível 5: Tenta Wikipedia Search API
            return await this.fetchFromWikipediaSearch(cleanTerm);
          } catch (searchError) {
            // Fallback final com mensagem amigável
            return this.createOfflineArticle(cleanTerm);
          }
        }
      }
    }
  }

  private async fetchFromAGRIS(term: string): Promise<WikiArticle> {
    // AGRIS API - Food and Agriculture Organization
    // Busca documentos de pesquisa agrícola
    const response = await fetch(
      `https://agris.fao.org/agris-search/api/search?query=${encodeURIComponent(
        term
      )}&format=json`,
      {
        headers: {
          'User-Agent': 'AgroVision/1.0 (Agricultural diagnostic app)',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`AGRIS API returned ${response.status}`);
    }

    const data = await response.json();
    const results = data.response?.docs || data.docs || [];

    if (results.length === 0) {
      throw new Error('No AGRIS results found');
    }

    // Processa o primeiro resultado (mais relevante)
    const result = results[0];
    const article: WikiArticle = {
      title: result.title || result.name || term,
      summary:
        result.summary ||
        result.description ||
        result.abstract ||
        'Artigo disponível no AGRIS (FAO)',
      imageUrl: result.thumbnail || undefined,
      pageUrl: result.uri || result.url || `https://agris.fao.org/agris-search/search?query=${encodeURIComponent(term)}`,
      lastModified: result.dateModified || result.year || 'Data desconhecida',
    };

    this.cache.set(term, article);
    return article;
  }

  private async fetchFromOpenAgriData(term: string): Promise<WikiArticle> {
    // Open Agri Data - Linked Open Data sobre agricultura
    const response = await fetch(
      `https://www.openagridata.eu/api/search?q=${encodeURIComponent(term)}`,
      {
        headers: {
          'User-Agent': 'AgroVision/1.0 (Agricultural diagnostic app)',
          'Accept': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Open Agri Data returned ${response.status}`);
    }

    const data = await response.json();
    const results = data.results || data.data || [];

    if (results.length === 0) {
      throw new Error('No Open Agri Data results found');
    }

    // Processa o primeiro resultado
    const result = results[0];
    const article: WikiArticle = {
      title: result.title || result.label || result.name || term,
      summary:
        result.description ||
        result.summary ||
        result.comment ||
        'Informação disponível em Open Agri Data',
      imageUrl: result.image || result.thumbnail || undefined,
      pageUrl: result.url || result.uri || `https://www.openagridata.eu/`,
      lastModified: result.modified || result.updated || 'Data desconhecida',
    };

    this.cache.set(term, article);
    return article;
  }

  private async fetchFromWikipediaExact(term: string): Promise<WikiArticle> {
    const encodedTerm = encodeURIComponent(term);
    const response = await fetch(
      `https://pt.wikipedia.org/api/rest_v1/page/summary/${encodedTerm}`,
      {
        headers: {
          'User-Agent': 'AgroVision/1.0 (Plant disease detection app)',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Wikipedia exact search returned ${response.status}`);
    }

    const data = await response.json();
    const article: WikiArticle = {
      title: data.title || term,
      summary: data.extract || 'Conteúdo não disponível',
      imageUrl: data.thumbnail?.source,
      pageUrl: data.content_urls?.desktop?.page || `https://pt.wikipedia.org/wiki/${encodedTerm}`,
      lastModified: data.timestamp
        ? new Date(data.timestamp).toLocaleDateString('pt-BR')
        : 'Data desconhecida',
    };

    this.cache.set(term, article);
    return article;
  }

  private async fetchFromWikipediaSearch(term: string): Promise<WikiArticle> {
    const response = await fetch(
      `https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(
        term
      )}&format=json&origin=*`,
      {
        headers: {
          'User-Agent': 'AgroVision/1.0 (Plant disease detection app)',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Wikipedia search returned ${response.status}`);
    }

    const data = await response.json();
    const results = data.query?.search || [];

    if (results.length === 0) {
      throw new Error('No search results found');
    }

    // Pega o primeiro resultado (mais relevante)
    const firstResult = results[0];
    const pageTitle = firstResult.title;

    // Busca o resumo da página encontrada
    return this.fetchFromWikipediaExact(pageTitle);
  }

  private createOfflineArticle(term: string): WikiArticle {
    return {
      title: term,
      summary: `Informação sobre "${term}" não disponível no momento. O artigo pode não existir na Wikipedia em português ou o servidor pode estar indisponível. Verifique sua conexão de internet e tente novamente.`,
      imageUrl: undefined,
      pageUrl: `https://pt.wikipedia.org/wiki/${encodeURIComponent(term)}`,
      lastModified: new Date().toLocaleDateString('pt-BR'),
    };
  }
}

export const institutionalService = new InstitutionalService();
