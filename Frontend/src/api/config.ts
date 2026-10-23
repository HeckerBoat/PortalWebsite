import request from './request'

export const getConfig = (key?: string) =>
  request.get<any, any>(key ? `/api/config/${key}` : '/api/config')

export const setConfig = (key: string, data: { value: string; description?: string }) =>
  request.put<any, any>(`/api/config/${key}`, data)

export const deleteConfig = (key: string) =>
  request.delete<any, any>(`/api/config/${key}`)
