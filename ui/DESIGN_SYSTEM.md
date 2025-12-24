# PeelJobs Design System

A comprehensive design guide based on Google's Material Design 3 principles, customized for PeelJobs.

---

## Table of Contents

1. [Typography](#typography)
2. [Colors](#colors)
3. [Spacing](#spacing)
4. [Elevation & Shadows](#elevation--shadows)
5. [Border Radius](#border-radius)
6. [Buttons](#buttons)
7. [Form Inputs](#form-inputs)
8. [Cards](#cards)
9. [Chips & Badges](#chips--badges)
10. [Icons](#icons)
11. [Navigation](#navigation)
12. [Responsive Breakpoints](#responsive-breakpoints)
13. [Animations](#animations)
14. [Component Examples](#component-examples)

---

## Typography

### Font Family

**Primary Font**: Outfit (Google Sans alternative)

```css
font-family: 'Outfit', system-ui, -apple-system, sans-serif;
```

Imported via:
```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
```

### Font Weights

| Weight | Class | Usage |
|--------|-------|-------|
| 300 | `font-light` | Subtle text, large displays |
| 400 | `font-normal` | Body text |
| 500 | `font-medium` | Buttons, labels, navigation |
| 600 | `font-semibold` | Subheadings, card titles |
| 700 | `font-bold` | Headings, emphasis |
| 800 | `font-extrabold` | Hero headings (rare) |

### Type Scale

| Element | Mobile | Desktop | Classes |
|---------|--------|---------|---------|
| Hero H1 | 36px | 60px | `text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight` |
| Section H2 | 24px | 36px | `text-2xl lg:text-3xl font-bold tracking-tight` |
| Card H3 | 16px | 18px | `text-base lg:text-lg font-semibold` |
| Body Large | 18px | 20px | `text-lg md:text-xl` |
| Body | 14px | 16px | `text-sm md:text-base` |
| Caption | 12px | 14px | `text-xs md:text-sm` |

### Text Colors

| Usage | Class | Hex |
|-------|-------|-----|
| Primary text | `text-gray-900` | #111827 |
| Secondary text | `text-gray-600` | #4B5563 |
| Muted text | `text-gray-500` | #6B7280 |
| Disabled text | `text-gray-400` | #9CA3AF |
| Link text | `text-primary-600` | #1a73e8 |
| Error text | `text-error-600` | #d93025 |
| Success text | `text-success-600` | #1e8e3e |

---

## Colors

### Primary Palette (Google Blue)

| Token | Hex | Tailwind Class | Usage |
|-------|-----|----------------|-------|
| primary-50 | #e8f0fe | `bg-primary-50` | Tinted backgrounds, hover states |
| primary-100 | #d2e3fc | `bg-primary-100` | Light backgrounds |
| primary-200 | #aecbfa | `bg-primary-200` | Borders, dividers |
| primary-300 | #8ab4f8 | `bg-primary-300` | Icons (light mode) |
| primary-400 | #669df6 | `bg-primary-400` | — |
| primary-500 | #4285f4 | `bg-primary-500` | Secondary buttons |
| **primary-600** | **#1a73e8** | `bg-primary-600` | **Primary buttons, links** |
| primary-700 | #1967d2 | `bg-primary-700` | Hover states |
| primary-800 | #185abc | `bg-primary-800` | Active states |
| primary-900 | #174ea6 | `bg-primary-900` | Dark accents |

### Semantic Colors

| Color | Token | Hex | Usage |
|-------|-------|-----|-------|
| Success | `success-500` | #34a853 | Success states, verified |
| Success Dark | `success-600` | #1e8e3e | Hover, text |
| Warning | `warning-500` | #fbbc04 | Warnings, highlights |
| Warning Dark | `warning-600` | #f9ab00 | Hover, text |
| Error | `error-500` | #ea4335 | Errors, destructive |
| Error Dark | `error-600` | #d93025 | Hover, text |

### Surface Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `surface-50` | #f8fafd | Page background |
| `surface-100` | #f1f5f9 | Card backgrounds (alternate) |
| `surface-200` | #e8eef4 | Hover states |
| `surface-300` | #dde4ed | Borders |

### Neutral Colors

Use Tailwind's default gray scale:
- `gray-50` to `gray-900` for text and backgrounds
- `white` for card surfaces
- `gray-900` (#111827) for dark sections (footer, features)

---

## Spacing

Follow Tailwind's default spacing scale. Key values:

| Token | Value | Usage |
|-------|-------|-------|
| `1` | 4px | Tight gaps |
| `2` | 8px | Icon gaps, small padding |
| `3` | 12px | Button padding (y) |
| `4` | 16px | Card padding (mobile), gaps |
| `5` | 20px | Card padding (desktop) |
| `6` | 24px | Section gaps |
| `8` | 32px | Large gaps |
| `10` | 40px | Section margins |
| `12` | 48px | — |
| `16` | 64px | Section padding (py-16) |
| `20` | 80px | Large section padding |
| `24` | 96px | Hero padding (lg:py-24) |

### Container

```html
<div class="max-w-7xl mx-auto px-4 lg:px-8">
```

---

## Elevation & Shadows

Material Design 3 elevation system:

```css
/* Level 1 - Cards at rest */
.elevation-1 {
  box-shadow: 0 1px 2px 0 rgb(60 64 67 / 0.3), 0 1px 3px 1px rgb(60 64 67 / 0.15);
}

/* Level 2 - Cards on hover, dropdowns */
.elevation-2 {
  box-shadow: 0 1px 2px 0 rgb(60 64 67 / 0.3), 0 2px 6px 2px rgb(60 64 67 / 0.15);
}

/* Level 3 - Modals, mega menus */
.elevation-3 {
  box-shadow: 0 1px 3px 0 rgb(60 64 67 / 0.3), 0 4px 8px 3px rgb(60 64 67 / 0.15);
}

/* Level 4 - Dialogs, popovers */
.elevation-4 {
  box-shadow: 0 2px 3px 0 rgb(60 64 67 / 0.3), 0 6px 10px 4px rgb(60 64 67 / 0.15);
}
```

### Usage

| Component | Resting | Hover |
|-----------|---------|-------|
| Cards | `elevation-1` or `border border-gray-100` | `hover:elevation-3` |
| Buttons (filled) | `elevation-1` | `hover:elevation-2` |
| Dropdowns | `elevation-3` | — |
| Modals | `elevation-4` | — |
| Header (scrolled) | `elevation-2` | — |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded` | 4px | Small elements |
| `rounded-lg` | 8px | Chips, small buttons |
| `rounded-xl` | 12px | Inputs, icons containers |
| `rounded-2xl` | 16px | Cards, dropdowns |
| `rounded-full` | 9999px | Pills, avatars, circular buttons |

### Common Patterns

```html
<!-- Cards -->
<div class="rounded-2xl">

<!-- Buttons -->
<button class="rounded-full">  <!-- Pill buttons -->
<button class="rounded-xl">    <!-- Square buttons -->

<!-- Inputs -->
<input class="rounded-xl">

<!-- Avatars -->
<img class="rounded-full">

<!-- Icon containers -->
<div class="rounded-xl">
```

---

## Buttons

### Filled Button (Primary)

```html
<button class="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-full transition-colors elevation-1 hover:elevation-2">
  Button Text
</button>
```

### Outlined Button

```html
<button class="px-5 py-2.5 border border-primary-600 text-primary-600 font-medium rounded-full hover:bg-primary-50 transition-colors">
  Button Text
</button>
```

### Tonal Button

```html
<button class="px-5 py-2.5 bg-primary-50 text-primary-700 font-medium rounded-full hover:bg-primary-100 transition-colors">
  Button Text
</button>
```

### Text Button

```html
<button class="px-4 py-2 text-primary-600 font-medium rounded-full hover:bg-primary-50 transition-colors">
  Button Text
</button>
```

### Icon Button

```html
<button class="p-2 rounded-full hover:bg-gray-100 transition-colors">
  <Icon size={20} class="text-gray-600" />
</button>
```

### Button with Icon

```html
<button class="flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-medium rounded-full">
  <Icon size={18} />
  <span>Button Text</span>
</button>
```

### Button Sizes

| Size | Padding | Font | Usage |
|------|---------|------|-------|
| Small | `px-4 py-2` | `text-sm` | Inline actions |
| Medium | `px-5 py-2.5` | `text-sm` | Default |
| Large | `px-8 py-4` | `text-base` | CTAs, hero |

---

## Form Inputs

### Text Input

```html
<input
  type="text"
  placeholder="Placeholder"
  class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
/>
```

### Input with Icon

```html
<div class="relative">
  <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
    <Icon size={18} class="text-gray-400" />
  </span>
  <input
    type="text"
    class="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
  />
</div>
```

### Select

```html
<select class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none">
  <option>Option 1</option>
</select>
```

### Form States

| State | Border | Background | Ring |
|-------|--------|------------|------|
| Default | `border-gray-200` | `bg-gray-50` | — |
| Focus | `border-primary-500` | `bg-white` | `ring-2 ring-primary-500/20` |
| Error | `border-error-500` | `bg-white` | `ring-2 ring-error-500/20` |
| Disabled | `border-gray-200` | `bg-gray-100` | — |

---

## Cards

### Elevated Card

```html
<div class="bg-white rounded-2xl p-5 elevation-1 hover:elevation-3 transition-all">
  <!-- Content -->
</div>
```

### Outlined Card

```html
<div class="bg-white rounded-2xl p-5 border border-gray-100 hover:border-primary-200 transition-colors">
  <!-- Content -->
</div>
```

### Filled Card

```html
<div class="bg-surface-50 rounded-2xl p-5 hover:bg-primary-50 transition-colors">
  <!-- Content -->
</div>
```

### Interactive Card (Link)

```html
<a href="/path/" class="group bg-white rounded-2xl p-5 border border-gray-100 hover:border-primary-200 hover:elevation-3 transition-all block">
  <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
    Title
  </h3>
</a>
```

---

## Chips & Badges

### Filter Chip (Unselected)

```html
<button class="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm font-medium hover:bg-gray-200 transition-colors">
  <Icon size={16} />
  <span>Label</span>
</button>
```

### Filter Chip (Selected)

```html
<button class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-full text-sm font-medium elevation-1 transition-colors">
  <Icon size={16} />
  <span>Label</span>
</button>
```

### Assist Chip

```html
<span class="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 text-primary-700 rounded-full text-sm font-medium">
  <Icon size={16} />
  <span>Label</span>
</span>
```

### Skill Tag

```html
<span class="px-2.5 py-1 bg-primary-50 text-primary-700 text-xs font-medium rounded-lg">
  Skill Name
</span>
```

### Badge

```html
<span class="px-3 py-1 bg-success-500/10 text-success-600 text-sm font-medium rounded-full">
  Badge
</span>
```

---

## Icons

### Library

Use **Lucide Svelte** (`@lucide/svelte`)

```svelte
<script>
  import { Search, MapPin, Briefcase } from '@lucide/svelte';
</script>

<Search size={18} class="text-gray-400" />
```

### Icon Sizes

| Context | Size | Class |
|---------|------|-------|
| Inline with text | 14-16px | `size={14}` or `size={16}` |
| Buttons | 16-18px | `size={16}` or `size={18}` |
| Cards/Lists | 18-20px | `size={18}` or `size={20}` |
| Features | 24-28px | `size={24}` or `size={28}` |
| Hero | 32px+ | `size={32}` |

### Icon Containers

```html
<!-- Small (32px) -->
<div class="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
  <Icon size={16} class="text-primary-600" />
</div>

<!-- Medium (40px) -->
<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
  <Icon size={18} class="text-primary-600" />
</div>

<!-- Large (48px) -->
<div class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
  <Icon size={22} class="text-primary-600" />
</div>

<!-- Feature (56px) -->
<div class="w-14 h-14 rounded-2xl bg-primary-500/20 flex items-center justify-center">
  <Icon size={28} class="text-primary-400" />
</div>
```

---

## Navigation

### Header Structure

```html
<header class="bg-white sticky top-0 z-50 transition-all duration-300 {scrolled ? 'elevation-2' : 'border-b border-gray-100'}">
  <nav class="max-w-7xl mx-auto px-4 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <!-- Nav Links (hidden lg:flex) -->
      <!-- Auth Buttons (hidden lg:flex) -->
      <!-- Mobile Menu Button (lg:hidden) -->
    </div>
  </nav>
</header>
```

### Nav Link

```html
<a href="/path/" class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-gray-700 rounded-full hover:bg-gray-100 transition-colors">
  <Icon size={16} />
  <span>Label</span>
</a>
```

### Dropdown Menu

```html
<div class="absolute left-0 top-full mt-2 bg-white elevation-3 rounded-2xl z-50 w-72 overflow-hidden animate-scale-in origin-top-left">
  <div class="py-2">
    <a href="/path/" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
      Menu Item
    </a>
  </div>
</div>
```

---

## Responsive Breakpoints

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| (default) | 0px | Mobile styles |
| `sm:` | 640px | Large phones |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Desktop |
| `xl:` | 1280px | Large desktop |
| `2xl:` | 1536px | Extra large |

### Common Patterns

```html
<!-- Grid columns -->
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">

<!-- Show/hide -->
<div class="hidden lg:flex">  <!-- Desktop only -->
<div class="lg:hidden">       <!-- Mobile/tablet only -->

<!-- Typography -->
<h1 class="text-4xl md:text-5xl lg:text-6xl">

<!-- Padding -->
<section class="py-16 lg:py-24">

<!-- Flex direction -->
<div class="flex flex-col md:flex-row">
```

---

## Animations

### CSS Keyframes (defined in app.css)

```css
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in-down {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

### Animation Classes

| Class | Duration | Usage |
|-------|----------|-------|
| `animate-fade-in-up` | 0.6s | Page load elements |
| `animate-fade-in-down` | 0.6s | Headers, badges |
| `animate-fade-in` | 0.5s | General fade |
| `animate-scale-in` | 0.4s | Dropdowns, modals |

### Staggered Animations

```html
<div class="animate-fade-in-up" style="opacity: 0;">Item 1</div>
<div class="animate-fade-in-up delay-100" style="opacity: 0;">Item 2</div>
<div class="animate-fade-in-up delay-200" style="opacity: 0;">Item 3</div>
```

Or with inline styles:
```html
{#each items as item, i}
  <div style="animation: fade-in-up 0.5s ease forwards; animation-delay: {i * 50}ms; opacity: 0;">
    {item}
  </div>
{/each}
```

### Transitions

```html
<!-- Standard transition -->
<div class="transition-colors">  <!-- 150ms default -->

<!-- All properties -->
<div class="transition-all duration-200">

<!-- Specific timing -->
<div class="transition-all duration-300">

<!-- Material easing -->
<div class="transition-all duration-200" style="transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);">
```

---

## Component Examples

### Job Card

```svelte
<a href={job.slug} class="group bg-white rounded-2xl overflow-hidden transition-all duration-300 hover:elevation-3 border border-gray-100">
  <div class="p-5">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-4">
      <img src={job.company_logo} alt="" class="w-12 h-12 rounded-xl object-cover bg-gray-100" />
      <div class="flex-1 min-w-0">
        <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
          {job.title}
        </h3>
        <p class="text-sm text-gray-500 truncate">{job.company_name}</p>
      </div>
    </div>

    <!-- Details -->
    <div class="space-y-2 mb-4">
      <div class="flex items-center gap-2 text-sm text-gray-600">
        <MapPin size={14} class="text-gray-400" />
        <span class="truncate">{job.location}</span>
      </div>
    </div>

    <!-- Skills -->
    <div class="flex flex-wrap gap-1.5">
      {#each job.skills.slice(0, 3) as skill}
        <span class="px-2.5 py-1 bg-primary-50 text-primary-700 text-xs font-medium rounded-lg">
          {skill.name}
        </span>
      {/each}
    </div>
  </div>

  <!-- Footer -->
  <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
    <span class="text-xs text-gray-500">{job.time_ago}</span>
    <span class="text-sm font-medium text-primary-600 flex items-center gap-1 group-hover:gap-2 transition-all">
      View Job
      <ChevronRight size={16} />
    </span>
  </div>
</a>
```

### Section Header

```svelte
<div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
  <div>
    <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">Section Title</h2>
    <p class="text-gray-600 mt-2">Section description text</p>
  </div>
  <a href="/path/" class="inline-flex items-center gap-2 text-primary-600 font-medium hover:text-primary-700 transition-colors group">
    View All
    <ArrowRight size={18} class="group-hover:translate-x-1 transition-transform" />
  </a>
</div>
```

### Feature Card (Dark Background)

```svelte
<div class="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-300">
  <div class="w-14 h-14 rounded-2xl bg-primary-500/20 flex items-center justify-center mb-6">
    <Icon size={28} class="text-primary-400" />
  </div>
  <h3 class="text-xl font-bold text-white mb-3">Feature Title</h3>
  <p class="text-gray-400 leading-relaxed">
    Feature description text goes here.
  </p>
</div>
```

---

## Do's and Don'ts

### Do

- Use `rounded-full` for buttons (pill shape)
- Use `rounded-2xl` for cards
- Use `elevation-*` classes for shadows
- Use `transition-all duration-200` for smooth interactions
- Use `group` and `group-hover:` for linked card effects
- Use semantic color tokens (`primary-600`, `success-500`, etc.)
- Use `line-clamp-2` for truncating multi-line text
- Use `truncate` for single-line overflow

### Don't

- Don't use gradients for backgrounds
- Don't use custom CSS when Tailwind classes exist
- Don't use arbitrary values (`[...]`) unless necessary
- Don't mix shadow utilities with `elevation-*` classes
- Don't use `text-blue-500` - use `text-primary-600`
- Don't forget hover and focus states
- Don't skip responsive breakpoints

---

## File References

- **Theme CSS**: `ui/src/app.css`
- **Layout**: `ui/src/routes/(site)/+layout.svelte`
- **Home Page**: `ui/src/routes/(site)/+page.svelte`
- **Components**: `ui/src/lib/components/`

---

*Last updated: December 2024*
