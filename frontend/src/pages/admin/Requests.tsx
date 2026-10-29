import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, XCircle, MapPin } from 'lucide-react'
import {
  getRequests,
  approveRequest,
  rejectRequest,
  type TransportRequest,
} from '../../api/requests'
import { getRoutes } from '../../api/routes'
import { Table, type Column } from '../../components/ui/Table'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'

export default function Requests() {
  const qc = useQueryClient()
  const { showToast } = useToast()

  const [approveTarget, setApproveTarget] = useState<TransportRequest | null>(null)
  const [rejectTarget, setRejectTarget] = useState<TransportRequest | null>(null)
  const [selectedRouteId, setSelectedRouteId] = useState<number>(1)
  const [customPickup, setCustomPickup] = useState<string>('')

  const { data: requests = [], isLoading } = useQuery({
    queryKey: ['requests'],
    queryFn: getRequests,
  })

  const { data: routes = [] } = useQuery({
    queryKey: ['routes'],
    queryFn: () => getRoutes(),
  })

  const approveMut = useMutation({
    mutationFn: ({ id, routeId, pickup }: { id: number; routeId: number; pickup: string }) =>
      approveRequest(id, { new_route_id: routeId, new_pickup_point: pickup }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['requests'] })
      showToast('Transport request approved successfully', 'success')
      setApproveTarget(null)
    },
    onError: () => showToast('Failed to approve request', 'error'),
  })

  const rejectMut = useMutation({
    mutationFn: (id: number) => rejectRequest(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['requests'] })
      showToast('Transport request rejected', 'info')
      setRejectTarget(null)
    },
    onError: () => showToast('Failed to reject request', 'error'),
  })

  const openApproveModal = (req: TransportRequest) => {
    setApproveTarget(req)
    setCustomPickup(req.requested_pickup_point)
    if (routes.length > 0) {
      setSelectedRouteId(routes[0].id || routes[0].route_id)
    }
  }

  const columns: Column<TransportRequest>[] = [
    {
      key: 'student_name',
      header: 'Student',
      render: (r) => (
        <div>
          <span className="font-semibold text-slate-800">{r.student_name}</span>
          <span className="block text-xs text-slate-500">Class {r.student_class || r.class_name}</span>
        </div>
      ),
    },
    {
      key: 'parent_name',
      header: 'Parent Account',
      render: (r) => r.parent_name,
    },
    {
      key: 'requested_pickup_point',
      header: 'Requested Pickup Stop',
      render: (r) => (
        <span className="inline-flex items-center gap-1.5 font-medium text-slate-800 bg-sky-50 text-sky-700 px-2.5 py-1 rounded-md text-xs">
          <MapPin size={13} />
          {r.requested_pickup_point}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (r) => <Badge variant="warning">{r.request_status || r.status || 'Pending'}</Badge>,
    },
    {
      key: 'actions',
      header: 'Review Actions',
      render: (r) => (
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="primary"
            onClick={() => openApproveModal(r)}
            className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white"
          >
            <CheckCircle size={14} />
            Approve
          </Button>
          <Button
            size="sm"
            variant="danger"
            onClick={() => setRejectTarget(r)}
            className="flex items-center gap-1"
          >
            <XCircle size={14} />
            Reject
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Transport Change Requests</h1>
        <p className="text-sm text-slate-500 mt-1">
          Review pickup point changes submitted by parents and reassign student routes.
        </p>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : requests.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
            <CheckCircle size={24} />
          </div>
          <h3 className="text-base font-semibold text-slate-800">All caught up!</h3>
          <p className="text-sm text-slate-500 mt-1">There are no pending transport change requests.</p>
        </div>
      ) : (
        <Table columns={columns} data={requests} keyField="request_id" />
      )}

      {/* Approve Modal */}
      <Modal
        isOpen={!!approveTarget}
        onClose={() => setApproveTarget(null)}
        title="Approve Transport Change"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-600">
            You are approving a new pickup point for{' '}
            <strong className="text-slate-800">{approveTarget?.student_name}</strong>.
          </p>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700">Confirmed Pickup Point</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              value={customPickup}
              onChange={(e) => setCustomPickup(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700">Assign New Route</label>
            <select
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              value={selectedRouteId}
              onChange={(e) => setSelectedRouteId(parseInt(e.target.value))}
            >
              {routes.map((r) => (
                <option key={r.id || r.route_id} value={r.id || r.route_id}>
                  {r.route_name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
            <Button variant="ghost" onClick={() => setApproveTarget(null)}>
              Cancel
            </Button>
            <Button
              disabled={approveMut.isPending}
              onClick={() =>
                approveTarget &&
                approveMut.mutate({
                  id: approveTarget.id || approveTarget.request_id,
                  routeId: selectedRouteId,
                  pickup: customPickup,
                })
              }
            >
              {approveMut.isPending ? 'Approving...' : 'Confirm Approval'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Reject Modal */}
      <Modal
        isOpen={!!rejectTarget}
        onClose={() => setRejectTarget(null)}
        title="Reject Transport Request"
      >
        <p className="text-sm text-slate-600">
          Are you sure you want to reject the transport change request for{' '}
          <strong className="text-slate-800">{rejectTarget?.student_name}</strong>?
        </p>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="ghost" onClick={() => setRejectTarget(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            disabled={rejectMut.isPending}
            onClick={() =>
              rejectTarget && rejectMut.mutate(rejectTarget.id || rejectTarget.request_id)
            }
          >
            {rejectMut.isPending ? 'Rejecting...' : 'Reject Request'}
          </Button>
        </div>
      </Modal>
    </div>
  )
}

