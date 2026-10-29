import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import {
  getRoutes,
  createRoute,
  updateRoute,
  deleteRoute,
  type Route,
  type RoutePayload,
} from '../../api/routes'
import { Table, type Column } from '../../components/ui/Table'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { SearchBar } from '../../components/ui/SearchBar'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'

type FormErrors = Partial<Record<keyof RoutePayload | 'root', string>>

const emptyForm: RoutePayload = {
  route_name: '',
}

export default function Routes() {
  const qc = useQueryClient()
  const { showToast } = useToast()

  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<Route | null>(null)
  const [form, setForm] = useState<RoutePayload>(emptyForm)
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [deleteTarget, setDeleteTarget] = useState<Route | null>(null)

  const { data: routes = [], isLoading } = useQuery({
    queryKey: ['routes', search],
    queryFn: () => getRoutes(search),
  })

  const createMut = useMutation({
    mutationFn: createRoute,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['routes'] })
      showToast('Route created successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to create route', 'error'),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: RoutePayload }) =>
      updateRoute(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['routes'] })
      showToast('Route updated successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to update route', 'error'),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteRoute(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['routes'] })
      showToast('Route deleted successfully', 'success')
      setDeleteTarget(null)
    },
    onError: () => showToast('Failed to delete route', 'error'),
  })

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormErrors({})
    setIsModalOpen(true)
  }

  const openEdit = (route: Route) => {
    setEditing(route)
    setForm({
      route_name: route.route_name,
    })
    setFormErrors({})
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditing(null)
    setForm(emptyForm)
    setFormErrors({})
  }

  const validate = (): boolean => {
    const errs: FormErrors = {}
    if (!form.route_name.trim()) errs.route_name = 'Route name is required'
    setFormErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    if (editing) {
      updateMut.mutate({ id: editing.id || editing.route_id, payload: form })
    } else {
      createMut.mutate(form)
    }
  }

  const columns: Column<Route>[] = [
    {
      key: 'route_id',
      header: 'Route ID',
      render: (r) => <span className="font-mono text-xs text-slate-500">#{r.id || r.route_id}</span>,
    },
    {
      key: 'route_name',
      header: 'Route Name',
      render: (r) => <span className="font-semibold text-slate-800">{r.route_name}</span>,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r) => (
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => openEdit(r)}
            className="text-slate-600 hover:text-sky-600"
          >
            <Pencil size={15} />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setDeleteTarget(r)}
            className="text-slate-600 hover:text-rose-600"
          >
            <Trash2 size={15} />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Designated Routes</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage school transport paths across city and suburban sectors.
          </p>
        </div>
        <Button onClick={openCreate} className="flex items-center gap-2">
          <Plus size={18} />
          Add New Route
        </Button>
      </div>

      {/* Search Bar */}
      <div className="w-full max-w-sm">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder="Search by route name..."
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <Table columns={columns} data={routes} keyField="route_id" />
      )}

      {/* Add / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editing ? 'Edit Route' : 'Create New Route'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Route Name *"
            placeholder="e.g. Vasant Kunj - Route A"
            value={form.route_name}
            onChange={(e) => setForm({ ...form, route_name: e.target.value })}
            error={formErrors.route_name}
          />
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
            <Button type="button" variant="ghost" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMut.isPending || updateMut.isPending}
            >
              {editing ? 'Save Changes' : 'Create Route'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="Confirm Delete Route"
      >
        <p className="text-sm text-slate-600">
          Are you sure you want to delete route{' '}
          <strong className="text-slate-800">{deleteTarget?.route_name}</strong>?
          This will unassign all buses and students associated with this route.
        </p>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="ghost" onClick={() => setDeleteTarget(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            disabled={deleteMut.isPending}
            onClick={() => deleteTarget && deleteMut.mutate(deleteTarget.id || deleteTarget.route_id)}
          >
            {deleteMut.isPending ? 'Deleting...' : 'Delete Route'}
          </Button>
        </div>
      </Modal>
    </div>
  )
}

