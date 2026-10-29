import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CalendarCheck, CheckCircle2, XCircle } from 'lucide-react'
import { getMyChildren } from '../../api/parents'
import { getStudentAttendance, type StudentAttendanceHistory } from '../../api/attendance'
import { Badge } from '../../components/ui/Badge'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

export default function ParentAttendance() {
  const { data: children = [], isLoading: loadingChildren } = useQuery({
    queryKey: ['my-children'],
    queryFn: getMyChildren,
  })

  const [selectedChildId, setSelectedChildId] = useState<number | null>(null)

  // Default to first child when data arrives
  const activeChildId =
    selectedChildId !== null
      ? selectedChildId
      : children.length > 0
      ? children[0].id || children[0].student_id
      : null

  const { data: records = [], isLoading: loadingAttendance } = useQuery({
    queryKey: ['attendance-child', activeChildId],
    queryFn: () => (activeChildId ? getStudentAttendance(activeChildId) : Promise.resolve([])),
    enabled: !!activeChildId,
  })

  const activeChild = children.find(
    (c) => (c.id || c.student_id) === activeChildId
  )

  const presentCount = records.filter(
    (r) => r.attendance_status?.toLowerCase() === 'present'
  ).length
  const attendanceRate = records.length > 0 ? Math.round((presentCount / records.length) * 100) : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Boarding & Attendance Logs</h1>
        <p className="text-sm text-slate-500 mt-1">
          Daily bus boarding records logged by the bus driver.
        </p>
      </div>

      {loadingChildren ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : children.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <p className="text-sm text-slate-500">No linked children found.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Child selector tabs */}
          <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
            {children.map((c) => {
              const id = c.id || c.student_id
              const isSelected = id === activeChildId
              return (
                <button
                  key={id}
                  onClick={() => setSelectedChildId(id)}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 ${
                    isSelected
                      ? 'bg-sky-500 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <span>{c.name || c.student_name}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      isSelected ? 'bg-sky-600 text-white' : 'bg-slate-200 text-slate-600'
                    }`}
                  >
                    Class {c.class_name || c.student_class}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Child stats banner */}
          {activeChild && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-400 uppercase">Attendance Rate</span>
                <p className="text-2xl font-bold text-slate-800 mt-1">{attendanceRate}%</p>
                <span className="text-xs text-slate-500 mt-0.5 block">Last 30 recorded trips</span>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-400 uppercase">Days Present</span>
                <p className="text-2xl font-bold text-emerald-600 mt-1">{presentCount}</p>
                <span className="text-xs text-slate-500 mt-0.5 block">Boarded the bus successfully</span>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-400 uppercase">Days Absent</span>
                <p className="text-2xl font-bold text-rose-600 mt-1">{records.length - presentCount}</p>
                <span className="text-xs text-slate-500 mt-0.5 block">Did not board transport</span>
              </div>
            </div>
          )}

          {/* Records Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-800 text-sm">
                Attendance Log for {activeChild?.name || activeChild?.student_name}
              </h3>
              <span className="text-xs text-slate-400">{records.length} records found</span>
            </div>

            {loadingAttendance ? (
              <div className="py-12 flex justify-center">
                <LoadingSpinner size="md" />
              </div>
            ) : records.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-500">
                No attendance logs found for this student.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {records.map((r, i) => {
                  const isPresent = r.attendance_status?.toLowerCase() === 'present'
                  return (
                    <div
                      key={i}
                      className="px-5 py-3.5 flex items-center justify-between hover:bg-slate-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            isPresent ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
                          }`}
                        >
                          {isPresent ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div>
                          <span className="text-sm font-semibold text-slate-800 font-mono">
                            {r.date}
                          </span>
                          <span className="block text-xs text-slate-400">School Bus Transport</span>
                        </div>
                      </div>
                      <Badge variant={isPresent ? 'success' : 'danger'}>
                        {isPresent ? 'Present' : 'Absent'}
                      </Badge>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

