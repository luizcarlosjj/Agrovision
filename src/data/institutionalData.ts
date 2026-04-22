import { Category, CategoryItem } from '@models/institutional';

export const INSTITUTIONAL_CATEGORIES: Category[] = [
  {
    id: 'culturas',
    name: 'Culturas',
    icon: '🌾',
    items: [
      { id: 'milho', name: 'Milho', searchTerm: 'Milho agricultura' },
      { id: 'soja', name: 'Soja', searchTerm: 'Soja cultivo' },
      { id: 'cafe', name: 'Café', searchTerm: 'Café plantação' },
      { id: 'algodao', name: 'Algodão', searchTerm: 'Algodão fibra' },
      { id: 'cana', name: 'Cana-de-açúcar', searchTerm: 'Cana-de-açúcar' },
      { id: 'arroz', name: 'Arroz', searchTerm: 'Arroz cultivo' },
      { id: 'feijao', name: 'Feijão', searchTerm: 'Feijão plantação' },
      { id: 'trigo', name: 'Trigo', searchTerm: 'Trigo cereal' },
    ],
  },
  {
    id: 'doencas',
    name: 'Doenças',
    icon: '🦠',
    items: [
      { id: 'ferrugem', name: 'Ferrugem', searchTerm: 'Ferrugem plantas' },
      { id: 'oideo', name: 'Oídio', searchTerm: 'Oídio fungal' },
      { id: 'mancha', name: 'Mancha Foliar', searchTerm: 'Mancha foliar' },
      { id: 'antracnose', name: 'Antracnose', searchTerm: 'Antracnose' },
      { id: 'mosaico', name: 'Mosaico', searchTerm: 'Mosaico viral' },
      { id: 'podridao', name: 'Podridão', searchTerm: 'Podridão raíz' },
    ],
  },
  {
    id: 'pragas',
    name: 'Pragas',
    icon: '🐛',
    items: [
      { id: 'lagarta', name: 'Lagarta-do-cartucho', searchTerm: 'Lagarta cartucho' },
      { id: 'pulgao', name: 'Pulgão', searchTerm: 'Pulgão inseto' },
      { id: 'mosca', name: 'Mosca-branca', searchTerm: 'Mosca branca' },
      { id: 'percevejo', name: 'Percevejo', searchTerm: 'Percevejo' },
      { id: 'cigarrinha', name: 'Cigarrinha', searchTerm: 'Cigarrinha' },
      { id: 'acaro', name: 'Ácaro', searchTerm: 'Ácaro aranha' },
    ],
  },
  {
    id: 'solos',
    name: 'Solos e Nutrição',
    icon: '🌱',
    items: [
      { id: 'nitrogenio', name: 'Nitrogênio', searchTerm: 'Nitrogênio nutriente' },
      { id: 'fosforo', name: 'Fósforo', searchTerm: 'Fósforo nutriente' },
      { id: 'potassio', name: 'Potássio', searchTerm: 'Potássio nutriente' },
      { id: 'ph', name: 'pH do Solo', searchTerm: 'pH solo' },
      { id: 'calcario', name: 'Calcário', searchTerm: 'Calcário correção' },
      { id: 'materia', name: 'Matéria Orgânica', searchTerm: 'Matéria orgânica solo' },
    ],
  },
];
