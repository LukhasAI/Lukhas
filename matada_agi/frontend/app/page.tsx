'use client'

import { useEffect } from 'react'
import Hero from '@/components/sections/Hero'
import WhatIsMatada from '@/components/sections/WhatIsMatada'
import Vision from '@/components/sections/Vision'
import Trinity from '@/components/sections/Trinity'
import Ethos from '@/components/sections/Ethos'
import HowItWorks from '@/components/sections/HowItWorks'
import InteractiveDemo from '@/components/sections/InteractiveDemo'
import Navigation from '@/components/Navigation'

export default function Home() {
  useEffect(() => {
    // Initialize scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -10% 0px'
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
        }
      })
    }, observerOptions)

    const elements = document.querySelectorAll('.scroll-fade-up')
    elements.forEach(el => observer.observe(el))

    return () => observer.disconnect()
  }, [])

  return (
    <>
      <Navigation />
      <main className="relative overflow-hidden">
        <Hero />
        <WhatIsMatada />
        <Vision />
        <Trinity />
        <Ethos />
        <HowItWorks />
        <InteractiveDemo />
      </main>
    </>
  )
}