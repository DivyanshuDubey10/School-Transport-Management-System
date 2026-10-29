import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CalendarCheck } from 'lucide-react'
import { getAttendance, type AttendanceRecord } from '../../api/attendance'
import { Table, type Column } from '../../components/ui/Table'
import { Badge } from '../../components/ui/Badge'
import { SearchBar } from '../../components/ui/SearchBar'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

export default function Attendance() {
  const [search, setSearch] = useState('')

  const { data: records = [], isLoading } = useQuery({
    queryKey: ['attendance', search],
    queryFn: () => getAttendance(search),
  })

  const columns: Column<AttendanceRecord>[] = [
    {
      key: 'date',
      header: 'Date',
      render: (r) => <span className="font-mono text-xs text-slate-600">{r.date}</span>,
    },
    {
      key: 'student_name',
      header: 'Student Name',
      render: (r) => <span className="font-semibold text-slate-800">{r.student_name}</span>,
    },
    {
      key: 'student_class',
      header: 'Class',
      render: (r) => <span className="text-slate-600">Class {r.student_class}</span>,
    },
    {
      key: 'bus_number',
      header: 'Bus Vehicle',
      render: (r) => (
        <span className="inline-flex items-center gap-1.5 font-medium text-slate-700">
          🚌 {r.bus_number}
        </span>
      ),
    },
    {
      key: 'attendance_status',
      header: 'Status',
      render: (r) => {
        const status = r.attendance_status || r.status || ''
        const isPresent = status.toLowerCase() === 'present'
        return (
          <Badge variant={isPresent ? 'success' : 'danger'}>
            {isPresent ? '✓ Present' : '✗ Absent'}
          </Badge>
        )
      },
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Student Attendance Records</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time daily boarding and attendance records logged by bus drivers.
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="w-full max-w-sm">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder="Filter by student or bus number..."
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <Table columns={columns} data={records} keyField="date" />
      )}
    </div>
  )
}

