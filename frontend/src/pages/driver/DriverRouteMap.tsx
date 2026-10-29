import { useQuery } from '@tanstack/react-query'
import { MapPin, Users, Phone, Bus } from 'lucide-react'
import { getDriverStudents, type StudentForDriver } from '../../api/attendance'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

interface StopGroup {
  stopName: string
  students: StudentForDriver[]
}

export default function DriverRouteMap() {
  const { data: students = [], isLoading } = useQuery({
    queryKey: ['driver-students'],
    queryFn: getDriverStudents,
  })

  // Group students by pickup point
  const stopGroups: StopGroup[] = []
  const groupMap: Record<string, StudentForDriver[]> = {}

  for (const s of students) {
    const stop = s.pickup_point || 'General Campus Stop'
    if (!groupMap[stop]) {
      groupMap[stop] = []
    }
    groupMap[stop].push(s)
  }

  for (const [stopName, list] of Object.entries(groupMap)) {
    stopGroups.push({ stopName, students: list })
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Route Pickup Itinerary</h1>
        <p className="text-sm text-slate-500 mt-1">
          Organized sequence of designated pickup stops and assigned students along your route.
        </p>
      </div>

      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : stopGroups.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <Bus size={36} className="text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-700">No stops scheduled</h3>
          <p className="text-sm text-slate-500 mt-1">
            There are no student pickup stops assigned to this bus route.
          </p>
        </div>
      ) : (
        <div className="relative pl-6 border-l-2 border-sky-400 space-y-6 ml-3 my-4">
          {stopGroups.map((group, idx) => (
            <div key={group.stopName} className="relative">
              {/* Timeline pin */}
              <div className="absolute -left-[31px] top-1.5 w-7 h-7 rounded-full bg-sky-500 text-white flex items-center justify-center text-xs font-bold shadow-sm">
                {idx + 1}
              </div>

              {/* Stop Card */}
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 border-b border-slate-100 gap-2">
                  <div className="flex items-center gap-2">
                    <MapPin size={18} className="text-sky-500" />
                    <h3 className="font-bold text-slate-800 text-base">
                      Stop {idx + 1}: {group.stopName}
                    </h3>
                  </div>
                  <span className="text-xs bg-sky-50 text-sky-700 font-semibold px-2.5 py-1 rounded-full flex items-center gap-1 self-start sm:self-auto">
                    <Users size={12} />
                    {group.students.length} Student{group.students.length !== 1 ? 's' : ''}
                  </span>
                </div>

                {/* Student list at this stop */}
                <div className="pt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                  {group.students.map((s) => (
                    <div
                      key={s.student_id}
                      className="bg-slate-50 p-3 rounded-lg border border-slate-100 flex items-center justify-between"
                    >
                      <div>
                        <span className="font-semibold text-sm text-slate-800 block">
                          {s.student_name}
                        </span>
                        <span className="text-xs text-slate-500">
                          Class {s.student_class} • {s.parent_name || 'Parent'}
                        </span>
                      </div>
                      {s.phone && (
                        <a
                          href={`tel:${s.phone}`}
                          className="w-8 h-8 rounded-full bg-white border border-slate-200 text-sky-600 flex items-center justify-center hover:bg-sky-50 transition-colors shadow-2xs"
                          title={`Call ${s.parent_name || 'Parent'}`}
                        >
                          <Phone size={14} />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

