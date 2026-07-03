---
name: Kinetic Obsidian
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c4c9ac'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#8e9379'
  outline-variant: '#444933'
  surface-tint: '#abd600'
  primary: '#ffffff'
  on-primary: '#283500'
  primary-container: '#c3f400'
  on-primary-container: '#556d00'
  inverse-primary: '#506600'
  secondary: '#dcb8ff'
  on-secondary: '#480081'
  secondary-container: '#7701d0'
  on-secondary-container: '#dcb7ff'
  tertiary: '#ffffff'
  on-tertiary: '#00363a'
  tertiary-container: '#7df4ff'
  on-tertiary-container: '#006f77'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c3f400'
  primary-fixed-dim: '#abd600'
  on-primary-fixed: '#161e00'
  on-primary-fixed-variant: '#3c4d00'
  secondary-fixed: '#efdbff'
  secondary-fixed-dim: '#dcb8ff'
  on-secondary-fixed: '#2c0051'
  on-secondary-fixed-variant: '#6700b5'
  tertiary-fixed: '#7df4ff'
  tertiary-fixed-dim: '#00dbe9'
  on-tertiary-fixed: '#002022'
  on-tertiary-fixed-variant: '#004f54'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-xl:
    fontFamily: Archivo Narrow
    fontSize: 72px
    fontWeight: '800'
    lineHeight: 72px
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Archivo Narrow
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Archivo Narrow
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Archivo Narrow
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.1em
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 16px
  margin-mobile: 20px
  margin-desktop: 80px
---

## Brand & Style

This design system targets high-performance athletes and biohackers who view fitness as a technical discipline. The brand personality is aggressive, precise, and futuristic, evoking the feeling of a high-end heads-up display (HUD) found in advanced performance labs.

The aesthetic fuses **Glassmorphism** with **High-Contrast Cyberpunk** elements. Visuals utilize deep obsidian layers, frosted translucent surfaces, and vibrant neon accents to create a sense of digital depth. Imagery must feature high-contrast, moody photography with deep shadows and cool highlights to maintain the "hardcore" atmosphere.

## Colors

The palette is anchored in a monochromatic dark base to ensure the neon accents "vibrate" against the UI.

- **Primary (Electric Lime):** Used for critical calls to action, progress indicators, and "active" states. It represents energy and go-signals.
- **Secondary (Cyber Purple):** Reserved for AI-driven insights, recovery data, and premium features. It adds a sophisticated, technological layer.
- **Accent (Cyber Cyan):** Used sparingly for secondary data points or data visualization categories.
- **Base (Deep Charcoal/Obsidian):** `#0A0A0A` is the canvas. Surface containers use varying opacities of black to create depth without introducing gray mid-tones.

## Typography

The typographic hierarchy prioritizes speed and technicality. 

- **Headlines:** Utilizes **Archivo Narrow** in heavy weights. The condensed nature allows for impactful, large-scale titles that fit within tight mobile grids. All headlines should be set in Uppercase for maximum aggression.
- **Body:** **Inter** provides a neutral, highly readable counterpoint to the intense headlines.
- **Technical Labels:** **JetBrains Mono** is used for data points, timestamps, and AI-generated stats to reinforce the "coded" and precise nature of the platform.

## Layout & Spacing

This design system employs a **Fluid Grid** with strict 4px increments. 

- **Mobile:** 4-column layout with 20px margins. Content cards usually span full width to maximize focus on performance metrics.
- **Desktop:** 12-column layout with 80px margins. Sidebars should be treated as fixed "control panels" while the main stage remains fluid.
- **Rhythm:** Use "md" (24px) for most vertical spacing between sections to maintain a clean, breathable but high-density information environment.

## Elevation & Depth

Elevation is achieved through **Glassmorphism and Tonal Layering** rather than traditional shadows.

1.  **Base Layer:** Solid `#0A0A0A`.
2.  **Mid Layer (Cards/Containers):** Black with 40-60% opacity, featuring a `20px` background blur (backdrop-filter). 
3.  **Top Layer (Popovers/Modals):** Black with 80% opacity, `40px` background blur, and a thin `1px` inner border using the primary or secondary color at 20% opacity.
4.  **Glows:** High-priority elements use a soft outer "bloom" of their accent color (Primary or Secondary) with 15% opacity and a `32px` blur to simulate neon light emission.

## Shapes

The shape language is **Sharp and Architectural**. 

- **Corners:** Use 0px (sharp) corners for most primary containers and buttons to reinforce the "hardcore" and "aggressive" aesthetic. 
- **Exceptions:** For small interactive elements like chips or tags, a `2px` micro-radius may be used to prevent visual "stabbing" in high-density areas, but the overall system should feel crystalline and jagged.
- **Angled Motifs:** Use 45-degree chamfered corners for special "Hero" buttons or AI status indicators to evoke military-grade hardware.

## Components

- **Buttons:** 
    - **Primary:** Solid Electric Lime background, black text, sharp corners. On hover, add a subtle glow.
    - **Ghost:** 1px Electric Lime border, transparent background, lime text.
- **Inputs:** 
    - Dark, semi-transparent backgrounds with a bottom-only border (2px). The border glows when the input is focused.
- **Cards:** 
    - Use the Mid Layer glassmorphic effect. Include a subtle top-left "technical label" using JetBrains Mono to identify the data type.
- **Progress Bars:** 
    - High-contrast segmented bars rather than smooth fills. Each segment represents a data packet.
- **AI Assistant Interface:** 
    - Features a distinctive Cyber Purple glow. All AI-generated text should appear with a "typing" terminal effect where possible.
- **Charts:** 
    - No fills, only high-contrast neon lines. Use thin 1px grid lines in the background at 10% opacity.