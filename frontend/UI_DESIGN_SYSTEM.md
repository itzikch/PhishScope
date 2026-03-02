# PhishScope UI Design System

## Overview
This document describes the modern, professional UI design system implemented for PhishScope's React + Vite frontend.

## Design Principles

### 1. **Visual Hierarchy**
- Clear distinction between primary, secondary, and tertiary content
- Consistent heading sizes and weights
- Strategic use of color and spacing to guide user attention

### 2. **Modern Aesthetics**
- Clean, minimalist design with purposeful whitespace
- Subtle gradients and shadows for depth
- Smooth transitions and micro-interactions
- Glass morphism effects on key elements

### 3. **Accessibility First**
- WCAG 2.1 AA compliant color contrast ratios
- Comprehensive ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly
- Focus indicators on all interactive elements
- Reduced motion support for users with vestibular disorders

### 4. **Responsive Design**
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Flexible grid layouts
- Touch-friendly interactive elements (min 44x44px)

## Color System

### Primary Colors
```
primary-50:  #f0f9ff (lightest)
primary-600: #0284c7 (main brand color)
primary-700: #0369a1 (hover state)
primary-900: #0c4a6e (darkest)
```

### Semantic Colors
- **Success**: Green palette for positive actions/states
- **Warning**: Yellow palette for caution states
- **Danger**: Red palette for errors/critical states
- **Info**: Blue palette for informational content

### Neutral Grays
- Used for text, borders, and backgrounds
- Range from gray-50 (lightest) to gray-950 (darkest)

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 
             'Helvetica Neue', sans-serif;
```

### Heading Scale
- **H1**: 4xl (36px) - Page titles
- **H2**: 3xl (30px) - Section headers
- **H3**: 2xl (24px) - Card titles
- **H4**: xl (20px) - Subsection headers

### Body Text
- Base: 16px (1rem)
- Small: 14px (0.875rem)
- Extra small: 12px (0.75rem)

## Component Library

### Button Component
**Location**: `src/components/ui/Button.jsx`

**Variants**:
- `primary` - Main call-to-action (blue background)
- `secondary` - Secondary actions (white with border)
- `danger` - Destructive actions (red background)
- `ghost` - Subtle actions (transparent)
- `link` - Text-only links

**Sizes**: `sm`, `md`, `lg`, `xl`

**Features**:
- Loading state with spinner
- Left/right icon support
- Disabled state
- Focus ring for accessibility
- Smooth hover transitions

**Usage**:
```jsx
<Button 
  variant="primary" 
  size="md" 
  loading={isLoading}
  leftIcon={<Icon />}
  onClick={handleClick}
>
  Click Me
</Button>
```

### Card Component
**Location**: `src/components/ui/Card.jsx`

**Sub-components**:
- `Card.Header` - Card header section
- `Card.Title` - Card title
- `Card.Description` - Card description text
- `Card.Content` - Main content area
- `Card.Footer` - Footer section with border

**Features**:
- Hover effect (optional)
- Flexible padding options
- Shadow and border styling
- Rounded corners

**Usage**:
```jsx
<Card hover>
  <Card.Header>
    <Card.Title>Title</Card.Title>
    <Card.Description>Description</Card.Description>
  </Card.Header>
  <Card.Content>
    Content here
  </Card.Content>
</Card>
```

### Badge Component
**Location**: `src/components/ui/Badge.jsx`

**Variants**: `default`, `primary`, `success`, `warning`, `danger`, `info`

**Sizes**: `sm`, `md`, `lg`

**Features**:
- Icon support
- Rounded pill shape
- Color-coded variants

### Alert Component
**Location**: `src/components/ui/Alert.jsx`

**Variants**: `info`, `success`, `warning`, `error`

**Features**:
- Icon automatically matches variant
- Optional title
- Dismissible with close button
- ARIA role="alert" for accessibility

### LoadingSpinner Component
**Location**: `src/components/ui/LoadingSpinner.jsx`

**Features**:
- Multiple sizes
- Optional loading text
- Full-screen overlay mode
- Smooth animation
- ARIA labels for screen readers

## Animations

### Custom Animations
Defined in `tailwind.config.js`:

- `fade-in` - Fade in effect (0.3s)
- `slide-up` - Slide up from bottom (0.3s)
- `slide-down` - Slide down from top (0.3s)
- `scale-in` - Scale in effect (0.2s)

### Usage
```jsx
<div className="animate-fade-in">
  Content fades in
</div>
```

### Transition Guidelines
- **Fast**: 150ms - Small UI changes (hover states)
- **Normal**: 200-300ms - Standard transitions
- **Slow**: 500ms+ - Large layout changes

## Layout Patterns

### Container
```jsx
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  Content
</div>
```

### Grid Layouts
```jsx
{/* Responsive 3-column grid */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card>...</Card>
  <Card>...</Card>
  <Card>...</Card>
</div>
```

### Spacing Scale
- `gap-2` (8px) - Tight spacing
- `gap-4` (16px) - Default spacing
- `gap-6` (24px) - Comfortable spacing
- `gap-8` (32px) - Generous spacing

## Page Layouts

### AnalysisPage
- Hero section with icon and description
- Input card with URL form
- Loading state with progress bar
- Results panel with expandable sections
- Feature cards for empty state

### DashboardPage
- Stats grid (4 columns)
- Search bar
- Data table with hover effects
- Empty state with icon

### Navigation
- Sticky header with backdrop blur
- Active state indicators
- Responsive mobile menu
- Logo with gradient text effect

## Best Practices

### Accessibility
1. Always include ARIA labels on icons
2. Use semantic HTML elements
3. Ensure keyboard navigation works
4. Test with screen readers
5. Maintain color contrast ratios
6. Provide text alternatives for visual content

### Performance
1. Use CSS transitions over JavaScript animations
2. Lazy load images and heavy components
3. Minimize re-renders with proper React patterns
4. Use CSS containment for complex layouts

### Consistency
1. Use design system components instead of custom styles
2. Follow established spacing patterns
3. Maintain consistent border radius (rounded-lg, rounded-xl)
4. Use semantic color names (primary, success, danger)

## Future Enhancements

### Planned Features
- [x] Dark mode support (implemented)
- [ ] Additional chart components for data visualization
- [x] Toast notification system (Sonner)
- [ ] Modal/Dialog component
- [ ] Dropdown menu component
- [ ] Tabs component
- [ ] Tooltip component
- [x] Skeleton loading states (implemented)
- [ ] Pagination component
- [ ] Form validation components

## Resources

### Design System
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Lucide Icons**: https://lucide.dev/
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **React Accessibility**: https://react.dev/learn/accessibility
- **Design Tokens Spec**: https://design-tokens.github.io/community-group/format/

## Support

For questions or suggestions about the UI design system:
1. Review the component source files in `src/components/ui/`
2. Open an issue on GitHub
3. Contact the development team