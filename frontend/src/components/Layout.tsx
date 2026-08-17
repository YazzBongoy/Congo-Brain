import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/provinces', label: 'Provinces', icon: '🗺️' },
  { to: '/ministries', label: 'Ministères', icon: '🏛️' },
  { to: '/resources', label: 'Ressources', icon: '⛏️' },
  { to: '/companies', label: 'Entreprises', icon: '🏭' },
  { to: '/projects', label: 'Projets', icon: '📋' },
]

export default function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>Congo-Brain</h1>
          <span>GEOS Dashboard</span>
        </div>
        <nav>
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === '/'}>
              <span>{l.icon}</span> {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
