import { Outlet } from 'react-router-dom'
import { Sidebar, adminNavItems } from './Sidebar'
import { TopBar } from './TopBar'

export default function AdminLayout() {
  return (
    <div className="min-h-screen bg-bg-main">
      <Sidebar navItems={adminNavItems} role="admin" />
      <TopBar />
      <main className="ml-60 pt-14 min-h-screen">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
