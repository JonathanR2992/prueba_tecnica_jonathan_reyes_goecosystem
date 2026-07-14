export interface User {
  usuario_id: number;
  usuario: string;
  nombre: string;
  rol: 'ADMIN' | 'OPERADOR';
  activo: boolean;
}

export interface LoginRequest {
  usuario: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  token_type: 'Bearer';
  user: User;
}

export interface CurrentUserResponse {
  user: User;
  token: {
    rol: string;
    nombre: string;
  };
}