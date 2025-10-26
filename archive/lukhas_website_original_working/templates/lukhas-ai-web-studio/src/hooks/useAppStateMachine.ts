// hooks/useAppStateMachine.ts
"use client"

import { useActor } from '@xstate/react';
import { appStateMachine } from '@/lib/state/appStateMachine';

export function useAppStateMachine() {
  const [state, send] = useActor(appStateMachine);
  
  return {
    state: state.value,
    context: state.context,
    send,
    can: (event: string) => state.can({ type: event }),
    matches: (stateValue: string) => state.matches(stateValue),
  };
}
