/**
 * LUKHAS UI Components
 *
 * Consciousness-inspired design system components
 * Built with React + TypeScript + Glassmorphism
 */

// Glass Card
export {
  GlassCard,
  GlassCardHeader,
  GlassCardTitle,
  GlassCardDescription,
  GlassCardContent,
  GlassCardFooter,
} from './GlassCard'
export type {
  GlassCardProps,
  GlassCardHeaderProps,
  GlassCardTitleProps,
  GlassCardDescriptionProps,
  GlassCardContentProps,
  GlassCardFooterProps,
} from './GlassCard'

// Button
export { Button, ButtonGroup } from './Button'
export type { ButtonProps, ButtonGroupProps } from './Button'

// Header
export {
  Header,
  HeaderLogo,
  HeaderNav,
  HeaderNavLink,
  HeaderActions,
} from './Header'
export type {
  HeaderProps,
  HeaderLogoProps,
  HeaderNavProps,
  HeaderNavLinkProps,
  HeaderActionsProps,
} from './Header'

// Footer
export {
  Footer,
  FooterEcosystemNav,
  FooterSection,
  FooterLink,
  FooterBottom,
} from './Footer'
export type {
  FooterProps,
  FooterSectionProps,
  FooterLinkProps,
} from './Footer'

// Morphing Particles (React Three Fiber)
export { MorphingParticles } from './MorphingParticles'
export type {
  MorphingShape,
  VoiceData,
  MorphingParticlesProps,
} from './MorphingParticles'
