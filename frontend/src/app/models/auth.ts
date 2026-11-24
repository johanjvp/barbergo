export interface LoginRequest {
  email: string;
  password: string;
}


export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}


export interface RegisterRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  phone: string | null;
}


export interface UserResponse {
  id: number;

  first_name: string;
  last_name: string;

  email: string;
  phone: string | null;

  email_verified: boolean;
  phone_verified: boolean;

  is_active: boolean;

  created_at: string;
}


export interface RoleResponse {
  name: string;
}


export interface UserMeResponse {
  id: number;

  first_name: string;
  last_name: string;

  email: string;
  phone: string | null;

  email_verified: boolean;
  phone_verified: boolean;

  is_active: boolean;

  roles: RoleResponse[];

  created_at: string;
}
