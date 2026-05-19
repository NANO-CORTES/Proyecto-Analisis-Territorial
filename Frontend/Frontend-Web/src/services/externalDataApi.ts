/**
 * Servicio para consumir datos de APIs externas (datos.gov.co, datosabiertos.bogota.gov.co)
 */

import axios, { AxiosInstance } from 'axios';

interface TerritorialDataResponse {
  success: boolean;
  data: {
    variable: string;
    department: string;
    municipality: string;
    sources: {
      datos_gov: any[];
      bogota: any[];
    };
    found: boolean;
  };
}

interface MunicipalityIndicators {
  success: boolean;
  data: {
    department: string;
    municipality: string;
    indicators: {
      population: any;
      income: any;
      education: any;
      competition: any;
    };
    fetched_at: string;
  };
}

interface DatasetSearchResponse {
  success: boolean;
  organization: string;
  query: string;
  total: number;
  datasets: any[];
}

export class ExternalDataService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001') {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL: `${this.baseURL}/api/v1/external`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para inyectar dinámicamente el token de autorización
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
  }

  /**
   * Obtiene datos territoriales para una variable específica
   * Variables: population, income, education, competition
   */
  async getTerritorialData(
    department: string,
    municipality: string,
    variable: 'population' | 'income' | 'education' | 'competition' = 'population'
  ): Promise<TerritorialDataResponse> {
    try {
      const response = await this.api.get<TerritorialDataResponse>('/territorial-data', {
        params: { department, municipality, variable },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching territorial data:', error);
      throw error;
    }
  }

  /**
   * Obtiene todos los indicadores para un municipio
   * Retorna datos de población, ingreso, educación y competencia
   */
  async getMunicipalityIndicators(
    department: string,
    municipality: string
  ): Promise<MunicipalityIndicators> {
    try {
      const response = await this.api.get<MunicipalityIndicators>('/municipality-indicators', {
        params: { department, municipality },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching municipality indicators:', error);
      throw error;
    }
  }

  /**
   * Busca datasets en los portales CKAN
   */
  async searchDatasets(
    query: string,
    organization: 'datos_gov' | 'bogota' = 'datos_gov'
  ): Promise<DatasetSearchResponse> {
    try {
      const response = await this.api.get<DatasetSearchResponse>('/search-datasets', {
        params: { query, organization },
      });
      return response.data;
    } catch (error) {
      console.error('Error searching datasets:', error);
      throw error;
    }
  }

  /**
   * Realiza una query directa a la API CKAN
   */
  async ckanQuery(
    query: string = '',
    organization: 'datos_gov' | 'bogota' = 'datos_gov',
    datasetType: string = 'dataset'
  ): Promise<any> {
    try {
      const response = await this.api.get('/ckan-query', {
        params: {
          query,
          organization,
          dataset_type: datasetType,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error in CKAN query:', error);
      throw error;
    }
  }

  /**
   * Verifica el estado del servicio de datos externos
   */
  async healthCheck(): Promise<{ status: string; services: any }> {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error in health check:', error);
      throw error;
    }
  }

  /**
   * Obtiene datos de población para un municipio
   */
  async getPopulationData(
    department: string,
    municipality: string
  ): Promise<TerritorialDataResponse> {
    return this.getTerritorialData(department, municipality, 'population');
  }

  /**
   * Obtiene datos de ingresos para un municipio
   */
  async getIncomeData(
    department: string,
    municipality: string
  ): Promise<TerritorialDataResponse> {
    return this.getTerritorialData(department, municipality, 'income');
  }

  /**
   * Obtiene datos de educación para un municipio
   */
  async getEducationData(
    department: string,
    municipality: string
  ): Promise<TerritorialDataResponse> {
    return this.getTerritorialData(department, municipality, 'education');
  }

  /**
   * Obtiene datos de competencia para un municipio
   */
  async getCompetitionData(
    department: string,
    municipality: string
  ): Promise<TerritorialDataResponse> {
    return this.getTerritorialData(department, municipality, 'competition');
  }
}

// Instancia exportada por defecto
export const externalDataService = new ExternalDataService();
