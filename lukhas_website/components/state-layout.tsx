'use client'

import { usePathname } from 'next/navigation'
import Navigation from '@/components/navigation'

interface StateLayoutProps {
  children?: React.ReactNode
}

export default function StateLayout({ children }: StateLayoutProps) {
  const pathname = usePathname()
  const isAppRoute = pathname.startsWith('/studio') || pathname.startsWith('/settings')

  if (isAppRoute) {
    return <>{children}</>
  }

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="pt-16">
        {children}
      </main>
    </div>
  )
}
