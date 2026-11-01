import { Outlet } from 'react-router-dom'
import { Sidebar, parentNavItems } from './Sidebar'
import { TopBar } from './TopBar'

export default function ParentLayout() {
  return (
    <div className="min-h-screen bg-bg-main">
      <Sidebar navItems={parentNavItems} role="parent" />
      <TopBar />
      <main className="ml-60 pt-14 min-h-screen">
        <div className="p-6 max-w-7xl mx-auto page-enter">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
