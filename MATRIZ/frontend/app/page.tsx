'use client'

import Hero from '@/components/sections/Hero'
import { useHero } from '@/hooks/useHero'
import WhatIsMatada from '@/components/sections/WhatIsMatada'
import Vision from '@/components/sections/Vision'
import Trinity from '@/components/sections/Trinity'
import Ethos from '@/components/sections/Ethos'
import HowItWorks from '@/components/sections/HowItWorks'
import DreamWeaverShowcase from '@/components/sections/DreamWeaverShowcase'
import InteractiveDemo from '@/components/sections/InteractiveDemo'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import ClientOnly from '@/components/ClientOnly'

export default function Home() {
  const { title, description, setHero } = useHero({
    title: 'MATADA',
    description: 'Every thought becomes a traceable, governed, evolvable node',
  });

  const handleUpdateHero = () => {
    setHero({
      title: 'UPDATED',
      description: 'The hero component has been updated dynamically.',
    });
  };

  return (
    <ClientOnly>
      <Navigation />
      <main className="relative overflow-hidden">
        <div className="w-full">
          <Hero title={title} description={description} />
          <div className="text-center my-4">
            <button
              onClick={handleUpdateHero}
              className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
            >
              Update Hero
            </button>
          </div>
          <WhatIsMatada />
          <Vision />
          <Trinity />
          <Ethos />
          <HowItWorks />
          <DreamWeaverShowcase />
          <InteractiveDemo />
        </div>
      </main>
      <Footer />
    </ClientOnly>
  )
}
