import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Provinces from './pages/Provinces'
import Ministries from './pages/Ministries'
import Resources from './pages/Resources'
import Companies from './pages/Companies'
import Projects from './pages/Projects'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="provinces" element={<Provinces />} />
          <Route path="ministries" element={<Ministries />} />
          <Route path="resources" element={<Resources />} />
          <Route path="companies" element={<Companies />} />
          <Route path="projects" element={<Projects />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
