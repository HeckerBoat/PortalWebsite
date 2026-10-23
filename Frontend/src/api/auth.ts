import request from './request'

export interface LoginParams {
  account: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  email?: string
  phone?: string
}

export interface UserInfo {
  id: number
  username: string
  email: string | null
  phone: string | null
  role: string
  is_active?: boolean
}

export const login = (data: LoginParams) =>
  request.post<any, any>('/api/auth/login', data)

export const register = (data: RegisterParams) =>
  request.post<any, any>('/api/auth/register', data)

export const getMe = () =>
  request.get<any, any>('/api/auth/me')
