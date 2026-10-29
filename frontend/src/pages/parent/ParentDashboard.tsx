import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bus, MapPin, Phone, User, Calendar, CreditCard, Send, CheckCircle2 } from 'lucide-react'
import { getMyChildren, type Child } from '../../api/parents'
import { createRequest } from '../../api/requests'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Input } from '../../components/ui/Input'
import { Badge } from '../../components/ui/Badge'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'
import { useAuth } from '../../hooks/useAuth'

export default function ParentDashboard() {
  const { user } = useAuth()
  const qc = useQueryClient()
  const { showToast } = useToast()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedStudentId, setSelectedStudentId] = useState<number>(0)
  const [newPickupPoint, setNewPickupPoint] = useState('')
  const [error, setError] = useState('')

  const { data: children = [], isLoading } = useQuery({
    queryKey: ['my-children'],
    queryFn: getMyChildren,
  })

  const requestMut = useMutation({
    mutationFn: createRequest,
    onSuccess: () => {
      showToast('Transport change request submitted successfully!', 'success')
      closeModal()
    },
    onError: () => {
      showToast('Failed to submit transport request', 'error')
    },
  })

  const openModal = (studentId?: number) => {
    if (studentId) {
      setSelectedStudentId(studentId)
    } else if (children.length > 0) {
      setSelectedStudentId(children[0].id || children[0].student_id)
    }
    setNewPickupPoint('')
    setError('')
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setNewPickupPoint('')
    setError('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newPickupPoint.trim()) {
      setError('Please specify the new pickup point')
      return
    }
    if (!selectedStudentId) {
      setError('Please select a student')
      return
    }
    requestMut.mutate({
      student_id: selectedStudentId,
      requested_pickup_point: newPickupPoint,
    })
  }

  const totalBalance = children.reduce((sum, c) => sum + (c.fee_balance || 0), 0)

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-slate-900 to-slate-800 p-6 rounded-2xl text-white shadow-sm">
        <div>
          <span className="text-xs uppercase tracking-wider text-sky-400 font-semibold">
            Parent Portal
          </span>
          <h1 className="text-2xl font-bold mt-1">Welcome, {user?.name || 'Parent'}</h1>
          <p className="text-sm text-slate-300 mt-1">
            Track your children's school transport routes, designated pickup stops, and fee status.
          </p>
        </div>
        <Button
          onClick={() => openModal()}
          className="bg-sky-500 hover:bg-sky-400 text-white flex items-center gap-2 self-start sm:self-auto"
        >
          <Send size={16} />
          Request Pickup Change
        </Button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase">Enrolled Children</span>
          <p className="text-2xl font-bold text-slate-800 mt-2">{children.length}</p>
          <span className="text-xs text-slate-400 mt-1 block">Active student transport profiles</span>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase">Active Buses</span>
          <p className="text-2xl font-bold text-slate-800 mt-2">
            {new Set(children.map((c) => c.bus_number).filter(Boolean)).size}
          </p>
          <span className="text-xs text-slate-400 mt-1 block">Assigned school transport fleet</span>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase">Fee Status</span>
          <p
            className={`text-2xl font-bold mt-2 ${
              totalBalance > 0 ? 'text-rose-600' : 'text-emerald-600'
            }`}
          >
            {totalBalance > 0 ? `₹${totalBalance.toLocaleString()}` : 'Cleared'}
          </p>
          <span className="text-xs text-slate-400 mt-1 block">
            {totalBalance > 0 ? 'Total outstanding balance' : 'All student fee accounts paid'}
          </span>
        </div>
      </div>

      {/* Children Cards */}
      <div>
        <h2 className="text-lg font-bold text-slate-800 mb-4">Children's Transport Details</h2>

        {isLoading ? (
          <div className="py-20 flex justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : children.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <User size={36} className="text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-700">No children linked</h3>
            <p className="text-sm text-slate-500 mt-1">
              Please contact the school transport administrator to link your children.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5">
            {children.map((c) => {
              const childId = c.id || c.student_id
              const childName = c.name || c.student_name
              const childClass = c.class_name || c.student_class
              const hasBalance = (c.fee_balance || 0) > 0

              return (
                <div
                  key={childId}
                  className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow"
                >
                  {/* Top Bar: Name, Class, Fee Badge */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 gap-2">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-base">
                        {childName.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-800">{childName}</h3>
                        <p className="text-xs text-slate-500 font-medium">Class {childClass}</p>
                      </div>
                    </div>
                    <div>
                      {hasBalance ? (
                        <Badge variant="danger">Balance: ₹{c.fee_balance}</Badge>
                      ) : (
                        <Badge variant="success">✓ Fees Paid</Badge>
                      )}
                    </div>
                  </div>

                  {/* Details Grid: Bus, Route, Pickup Point */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-4">
                    {/* Bus & Driver Details */}
                    <div className="space-y-2.5">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                        Assigned Bus Service
                      </span>
                      <div className="flex items-center gap-2 text-sm text-slate-700">
                        <Bus size={16} className="text-slate-400" />
                        <span className="font-semibold text-slate-800">
                          {c.bus_number || 'Unassigned'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-slate-700">
                        <User size={16} className="text-slate-400" />
                        <span>Driver: {c.driver_name || 'N/A'}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-slate-700">
                        <Phone size={16} className="text-slate-400" />
                        <span>Contact: {c.driver_phone || 'N/A'}</span>
                      </div>
                    </div>

                    {/* Route & Pickup Stop */}
                    <div className="space-y-2.5">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                        Route & Pickup Location
                      </span>
                      <div className="flex items-center gap-2 text-sm text-slate-700">
                        <MapPin size={16} className="text-sky-500" />
                        <span>
                          Route:{' '}
                          <strong className="text-slate-800">{c.route_name || 'Unassigned'}</strong>
                        </span>
                      </div>
                      <div className="flex items-start gap-2 text-sm text-slate-700">
                        <MapPin size={16} className="text-emerald-500 mt-0.5" />
                        <span>
                          Designated Stop:{' '}
                          <strong className="text-slate-800">
                            {c.pickup_point || 'Not assigned'}
                          </strong>
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-slate-700">
                        <CreditCard size={16} className="text-slate-400" />
                        <span>
                          Paid: ₹{c.fee_paid} • Balance: ₹{c.fee_balance}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Actions Footer */}
                  <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
                    <p className="text-xs text-slate-400">
                      Need to update this child's pickup point?
                    </p>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => openModal(childId)}
                      className="text-xs flex items-center gap-1.5"
                    >
                      <MapPin size={14} />
                      Request Different Pickup
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Change Request Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title="Request Transport Pickup Change"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-sm text-slate-600">
            Submit a request to change your child's designated bus pickup or drop-off location.
          </p>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700">Select Child *</label>
            <select
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(parseInt(e.target.value))}
            >
              {children.map((c) => (
                <option key={c.id || c.student_id} value={c.id || c.student_id}>
                  {c.name || c.student_name} (Class {c.class_name || c.student_class})
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Requested Pickup Stop *"
            placeholder="e.g. Near Big Banyan Tree, North Gate"
            value={newPickupPoint}
            onChange={(e) => setNewPickupPoint(e.target.value)}
            error={error}
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
            <Button type="button" variant="ghost" onClick={closeModal}>
              Cancel
            </Button>
            <Button type="submit" disabled={requestMut.isPending}>
              {requestMut.isPending ? 'Submitting...' : 'Submit Request'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

