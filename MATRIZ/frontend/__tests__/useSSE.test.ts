// Minimal tests (Vitest). Adjust if you use Jest.
import { describe, it, expect } from 'vitest'
import { useSSE } from './useSSE'
import { renderHook } from '@testing-library/react'

class ESMock {
  onopen: (() => void) | null = null
  onmessage: ((e:any)=>void) | null = null
  onerror: (() => void) | null = null
  constructor(url:string){ setTimeout(()=> this.onopen && this.onopen(), 0) }
  emit(data:any){ this.onmessage && this.onmessage({ data: JSON.stringify(data) }) }
  fail(){ this.onerror && this.onerror() }
  close(){}
}
// @ts-ignore
global.EventSource = ESMock as any

describe('useSSE', () => {
  it('connects', async () => {
    const { result } = renderHook(() => useSSE('/sse'))
    expect(result.current.connected).toBeTypeOf('boolean')
  })
})
