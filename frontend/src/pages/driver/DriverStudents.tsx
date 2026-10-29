import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, X, CheckCheck, Phone, MapPin, Calendar } from 'lucide-react'
import {
  getDriverStudents,
  markAttendance,
  type StudentForDriver,
} from '../../api/attendance'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'

export default function DriverStudents() {
  const qc = useQueryClient()
  const { showToast } = useToast()

  const todayStr = new Date().toISOString().split('T')[0]
  const [selectedDate, setSelectedDate] = useState<string>(todayStr)
  // Local state for tracking marked attendance statuses
  const [statusMap, setStatusMap] = useState<Record<number, 'Present' | 'Absent'>>({})

  const { data: students = [], isLoading } = useQuery({
    queryKey: ['driver-students'],
    queryFn: getDriverStudents,
  })

  const markMut = useMutation({
    mutationFn: markAttendance,
    onSuccess: () => {
      showToast('Attendance recorded successfully', 'success')
      qc.invalidateQueries({ queryKey: ['driver-students'] })
    },
    onError: () => {
      showToast('Failed to record attendance', 'error')
    },
  })

  const handleMarkOne = (studentId: number, status: 'Present' | 'Absent') => {
    setStatusMap((prev) => ({ ...prev, [studentId]: status }))
    markMut.mutate({
      date: selectedDate,
      records: [{ student_id: studentId, status }],
    })
  }

  const handleMarkAllPresent = () => {
    const newStatuses: Record<number, 'Present'> = {}
    const records = students.map((s) => {
      newStatuses[s.student_id] = 'Present'
      return { student_id: s.student_id, status: 'Present' }
    })
    setStatusMap((prev) => ({ ...prev, ...newStatuses }))
    markMut.mutate({
      date: selectedDate,
      records,
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-slate-900 to-slate-800 p-6 rounded-2xl text-white shadow-sm">
        <div>
          <span className="text-xs uppercase tracking-wider text-amber-400 font-semibold">
            Driver Operations Portal
          </span>
          <h1 className="text-2xl font-bold mt-1">My Route Students</h1>
          <p className="text-sm text-slate-300 mt-1">
            Mark daily transport boarding status for students assigned to your bus.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg text-sm">
            <Calendar size={15} className="text-slate-400" />
            <input
              type="date"
              className="bg-transparent text-white text-xs font-semibold focus:outline-none"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>
          <Button
            onClick={handleMarkAllPresent}
            disabled={markMut.isPending || students.length === 0}
            className="bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1.5"
          >
            <CheckCheck size={16} />
            Mark All Present
          </Button>
        </div>
      </div>

      {/* Student List */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : students.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <h3 className="text-base font-semibold text-slate-700">No students found</h3>
          <p className="text-sm text-slate-500 mt-1">
            No students are currently allocated to this bus route.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              {students.length} Allocated Students
            </span>
            <span className="text-xs text-slate-500">Trip Date: {selectedDate}</span>
          </div>

          <div className="divide-y divide-slate-100">
            {students.map((s) => {
              const currentStatus = statusMap[s.student_id]
              return (
                <div
                  key={s.student_id}
                  className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 transition-colors"
                >
                  {/* Student & Stop info */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-800 text-base">{s.student_name}</span>
                      <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
                        Class {s.student_class}
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                      <span className="flex items-center gap-1 text-slate-700 font-medium">
                        <MapPin size={13} className="text-sky-500" />
                        Stop: {s.pickup_point || 'Not specified'}
                      </span>
                      {s.phone && (
                        <a
                          href={`tel:${s.phone}`}
                          className="flex items-center gap-1 text-sky-600 hover:underline"
                        >
                          <Phone size={13} />
                          {s.phone} ({s.parent_name || 'Parent'})
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Attendance Actions */}
                  <div className="flex items-center gap-2">
                    {currentStatus && (
                      <Badge variant={currentStatus === 'Present' ? 'success' : 'danger'}>
                        {currentStatus}
                      </Badge>
                    )}
                    <Button
                      size="sm"
                      variant={currentStatus === 'Present' ? 'primary' : 'secondary'}
                      onClick={() => handleMarkOne(s.student_id, 'Present')}
                      className={`flex items-center gap-1 ${
                        currentStatus === 'Present'
                          ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                          : 'hover:border-emerald-500 hover:text-emerald-600'
                      }`}
                    >
                      <Check size={14} />
                      Present
                    </Button>
                    <Button
                      size="sm"
                      variant={currentStatus === 'Absent' ? 'danger' : 'secondary'}
                      onClick={() => handleMarkOne(s.student_id, 'Absent')}
                      className={`flex items-center gap-1 ${
                        currentStatus === 'Absent'
                          ? 'bg-rose-600 hover:bg-rose-700 text-white'
                          : 'hover:border-rose-500 hover:text-rose-600'
                      }`}
                    >
                      <X size={14} />
                      Absent
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

