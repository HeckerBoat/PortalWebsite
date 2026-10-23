import request from './request'

export interface HtmlFileItem {
  id: number
  filename: string
  relative_path: string
  url: string
  title: string | null
  description: string | null
  file_size: number
  last_modified: string | null
  updated_at: string | null
}

export const listHtml = (keyword?: string) =>
  request.get<any, any>('/api/html/list', { params: { keyword } })

export const scanHtml = () =>
  request.post<any, any>('/api/html/scan')

export const getHtml = (id: number) =>
  request.get<any, any>(`/api/html/${id}`)

export const updateHtml = (id: number, data: Partial<{ title: string; description: string; url: string }>) =>
  request.put<any, any>(`/api/html/${id}`, data)

export const deleteHtml = (id: number) =>
  request.delete<any, any>(`/api/html/${id}`)
