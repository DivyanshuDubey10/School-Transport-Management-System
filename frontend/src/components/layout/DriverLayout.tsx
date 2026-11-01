import { Outlet } from 'react-router-dom'
import { Sidebar, driverNavItems } from './Sidebar'
import { TopBar } from './TopBar'

export default function DriverLayout() {
  return (
    <div className="min-h-screen bg-bg-main">
      <Sidebar navItems={driverNavItems} role="driver" />
      <TopBar />
      <main className="ml-60 pt-14 min-h-screen">
        <div className="p-6 max-w-7xl mx-auto page-enter">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
