// Declares every URL in the app and which roles may open it.
import { Route, Routes } from 'react-router-dom'
import RequireRole from './auth/RequireRole'
import RootRedirect from './auth/RootRedirect'
import AppLayout from './components/AppLayout'
import AdminPage from './pages/AdminPage'
import LoginPage from './pages/LoginPage'
import ManagerPage from './pages/ManagerPage'
import OperatorPage from './pages/OperatorPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Operator pages: operators only (the API rejects other roles on operator routes). */}
      <Route element={<RequireRole allowed={['operator']} />}>
        <Route element={<AppLayout />}>
          <Route path="/operator" element={<OperatorPage />} />
        </Route>
      </Route>

      {/* Manager pages: managers and admins. */}
      <Route element={<RequireRole allowed={['manager', 'admin']} />}>
        <Route element={<AppLayout />}>
          <Route path="/manager" element={<ManagerPage />} />
        </Route>
      </Route>

      {/* Admin pages: admins only. */}
      <Route element={<RequireRole allowed={['admin']} />}>
        <Route element={<AppLayout />}>
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Route>

      {/* Anything else: send the user where they belong. */}
      <Route path="*" element={<RootRedirect />} />
    </Routes>
  )
}