/**
 * Plant Domain Models
 * Data structures for plant information
 */

/**
 * Plant species information
 */
export interface Plant {
  id: string;
  scientificName: string;
  commonName: string;
  family: string;
  genus: string;
  species: string;
  description: string;
  careInstructions: PlantCareInstructions;
  commonDiseases: string[];
  commonPests: string[];
  characteristics: PlantCharacteristics;
}

/**
 * Care instructions for a plant
 */
export interface PlantCareInstructions {
  sunlight: string; // e.g., "Full sun (6-8 hours)"
  water: string; // e.g., "Keep soil moist, not waterlogged"
  soil: string; // e.g., "Well-draining soil"
  temperature: string; // e.g., "20-30°C"
  humidity: string; // e.g., "Moderate humidity"
  fertilizer?: string;
  pruning?: string;
  propagation?: string;
}

/**
 * Physical characteristics of a plant
 */
export interface PlantCharacteristics {
  leafColor: string[];
  leafShape: string;
  leafSize: string;
  stemColor: string;
  flowerColor?: string[];
  flowerType?: string;
  height: string; // e.g., "30-60 cm"
  spread: string;
  seasonalBehavior: string;
}

/**
 * Plant health status for a given time period
 */
export interface PlantHealthStatus {
  plantId: string;
  timestamp: string;
  healthScore: number; // 0-100
  issues: string[];
  lastInspection: string;
  recommendations: string[];
}

/**
 * Captured plant image metadata
 */
export interface PlantImage {
  id: string;
  plantId?: string;
  imageUri: string;
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  notes?: string;
  analysisResults: string[]; // Analysis IDs
}
