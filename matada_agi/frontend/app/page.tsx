'use client'

import Hero from '@/components/sections/Hero'
import WhatIsMatada from '@/components/sections/WhatIsMatada'
import Vision from '@/components/sections/Vision'
import Trinity from '@/components/sections/Trinity'
import Ethos from '@/components/sections/Ethos'
import HowItWorks from '@/components/sections/HowItWorks'
import InteractiveDemo from '@/components/sections/InteractiveDemo'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import ClientOnly from '@/components/ClientOnly'

export default function Home() {

  return (
    <ClientOnly>
      <Navigation />
      <main className="relative overflow-hidden">
        <div className="w-full">
          <Hero />
          <WhatIsMatada />
          <Vision />
          <Trinity />
          <Ethos />
          <HowItWorks />
          <InteractiveDemo />
        </div>
      </main>
      <Footer />
    </ClientOnly>
  )
}