import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { api } from "./client"
import type { Customer, CustomerInput, CustomerLookup } from "../types/models"

interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export function useCustomerSearch(query: string) {
  return useQuery({
    queryKey: ["customers", "search", query],
    queryFn: () => api.get<CustomerLookup[]>(`/customers/search/?q=${encodeURIComponent(query)}`),
    enabled: query.trim().length > 0,
  })
}

export function useCustomers() {
  return useQuery({
    queryKey: ["customers"],
    queryFn: () => api.get<Paginated<Customer>>("/customers/"),
  })
}

export function useCreateCustomer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<CustomerInput>) => api.post<Customer>("/customers/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] })
    },
  })
}

export interface ImportPreviewRow {
  data: Record<string, string>
  errors: string[]
}

export interface ImportPreviewResponse {
  mapped_columns: Record<string, string>
  unmapped_columns: string[]
  valid_count: number
  total_count: number
  rows: ImportPreviewRow[]
  created_count?: number
}

export function useImportCustomersCsv() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ file, dryRun }: { file: File; dryRun: boolean }) => {
      const formData = new FormData()
      formData.append("file", file)
      return api.post<ImportPreviewResponse>(
        `/customers/import-csv/?dry_run=${dryRun ? "true" : "false"}`,
        formData,
      )
    },
    onSuccess: (_data, variables) => {
      if (!variables.dryRun) {
        queryClient.invalidateQueries({ queryKey: ["customers"] })
      }
    },
  })
}
