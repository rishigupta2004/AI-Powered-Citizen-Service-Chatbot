# Seva Sindhu Logo Showcase

## Logo Design Elements

### Visual Breakdown

```
┌─────────────────────────────────────┐
│                                     │
│   ╭─────────────────╮               │
│   │   ASHOKA CHAKRA  │               │
│   │   (24 Spokes)   │   सेवा सिंधु  │
│   │   ● ● ● ● ● ●  │   SEVA SINDHU  │
│   ╰─────────────────╯               │
│                                     │
└─────────────────────────────────────┘
```

---

## Design Philosophy

### **The Chakra (Wheel)**
- **24 Spokes**: Representing 24-hour service availability
- **Circular Form**: Unity, continuity, and completeness
- **Center Point**: The core mission of citizen service
- **Radiating Spokes**: Services reaching every citizen

### **Color Distribution**
```
Spoke Pattern (repeating every 3):
  1. Saffron (#FF9933)
  2. Green (#138808)
  3. Navy (#000080)

This creates a harmonious tricolor effect within the chakra.
```

### **Layers (Front to Back)**
1. **Shine Overlay** (Front) - Interactive highlight
2. **Spoke Decorative Dots** - Color-coded service types
3. **24 Spokes** - Radiating from center
4. **Center Circle** - Navy, solid
5. **Middle Ring** - Navy, stroke
6. **Outer Ring** - Navy, dashed (decorative)
7. **Background Circle** - Saffron, 10% opacity

---

## Logo Variants in Context

### **1. Navigation Header (Scrolled)**

```
┌──────────────────────────────────────────────────┐
│  [LOGO - Color]  Home  Services  Dashboard  FAQ  │
│  सेवा सिंधु                                      │
│  SEVA SINDHU                                     │
└──────────────────────────────────────────────────┘
```

**Specifications**:
- Size: Medium (40px)
- Variant: Color
- Background: White/Light
- Text: Shown (dual-script)

---

### **2. Navigation Header (Top/Hero)**

```
┌──────────────────────────────────────────────────┐
│  [LOGO - White]  Home  Services  Dashboard  FAQ  │
│  सेवा सिंधु        (On Dark Navy Background)     │
│  SEVA SINDHU                                     │
└──────────────────────────────────────────────────┘
```

**Specifications**:
- Size: Medium (40px)
- Variant: White
- Background: Navy gradient
- Text: Shown (dual-script)

---

### **3. Hero Section**

```
┌────────────────────────────────────────┐
│                                        │
│         [LARGE LOGO - White]           │
│            सेवा सिंधु                  │
│           SEVA SINDHU                  │
│                                        │
│     Ocean of Services                  │
│   Government of India Initiative       │
│                                        │
└────────────────────────────────────────┘
```

**Specifications**:
- Size: Extra Large (72px)
- Variant: White
- Background: Dark navy gradient with particles
- Text: Shown (dual-script + tagline)

---

### **4. Footer**

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  [LOGO - White]  │  Government of India          │
│  सेवा सिंधु      │  भारत सरकार                  │
│  SEVA SINDHU    │                               │
│                                                  │
│  [Service Links]  [Contact Info]  [Social]      │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Specifications**:
- Size: Large (56px)
- Variant: White
- Background: Dark navy
- Separator: Vertical line
- Government branding alongside

---

### **5. Mobile App Icon**

```
┌─────────┐
│         │
│   ●●●   │
│  ●●●●●  │  <- Simplified Chakra
│ ●●●●●●● │     (Emblem Only)
│  ●●●●●  │
│   ●●●   │
│         │
└─────────┘
```

**Specifications**:
- Size: Small (32px) or larger for app store
- Variant: Color (on white) or White (on navy)
- Text: Hidden (icon only)
- Simplified: Fewer details for small size

---

### **6. Favicon**

```
16x16 px:  [Simplified Chakra]
32x32 px:  [Chakra with 12 spokes]
48x48 px:  [Full Chakra, 24 spokes]
```

---

## Typography Hierarchy

### **Devanagari (Primary)**
```
सेवा सिंधु
├── Font: Noto Sans Devanagari
├── Weight: Bold (700)
├── Size: Responsive to logo size
└── Position: Top line
```

### **Latin (Secondary)**
```
SEVA SINDHU
├── Font: Poppins (or inherited)
├── Weight: Medium (500)
├── Size: 0.5x of Devanagari
├── Tracking: Wide (0.1em)
└── Position: Bottom line
```

---

## Color Specifications

### **Saffron Spokes & Background**
```css
Primary:     #FF9933
RGB:         255, 153, 51
CMYK:        0, 40, 80, 0
Pantone:     1505 C
HSL:         30°, 100%, 60%
Opacity:     100% (spokes), 10% (background)
```

### **Navy Spokes & Structure**
```css
Primary:     #000080
RGB:         0, 0, 128
CMYK:        100, 100, 0, 50
Pantone:     280 C
HSL:         240°, 100%, 25%
Opacity:     100%
```

### **Green Spokes**
```css
Primary:     #138808
RGB:         19, 136, 8
CMYK:        86, 0, 94, 47
Pantone:     362 C
HSL:         115°, 89%, 28%
Opacity:     100%
```

---

## Animation & Interactivity

### **Hover Effects** (Desktop)
```
Default State:
  - Scale: 1.0
  - Rotation: 0°

Hover State:
  - Scale: 1.05
  - Rotation: slight wobble
  - Duration: 0.3s
  - Easing: spring physics
```

### **Tap Effects** (Mobile)
```
Tap Down:
  - Scale: 0.98
  
Tap Release:
  - Scale: 1.0 (bounce back)
  - Duration: 0.2s
```

### **Loading Animation** (Optional)
```
Chakra spokes can rotate slowly:
  - Rotation: 360°
  - Duration: 3s
  - Loop: infinite
  - Direction: clockwise
```

---

## Clear Space Requirements

### **Minimum Clear Space**
```
┌─────────────────────────────────┐
│        ↑                        │
│        │                        │
│        x                        │
│        │                        │
│        ↓                        │
│  ←x→ [LOGO] ←x→                │
│        ↑                        │
│        │                        │
│        x                        │
│        │                        │
│        ↓                        │
└─────────────────────────────────┘

Where x = emblem height
```

**Rule**: Maintain clear space equal to the emblem height on all sides.

---

## Minimum Size Requirements

### **Digital (Screen)**
- **Minimum Width**: 120px (with text)
- **Minimum Width**: 40px (emblem only)
- **Recommended**: 200px+ for optimal legibility

### **Print**
- **Minimum Width**: 1 inch / 2.54 cm (with text)
- **Minimum Width**: 0.5 inch / 1.27 cm (emblem only)
- **Resolution**: 300 DPI minimum

---

## Usage Examples

### **Email Signature**
```
────────────────────────────
Rajesh Kumar
Project Director
[LOGO - Small, Color]
Seva Sindhu Portal
Government of India
support@sevasindhu.gov.in
────────────────────────────
```

### **Official Letter Letterhead**
```
┌──────────────────────────────────┐
│ [LOGO - Medium, Color]           │
│ सेवा सिंधु                       │
│ SEVA SINDHU                      │
│                                  │
│ Ministry of Electronics & IT     │
│ Government of India              │
└──────────────────────────────────┘
```

### **Certificate**
```
╔══════════════════════════════════╗
║                                  ║
║     [LOGO - Large, Color]        ║
║        सेवा सिंधु                ║
║       SEVA SINDHU                ║
║                                  ║
║   CERTIFICATE OF COMPLETION      ║
║                                  ║
╚══════════════════════════════════╝
```

### **Social Media Post**
```
┌────────────────────────┐
│ [Background Image]     │
│                        │
│  [LOGO - White]        │
│  सेवा सिंधु            │
│  SEVA SINDHU          │
│                        │
│  "Access 50+          │
│   Government Services" │
│                        │
│  #DigitalIndia         │
└────────────────────────┘
```

---

## Accessibility Features

### **Screen Reader Description**
```html
<Logo 
  aria-label="Seva Sindhu - Government of India Citizen Services Portal"
  role="img"
/>
```

### **Color Contrast Ratios**
```
White on Navy:    14.51:1 (AAA ✓)
Navy on White:    14.51:1 (AAA ✓)
Saffron on White:  3.02:1 (AA Large Text ✓)
Green on White:    4.54:1 (AA ✓)
```

### **Alternative Text Formats**
- **SVG**: Inline, scalable, accessible
- **PNG**: With alt text
- **High Contrast**: Navy-only variant available

---

## File Formats & Sizes

### **Web/Digital**
```
Format: SVG (vector, preferred)
├── logo-color.svg      (color variant)
├── logo-white.svg      (white variant)
└── logo-navy.svg       (navy variant)

Format: PNG (raster, backup)
├── logo-64.png         (small)
├── logo-128.png        (medium)
├── logo-256.png        (large)
├── logo-512.png        (retina)
└── logo-1024.png       (print/high-res)
```

### **Print**
```
Format: EPS (vector)
Format: AI (editable)
Format: PDF (documents)

Specifications:
├── Color Mode: CMYK
├── Resolution: 300 DPI
└── Bleed: 0.125 inch (if required)
```

### **App/Icon**
```
Format: ICO (Windows)
Format: ICNS (macOS)
Format: PNG (Android/iOS)

Sizes:
├── 16x16   (favicon)
├── 32x32   (favicon)
├── 48x48   (favicon)
├── 192x192 (Android)
└── 512x512 (iOS, high-res)
```

---

## Don'ts - Common Mistakes

### ❌ **Don't Distort**
```
❌ Stretched:  [====LOGO====]
❌ Squashed:   [=LOGO=]
❌ Skewed:     [/LOGO/]
✅ Correct:    [LOGO]
```

### ❌ **Don't Recolor**
```
❌ Pink chakra
❌ Rainbow spokes
❌ Gradient fill on emblem
✅ Use official variants only
```

### ❌ **Don't Add Effects**
```
❌ Drop shadow on logo
❌ Outer glow
❌ Bevel/emboss
✅ Clean, flat design
```

### ❌ **Don't Separate**
```
❌ Emblem on one side, text far away
❌ Text without emblem (except favicon)
✅ Keep emblem + text together
```

### ❌ **Don't Use on Busy Backgrounds**
```
❌ Patterned background
❌ Photograph (without overlay)
❌ Multiple colors
✅ Solid color or simple gradient
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════╗
║  SEVA SINDHU LOGO QUICK REFERENCE     ║
╠═══════════════════════════════════════╣
║                                       ║
║  Name:    Seva Sindhu (सेवा सिंधु)   ║
║  Meaning: Ocean of Services           ║
║                                       ║
║  VARIANTS:                            ║
║  • Color   - Light backgrounds        ║
║  • White   - Dark backgrounds         ║
║  • Navy    - Monochrome/print         ║
║                                       ║
║  SIZES:                               ║
║  • SM (32px)  - Icons                 ║
║  • MD (40px)  - Navigation            ║
║  • LG (56px)  - Footer                ║
║  • XL (72px)  - Hero                  ║
║                                       ║
║  COLORS:                              ║
║  • Saffron: #FF9933                   ║
║  • Navy:    #000080                   ║
║  • Green:   #138808                   ║
║  • White:   #FFFFFF                   ║
║                                       ║
║  CLEAR SPACE: = Emblem height         ║
║  MIN SIZE: 120px (digital, with text) ║
║                                       ║
╚═══════════════════════════════════════╝
```

---

## Component Props Reference

```tsx
interface LogoProps {
  className?: string;           // Additional CSS classes
  size?: 'sm' | 'md' | 'lg' | 'xl';  // Size variant
  showText?: boolean;           // Show/hide text
  variant?: 'color' | 'white' | 'navy';  // Color variant
}

// Default values:
{
  className: '',
  size: 'md',
  showText: true,
  variant: 'color'
}
```

---

**Version**: 2.0
**Last Updated**: October 11, 2025
**Maintained by**: Digital India Team, MeitY
