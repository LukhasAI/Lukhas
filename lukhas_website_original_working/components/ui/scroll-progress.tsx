'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

export function ScrollProgress() {
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = (window.scrollY / totalHeight) * 100
      setScrollProgress(progress)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-1 z-50 bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian"
      style={{
        scaleX: scrollProgress / 100,
        transformOrigin: 'left',
      }}
      transition={{ duration: 0.1 }}
    />
  )
}