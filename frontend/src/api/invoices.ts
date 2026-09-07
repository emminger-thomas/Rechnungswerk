import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { api } from "./client"
import type { Invoice } from "../types/models"

export function useInvoice(id: string | undefined) {
  return useQuery({
    queryKey: ["invoices", id],
    queryFn: () => api.get<Invoice>(`/invoices/${id}/`),
    enabled: Boolean(id),
  })
}

export function useInvoices(status?: string) {
  return useQuery({
    queryKey: ["invoices", "list", status],
    queryFn: () =>
      api.get<{ results: Invoice[] }>(`/invoices/${status ? `?status=${status}` : ""}`),
  })
}

export function useCreateInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Invoice>) => api.post<Invoice>("/invoices/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] }),
  })
}

export function useUpdateInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Invoice> }) =>
      api.patch<Invoice>(`/invoices/${id}/`, data),
    onSuccess: (invoice) => {
      queryClient.invalidateQueries({ queryKey: ["invoices", invoice.id] })
      queryClient.invalidateQueries({ queryKey: ["invoices", "list"] })
    },
  })
}

interface FinalizeError {
  errors: string[]
}

export function useFinalizeInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.post<Invoice | FinalizeError>(`/invoices/${id}/finalize/`),
    onSuccess: (_result, id) => {
      queryClient.invalidateQueries({ queryKey: ["invoices", id] })
      queryClient.invalidateQueries({ queryKey: ["invoices", "list"] })
    },
  })
}

export function useCancelInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.post<Invoice>(`/invoices/${id}/cancel/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] }),
  })
}

interface ActionError {
  errors: string[]
}

export function useMarkInvoicePaid() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, paidDate }: { id: string; paidDate: string }) =>
      api.post<Invoice | ActionError>(`/invoices/${id}/mark-paid/`, { paid_date: paidDate }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] }),
  })
}

export function useCreateReminder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.post<Invoice | ActionError>(`/invoices/${id}/remind/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] }),
  })
}

export async function downloadInvoicePdf(id: string, invoiceNumber: string) {
  const blob = await api.blob(`/invoices/${id}/pdf/`)
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `${invoiceNumber}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function downloadDatevExport(year: number, month: number) {
  const blob = await api.blob(`/export/datev?year=${year}&month=${String(month).padStart(2, "0")}`)
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `DATEV_Export_${year}-${String(month).padStart(2, "0")}.zip`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
