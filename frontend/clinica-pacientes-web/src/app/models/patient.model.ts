export interface Patient {
  paciente_id: number;
  tipo_documento: string;
  tipo_documento_nombre: string | null;
  documento: string;
  nombre_completo: string;
  fecha_nacimiento: string;
  genero: string;
  telefono: string;
  correo: string | null;
  eps_codigo: string;
  eps_nombre: string | null;
  ciudad: string | null;
  prioridad: string;
  estado: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface PatientPayload {
  tipo_documento: string;
  documento: string;
  nombre_completo: string;
  fecha_nacimiento: string;
  genero: string;
  telefono: string;
  correo: string | null;
  eps_codigo: string;
  ciudad: string | null;
  prioridad: string;
  estado: string;
}

export interface PatientResponse {
  message?: string;
  patient: Patient;
}

export interface PatientFilters {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
  priority?: string;
  eps_codigo?: string;
}

export interface PatientPagination {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
  next_page: number | null;
  previous_page: number | null;
}

export interface PatientListResponse {
  items: Patient[];
  pagination: PatientPagination;
  filters: {
    search: string | null;
    status: string | null;
    priority: string | null;
    eps_codigo: string | null;
  };
}

export interface DeletePatientResponse {
  message: string;
  patient: {
    paciente_id: number;
    documento: string;
    nombre_completo: string;
  };
}