export interface DocumentType {
  codigo: string;
  nombre: string;
  activo: boolean;
}

export interface Gender {
  nombre: string;
  activo: boolean;
}

export interface Eps {
  eps_codigo: string;
  eps_nombre: string;
  activo: boolean;
}

export interface Priority {
  nombre: string;
  nivel: number;
  activo: boolean;
}

export interface PatientStatus {
  nombre: string;
  activo: boolean;
}

export interface CatalogsResponse {
  tipos_documento: DocumentType[];
  generos: Gender[];
  eps: Eps[];
  prioridades: Priority[];
  estados: PatientStatus[];
}