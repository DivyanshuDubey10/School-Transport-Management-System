import React, { useState } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'

export interface Column<T> {
  key: keyof T | string
  header: string
  render?: (row: T) => React.ReactNode
  sortable?: boolean
  className?: string
}

export interface TableProps<T> {
  columns: Column<T>[]
  data: T[]
  isLoading?: boolean
  keyExtractor?: (row: T) => string | number
  keyField?: keyof T | string
  emptyMessage?: string
}

function SkeletonRow({ cols }: { cols: number }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="skeleton h-4 rounded bg-slate-100 animate-pulse" />
        </td>
      ))}
    </tr>
  )
}

export function Table<T>({
  columns,
  data,
  isLoading = false,
  keyExtractor,
  keyField,
  emptyMessage = 'No records found.',
}: TableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  const sorted = React.useMemo(() => {
    if (!sortKey) return data
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortKey]
      const bVal = (b as Record<string, unknown>)[sortKey]
      if (aVal == null) return 1
      if (bVal == null) return -1
      const cmp = String(aVal).localeCompare(String(bVal), undefined, { numeric: true })
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [data, sortKey, sortDir])

  const getRowKey = (row: T, index: number): string | number => {
    if (keyExtractor) return keyExtractor(row)
    if (keyField && (row as Record<string, unknown>)[keyField as string] != null) {
      return (row as Record<string, unknown>)[keyField as string] as string | number
    }
    if ((row as Record<string, unknown>).id != null) {
      return (row as Record<string, unknown>).id as string | number
    }
    return index
  }

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-100 text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className={[
                  'px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide select-none',
                  col.sortable ? 'cursor-pointer hover:text-slate-700' : '',
                  col.className ?? '',
                ].join(' ')}
                onClick={col.sortable ? () => handleSort(String(col.key)) : undefined}
              >
                <span className="inline-flex items-center gap-1">
                  {col.header}
                  {col.sortable && (
                    <span className="inline-flex flex-col">
                      <ChevronUp
                        size={10}
                        className={
                          sortKey === String(col.key) && sortDir === 'asc'
                            ? 'text-sky-500'
                            : 'text-slate-300'
                        }
                      />
                      <ChevronDown
                        size={10}
                        className={
                          sortKey === String(col.key) && sortDir === 'desc'
                            ? 'text-sky-500'
                            : 'text-slate-300'
                        }
                      />
                    </span>
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <SkeletonRow key={i} cols={columns.length} />
            ))
          ) : sorted.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-12 text-center text-slate-400"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sorted.map((row, idx) => (
              <tr
                key={getRowKey(row, idx)}
                className="hover:bg-slate-50/70 transition-colors"
              >
                {columns.map((col) => (
                  <td
                    key={String(col.key)}
                    className={['px-4 py-3 text-slate-700', col.className ?? ''].join(' ')}
                  >
                    {col.render
                      ? col.render(row)
                      : String((row as Record<string, unknown>)[String(col.key)] ?? '—')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
