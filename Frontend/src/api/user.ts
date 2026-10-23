import request from './request'

export interface UserItem {
  id: number
  username: string
  email: string | null
  phone: string | null
  role: string
  is_active: boolean
  created_at: string | null
  updated_at: string | null
}

export const listUsers = (keyword?: string) =>
  request.get<any, any>('/api/users', { params: { keyword } })

export const createUser = (data: any) =>
  request.post<any, any>('/api/users', data)

export const updateUser = (id: number, data: any) =>
  request.put<any, any>(`/api/users/${id}`, data)

export const deleteUser = (id: number) =>
  request.delete<any, any>(`/api/users/${id}`)
