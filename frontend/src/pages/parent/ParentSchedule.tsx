import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bus as BusIcon, Phone, MapPin, Search } from 'lucide-react'
import { getBuses, type Bus } from '../../api/buses'
import { Table, type Column } from '../../components/ui/Table'
import { SearchBar } from '../../components/ui/SearchBar'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

export default function ParentSchedule() {
  const [search, setSearch] = useState('')

  const { data: buses = [], isLoading } = useQuery({
    queryKey: ['parent-buses', search],
    queryFn: () => getBuses(search),
  })

  const columns: Column<Bus>[] = [
    {
      key: 'bus_number',
      header: 'Bus Vehicle',
      render: (b) => (
        <span className="font-semibold text-slate-800 flex items-center gap-2">
          🚌 {b.bus_number}
        </span>
      ),
    },
    {
      key: 'route_name',
      header: 'Route Path',
      render: (b) => (
        <span className="text-slate-800 font-medium">
          {b.route_name || <span className="text-slate-400 italic">Unassigned</span>}
        </span>
      ),
    },
    {
      key: 'driver_name',
      header: 'Driver Profile',
      render: (b) => b.driver_name,
    },
    {
      key: 'driver_phone',
      header: 'Contact Number',
      render: (b) => (
        <a
          href={`tel:${b.driver_phone}`}
          className="text-sky-600 hover:underline flex items-center gap-1.5"
        >
          <Phone size={13} />
          {b.driver_phone}
        </a>
      ),
    },
    {
      key: 'capacity',
      header: 'Total Capacity',
      render: (b) => `${b.capacity} passenger seats`,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">School Fleet & Routes Schedule</h1>
        <p className="text-sm text-slate-500 mt-1">
          Complete directory of school transport vehicles, assigned travel routes, and driver contacts.
        </p>
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
    </div>
  )
}

