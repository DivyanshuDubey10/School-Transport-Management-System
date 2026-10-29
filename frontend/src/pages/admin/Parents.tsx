import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import {
  getParents,
  createParent,
  updateParent,
  deleteParent,
  type Parent,
  type ParentPayload,
} from '../../api/parents'
import { Table, type Column } from '../../components/ui/Table'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { SearchBar } from '../../components/ui/SearchBar'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'

type FormErrors = Partial<Record<keyof ParentPayload | 'root', string>>

const emptyForm: ParentPayload = {
  name: '',
  phone: '',
  address: '',
  pickup_point: '',
  username: '',
  password: '',
}

export default function Parents() {
  const qc = useQueryClient()
  const { showToast } = useToast()

  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<Parent | null>(null)
  const [form, setForm] = useState<ParentPayload>(emptyForm)
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [deleteTarget, setDeleteTarget] = useState<Parent | null>(null)

  const { data: parents = [], isLoading } = useQuery<Parent[]>({
    queryKey: ['parents'],
    queryFn: () => getParents(),
  })

  const createMut = useMutation({
    mutationFn: createParent,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parents'] })
      showToast('Parent registered successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to register parent', 'error'),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<ParentPayload> }) =>
      updateParent(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parents'] })
      showToast('Parent updated successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to update parent', 'error'),
  })

  const deleteMut = useMutation({
    mutationFn: deleteParent,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parents'] })
      showToast('Parent removed', 'success')
      setDeleteTarget(null)
    },
    onError: () => showToast('Failed to delete parent', 'error'),
  })

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormErrors({})
    setIsModalOpen(true)
  }

  const openEdit = (p: Parent) => {
    setEditing(p)
    setForm({
      name: p.name || p.parent_name,
      phone: p.phone,
      address: p.address,
      pickup_point: p.pickup_point,
      username: p.username,
      password: '',
    })
    setFormErrors({})
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditing(null)
    setFormErrors({})
  }

  const validate = (): boolean => {
    const e: FormErrors = {}
    if (!form.name?.trim()) e.name = 'Name is required'
    if (!form.phone?.trim()) e.phone = 'Phone number is required'
    if (!form.address?.trim()) e.address = 'Address is required'
    if (!form.pickup_point?.trim()) e.pickup_point = 'Pickup point is required'
    if (!form.username?.trim()) e.username = 'Username is required'
    if (!editing && !form.password?.trim()) e.password = 'Password is required'
    setFormErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = () => {
    if (!validate()) return
    if (editing) {
      updateMut.mutate({ id: editing.id || editing.parent_id, payload: form })
    } else {
      createMut.mutate(form)
    }
  }

  const handleSearch = useCallback((v: string) => setSearch(v), [])

  const filtered = parents.filter(
    (p: Parent) =>
      (p.name || p.parent_name || '').toLowerCase().includes(search.toLowerCase()) ||
      (p.phone ?? '').includes(search) ||
      (p.pickup_point ?? '').toLowerCase().includes(search.toLowerCase()) ||
      (p.username ?? '').toLowerCase().includes(search.toLowerCase()),
  )

  const columns: Column<Parent>[] = [
    { key: 'id', header: 'ID', sortable: true, className: 'w-16' },
    {
      key: 'name',
      header: 'Parent Name',
      sortable: true,
      render: (r) => <span className="font-medium text-slate-800">{r.name || r.parent_name}</span>,
    },
    { key: 'phone', header: 'Phone', sortable: true },
    { key: 'address', header: 'Address' },
    {
      key: 'pickup_point',
      header: 'Pickup Point',
      render: (r) => (
        <span className="inline-flex items-center gap-1.5 font-medium text-sky-700 bg-sky-50 px-2.5 py-0.5 rounded-full text-xs">
          📍 {r.pickup_point}
        </span>
      ),
    },
    { key: 'username', header: 'Username', className: 'text-slate-400 font-mono text-xs' },
    {
      key: 'actions',
      header: '',
      className: 'w-20 text-right',
      render: (r) => (
        <div className="flex items-center justify-end gap-1">
          <button
            onClick={() => openEdit(r)}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
            title="Edit"
          >
            <Pencil size={15} />
          </button>
          <button
            onClick={() => setDeleteTarget(r)}
            className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
            title="Delete"
          >
            <Trash2 size={15} />
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Parents</h1>
          <p className="text-sm text-slate-500 mt-0.5">Manage parent accounts, contact details, and pickup points</p>
        </div>
        <Button onClick={openCreate} className="flex items-center gap-2">
          <Plus size={16} /> Register Parent
        </Button>
      </div>

      {/* Search */}
      <div className="w-full sm:w-72">
        <SearchBar placeholder="Search parents…" onSearch={handleSearch} />
      </div>

      {/* Table */}
      <Table<Parent>
        columns={columns}
        data={filtered}
        isLoading={isLoading}
        keyExtractor={(r) => r.id || r.parent_id}
        emptyMessage="No parents found."
      />

      {/* Register / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editing ? 'Edit Parent' : 'Register Parent Account'}
        description={editing ? 'Update parent contact and login details.' : 'Fill in the information to create a parent account.'}
      >
        <div className="space-y-4">
          <Input
            label="Full Name"
            placeholder="e.g. Priya Sharma"
            value={form.name || ''}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            error={formErrors.name}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Phone Number"
              placeholder="e.g. 9876543210"
              value={form.phone || ''}
              onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              error={formErrors.phone}
              required
            />
            <Input
              label="Designated Pickup Point"
              placeholder="e.g. Sector 10 Market"
              value={form.pickup_point || ''}
              onChange={(e) => setForm((f) => ({ ...f, pickup_point: e.target.value }))}
              error={formErrors.pickup_point}
              required
            />
          </div>

          <Input
            label="Residential Address"
            placeholder="e.g. 42, Vasant Kunj, New Delhi"
            value={form.address || ''}
            onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))}
            error={formErrors.address}
            required
          />

          <div className="grid grid-cols-2 gap-3 border-t border-slate-100 pt-3">
            <Input
              label="Username"
              placeholder="e.g. parent12"
              value={form.username || ''}
              onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
              error={formErrors.username}
              required
            />
            <Input
              label={editing ? 'Password (leave blank to keep)' : 'Password'}
              type="password"
              placeholder="••••••••"
              value={form.password || ''}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              error={formErrors.password}
              required={!editing}
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              loading={createMut.isPending || updateMut.isPending}
            >
              {editing ? 'Save Changes' : 'Register Parent'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        title="Delete Parent"
        description="Are you sure you want to remove this parent? All linked students will also be deleted."
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-600">
            You are about to delete{' '}
            <span className="font-semibold text-slate-800">
              {deleteTarget?.name || deleteTarget?.parent_name}
            </span>
            .
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={deleteMut.isPending}
              onClick={() => deleteTarget && deleteMut.mutate(deleteTarget.id || deleteTarget.parent_id)}
            >
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
