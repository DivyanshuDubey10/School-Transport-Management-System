import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import {
  getStudents,
  createStudent,
  updateStudent,
  deleteStudent,
  type Student,
  type StudentPayload,
} from '../../api/students'
import { getParents, type Parent } from '../../api/parents'
import { getRoutes, type Route } from '../../api/routes'
import { Table, type Column } from '../../components/ui/Table'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Badge } from '../../components/ui/Badge'
import { SearchBar } from '../../components/ui/SearchBar'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'

type FormErrors = Partial<Record<keyof StudentPayload | 'root', string>>

const emptyForm: StudentPayload = {
  name: '',
  class_name: '',
  parent_id: 0,
  route_id: null,
  fee_paid: 0,
  fee_balance: 0,
}

export default function Students() {
  const qc = useQueryClient()
  const { showToast } = useToast()

  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<Student | null>(null)
  const [form, setForm] = useState<StudentPayload>(emptyForm)
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [deleteTarget, setDeleteTarget] = useState<Student | null>(null)

  const { data: students = [], isLoading } = useQuery<Student[]>({
    queryKey: ['students'],
    queryFn: () => getStudents(),
  })
  const { data: parents = [] } = useQuery<Parent[]>({
    queryKey: ['parents'],
    queryFn: () => getParents(),
  })
  const { data: routes = [] } = useQuery<Route[]>({
    queryKey: ['routes'],
    queryFn: () => getRoutes(),
  })

  const createMut = useMutation({
    mutationFn: createStudent,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['students'] })
      showToast('Student enrolled successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to enroll student', 'error'),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<StudentPayload> }) =>
      updateStudent(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['students'] })
      showToast('Student updated successfully', 'success')
      closeModal()
    },
    onError: () => showToast('Failed to update student', 'error'),
  })

  const deleteMut = useMutation({
    mutationFn: deleteStudent,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['students'] })
      showToast('Student removed', 'success')
      setDeleteTarget(null)
    },
    onError: () => showToast('Failed to delete student', 'error'),
  })

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormErrors({})
    setIsModalOpen(true)
  }

  const openEdit = (s: Student) => {
    setEditing(s)
    setForm({
      name: s.name || s.student_name,
      class_name: s.class_name || s.student_class,
      parent_id: s.parent_id,
      route_id: s.route_id,
      fee_paid: s.fee_paid,
      fee_balance: s.fee_balance,
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
    if (!form.class_name?.trim()) e.class_name = 'Class is required'
    if (!form.parent_id) e.parent_id = 'Parent is required'
    setFormErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = () => {
    if (!validate()) return
    if (editing) {
      updateMut.mutate({ id: editing.id || editing.student_id, payload: form })
    } else {
      createMut.mutate(form)
    }
  }

  const handleSearch = useCallback((v: string) => setSearch(v), [])

  const filtered = students.filter(
    (s: Student) =>
      (s.name || s.student_name || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.class_name || s.student_class || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.parent_phone ?? s.phone ?? '').includes(search),
  )

  const statusVariant = (status: string) => {
    const lower = (status || '').toLowerCase()
    if (lower === 'active') return 'success'
    if (lower === 'pending') return 'warning'
    return 'neutral'
  }

  const columns: Column<Student>[] = [
    { key: 'id', header: 'ID', sortable: true, className: 'w-16' },
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      render: (r) => <span className="font-medium text-slate-800">{r.name || r.student_name}</span>,
    },
    {
      key: 'class_name',
      header: 'Class',
      sortable: true,
      render: (r) => r.class_name || r.student_class,
    },
    {
      key: 'parent_phone',
      header: 'Parent Phone',
      render: (r) => r.parent_phone ?? r.phone ?? '—',
    },
    {
      key: 'route_name',
      header: 'Route',
      render: (r) => {
        const found = routes.find((rt) => (rt.id || rt.route_id) === r.route_id)
        return r.route_name || found?.route_name || <span className="text-slate-400">Unassigned</span>
      },
    },
    {
      key: 'fee_paid',
      header: 'Fee Paid',
      render: (r) => (
        <span className="text-emerald-600 font-medium">₹{(r.fee_paid || 0).toLocaleString()}</span>
      ),
    },
    {
      key: 'fee_balance',
      header: 'Balance',
      render: (r) => (
        <span className={r.fee_balance > 0 ? 'text-red-500 font-medium' : 'text-slate-400'}>
          {r.fee_balance > 0 ? `₹${r.fee_balance.toLocaleString()}` : 'Nil'}
        </span>
      ),
    },
    {
      key: 'transport_status',
      header: 'Status',
      render: (r) => (
        <Badge variant={statusVariant(r.transport_status)} dot>
          {(r.transport_status || 'Active').toUpperCase()}
        </Badge>
      ),
    },
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
          <h1 className="text-2xl font-bold text-slate-800">Students</h1>
          <p className="text-sm text-slate-500 mt-0.5">Manage enrolled students and their route assignments</p>
        </div>
        <Button onClick={openCreate} className="flex items-center gap-2">
          <Plus size={16} /> Enroll Student
        </Button>
      </div>

      {/* Search */}
      <div className="w-full sm:w-72">
        <SearchBar placeholder="Search students…" onSearch={handleSearch} />
      </div>

      {/* Table */}
      <Table<Student>
        columns={columns}
        data={filtered}
        isLoading={isLoading}
        keyExtractor={(r) => r.id || r.student_id}
        emptyMessage="No students found."
      />

      {/* Enroll / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editing ? 'Edit Student' : 'Enroll New Student'}
        description={editing ? 'Update student information and route.' : 'Fill in the details to enroll a new student.'}
      >
        <div className="space-y-4">
          <Input
            label="Full Name"
            placeholder="e.g. Aarav Sharma"
            value={form.name || ''}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            error={formErrors.name}
            required
          />

          <Input
            label="Class / Grade"
            placeholder="e.g. 5A"
            value={form.class_name || ''}
            onChange={(e) => setForm((f) => ({ ...f, class_name: e.target.value }))}
            error={formErrors.class_name}
            required
          />

          {/* Parent Select */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
              Parent <span className="text-red-500">*</span>
            </label>
            <select
              value={form.parent_id || ''}
              onChange={(e) => setForm((f) => ({ ...f, parent_id: Number(e.target.value) }))}
              className={[
                'w-full px-3.5 py-2 text-sm bg-white border rounded-lg text-slate-700',
                'focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 transition-all',
                formErrors.parent_id ? 'border-red-400' : 'border-slate-200',
              ].join(' ')}
            >
              <option value="">Select a parent…</option>
              {parents.map((p: Parent) => (
                <option key={p.id || p.parent_id} value={p.id || p.parent_id}>
                  {p.name || p.parent_name} ({p.phone})
                </option>
              ))}
            </select>
            {formErrors.parent_id && <p className="text-xs text-red-500 mt-1">{formErrors.parent_id}</p>}
          </div>

          {/* Route Select */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
              Assigned Route
            </label>
            <select
              value={form.route_id ?? ''}
              onChange={(e) =>
                setForm((f) => ({ ...f, route_id: e.target.value ? Number(e.target.value) : null }))
              }
              className="w-full px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 transition-all"
            >
              <option value="">No route assigned</option>
              {routes.map((r: Route) => (
                <option key={r.id || r.route_id} value={r.id || r.route_id}>
                  {r.route_name}
                </option>
              ))}
            </select>
          </div>

          {/* Fee fields */}
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Fee Paid (₹)"
              type="number"
              min="0"
              placeholder="0"
              value={String(form.fee_paid)}
              onChange={(e) => setForm((f) => ({ ...f, fee_paid: Number(e.target.value) }))}
            />
            <Input
              label="Fee Balance (₹)"
              type="number"
              min="0"
              placeholder="0"
              value={String(form.fee_balance)}
              onChange={(e) => setForm((f) => ({ ...f, fee_balance: Number(e.target.value) }))}
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
              {editing ? 'Save Changes' : 'Enroll Student'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        title="Delete Student"
        description="Are you sure you want to remove this student? This action cannot be undone."
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-600">
            You are about to delete{' '}
            <span className="font-semibold text-slate-800">
              {deleteTarget?.name || deleteTarget?.student_name}
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
              onClick={() => deleteTarget && deleteMut.mutate(deleteTarget.id || deleteTarget.student_id)}
            >
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
