import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import {
  getBuses,
  createBus,
  updateBus,
  deleteBus,
  type Bus,
  type BusPayload,
} from '../../api/buses'
import { getRoutes } from '../../api/routes'
import { Table, type Column } from '../../components/ui/Table'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { SearchBar } from '../../components/ui/SearchBar'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'

type FormErrors = Partial<Record<keyof BusPayload | 'root', string>>

const emptyForm: BusPayload = {
  bus_number: '',
  driver_name: '',
  driver_phone: '',
  capacity: 40,
  route_id: null,
  driver_username: '',
  driver_password: '',
}

export default function Buses() {
  const qc = useQueryClient()
  const { showToast } = useToast()

  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<Bus | null>(null)
  const [form, setForm] = useState<BusPayload>(emptyForm)
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [deleteTarget, setDeleteTarget] = useState<Bus | null>(null)

  const { data: buses = [], isLoading } = useQuery({
    queryKey: ['buses', search],
    queryFn: () => getBuses(search),
  })

  const { data: routes = [] } = useQuery({
    queryKey: ['routes'],
    queryFn: () => getRoutes(),
  })

  const createMut = useMutation({
    mutationFn: createBus,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['buses'] })
      showToast('Bus registered successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to register bus', 'error'),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<BusPayload> }) =>
      updateBus(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['buses'] })
      showToast('Bus updated successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to update bus', 'error'),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteBus(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['buses'] })
      showToast('Bus deleted successfully', 'success')
      setDeleteTarget(null)
    },
    onError: () => showToast('Failed to delete bus', 'error'),
  })

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormErrors({})
    setIsModalOpen(true)
  }

  const openEdit = (bus: Bus) => {
    setEditing(bus)
    setForm({
      bus_number: bus.bus_number,
      driver_name: bus.driver_name,
      driver_phone: bus.driver_phone,
      capacity: bus.capacity,
      route_id: bus.route_id,
      driver_username: bus.driver_username || bus.username || '',
      driver_password: '',
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
    if (!form.bus_number.trim()) errs.bus_number = 'Bus number is required'
    if (!form.driver_name.trim()) errs.driver_name = 'Driver name is required'
    if (!form.driver_phone.trim()) errs.driver_phone = 'Driver phone is required'
    if (!form.capacity || form.capacity <= 0) errs.capacity = 'Capacity must be greater than 0'
    setFormErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    if (editing) {
      updateMut.mutate({ id: editing.id || editing.bus_id, payload: form })
    } else {
      createMut.mutate(form)
    }
  }

  const columns: Column<Bus>[] = [
    {
      key: 'bus_number',
      header: 'Bus Number',
      render: (b) => <span className="font-semibold text-slate-800">{b.bus_number}</span>,
    },
    {
      key: 'driver_name',
      header: 'Driver Name',
      render: (b) => b.driver_name,
    },
    {
      key: 'driver_phone',
      header: 'Driver Phone',
      render: (b) => b.driver_phone,
    },
    {
      key: 'capacity',
      header: 'Capacity',
      render: (b) => `${b.capacity} seats`,
    },
    {
      key: 'route_name',
      header: 'Assigned Route',
      render: (b) => b.route_name || <span className="text-slate-400 italic">None</span>,
    },
    {
      key: 'driver_username',
      header: 'Driver Login',
      render: (b) => b.driver_username || b.username || <span className="text-slate-400 italic">Not set</span>,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (b) => (
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => openEdit(b)}
            className="text-slate-600 hover:text-sky-600"
          >
            <Pencil size={15} />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setDeleteTarget(b)}
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
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Bus Fleet Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            Register transport vehicles, assign drivers, and manage route allocations.
          </p>
        </div>
        <Button onClick={openCreate} className="flex items-center gap-2">
          <Plus size={18} />
          Add New Bus
        </Button>
      </div>

      {/* Search Bar */}
      <div className="w-full max-w-sm">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder="Search by bus number, driver, or route..."
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <Table columns={columns} data={buses} keyField="bus_id" />
      )}

      {/* Add / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editing ? 'Edit Bus Information' : 'Register New Bus'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Bus Number *"
            placeholder="e.g. DL 1P 1001"
            value={form.bus_number}
            onChange={(e) => setForm({ ...form, bus_number: e.target.value })}
            error={formErrors.bus_number}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Driver Name *"
              placeholder="e.g. Rajesh Sharma"
              value={form.driver_name}
              onChange={(e) => setForm({ ...form, driver_name: e.target.value })}
              error={formErrors.driver_name}
            />
            <Input
              label="Driver Phone *"
              placeholder="e.g. 9876543210"
              value={form.driver_phone}
              onChange={(e) => setForm({ ...form, driver_phone: e.target.value })}
              error={formErrors.driver_phone}
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Passenger Capacity *"
              type="number"
              placeholder="40"
              value={form.capacity}
              onChange={(e) => setForm({ ...form, capacity: parseInt(e.target.value) || 0 })}
              error={formErrors.capacity}
            />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Assigned Route</label>
              <select
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
                value={form.route_id || ''}
                onChange={(e) =>
                  setForm({ ...form, route_id: e.target.value ? parseInt(e.target.value) : null })
                }
              >
                <option value="">-- Select a Route --</option>
                {routes.map((r) => (
                  <option key={r.id || r.route_id} value={r.id || r.route_id}>
                    {r.route_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="border-t border-slate-200 pt-4 mt-2">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
              Driver Login Credentials (Optional)
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Driver Username"
                placeholder="e.g. driver_rajesh"
                value={form.driver_username || ''}
                onChange={(e) => setForm({ ...form, driver_username: e.target.value })}
              />
              <Input
                label={editing ? 'New Password (leave empty to keep)' : 'Driver Password'}
                type="password"
                placeholder="••••••••"
                value={form.driver_password || ''}
                onChange={(e) => setForm({ ...form, driver_password: e.target.value })}
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
            <Button type="button" variant="ghost" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMut.isPending || updateMut.isPending}
            >
              {editing ? 'Save Changes' : 'Register Bus'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="Confirm Delete"
      >
        <p className="text-sm text-slate-600">
          Are you sure you want to delete bus{' '}
          <strong className="text-slate-800">{deleteTarget?.bus_number}</strong>?
          This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="ghost" onClick={() => setDeleteTarget(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            disabled={deleteMut.isPending}
            onClick={() => deleteTarget && deleteMut.mutate(deleteTarget.id || deleteTarget.bus_id)}
          >
            {deleteMut.isPending ? 'Deleting...' : 'Delete Bus'}
          </Button>
        </div>
      </Modal>
    </div>
  )
}

