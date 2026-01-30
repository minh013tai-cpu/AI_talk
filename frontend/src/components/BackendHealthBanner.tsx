import { useState, useEffect } from 'react'
import { checkBackendHealth } from '../services/api'
import './BackendHealthBanner.css'

const BACKEND_UNREACHABLE_MSG = 'Không kết nối được backend. Hãy chạy: cd backend && python run.py'

export default function BackendHealthBanner() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    const check = async () => {
      const ok = await checkBackendHealth()
      setIsHealthy(ok)
    }
    check()
    const interval = setInterval(check, 10000)
    return () => clearInterval(interval)
  }, [])

  if (isHealthy !== false || dismissed) return null

  return (
    <div className="backend-health-banner" role="alert">
      <span>{BACKEND_UNREACHABLE_MSG}</span>
      <button type="button" onClick={() => setDismissed(true)} aria-label="Đóng">
        ×
      </button>
    </div>
  )
}
