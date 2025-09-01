'use client'

import { useState } from 'react'

interface HeroData {
  title: string
  description: string
}

export function useHero(initialData: HeroData) {
  const [heroData, setHeroData] = useState<HeroData>(initialData)

  const setHero = (newData: Partial<HeroData>) => {
    setHeroData(prevData => ({ ...prevData, ...newData }))
  }

  return { ...heroData, setHero }
}
