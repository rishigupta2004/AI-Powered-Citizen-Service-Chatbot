export interface Service {
  service_id: number;
  name: string;
  category: string;
  ministry?: string;
}

export interface Procedure {
  procedure_id: number;
  service_id: number;
  title: string;
  description?: string;
}

export interface Document {
  doc_id: number;
  service_id: number;
  name: string;
  document_type?: string;
  is_mandatory: boolean;
}

export interface FAQ {
  faq_id: number;
  service_id: number;
  question: string;
  answer: string;
}

export type SearchResultItem = {
  id: string | number;
  title: string;
  snippet: string;
  category?: string;
};

export interface SearchResponse {
  total_results: number;
  results: SearchResultItem[];
}

