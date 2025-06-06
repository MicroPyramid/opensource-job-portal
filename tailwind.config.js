/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./templates/**/*.html", // All HTML templates in templates directory
    "./*/templates/**/*.html", // App-specific templates
    "./static/**/*.js", // JavaScript files with Tailwind classes
    "./static/**/*.html", // Static HTML files
  ],
  theme: {
    extend: {
      colors: {
        // Primary (blues)
        primary: {
          DEFAULT: '#2563EB', // blue-600
          light: '#3B82F6', // blue-500
          dark: '#1E40AF', // blue-800
        },
        // Secondary (emerald/greens)
        secondary: {
          DEFAULT: '#10B981', // emerald-500
          light: '#34D399', // emerald-400
          dark: '#059669', // emerald-600
        },
        // Accent (oranges)
        accent: {
          DEFAULT: '#FB923C', // orange-400
          light: '#FDBA74', // orange-300
          dark: '#F97316', // orange-500
        },
        // Neutral grays
        neutral: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
        // Legacy “peel” colors
        'peel-primary': '#00AEef',
        'peel-secondary': '#0681C4',
        'peel-accent': '#F8F9FA',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      fontSize: {
        xs: ['0.75rem', '1rem'], // 12px, 16px line-height
        sm: ['0.875rem', '1.25rem'], // 14px, 20px line-height
        base: ['1rem', '1.5rem'], // 16px, 24px line-height
        lg: ['1.125rem', '1.5rem'], // 18px, 24px line-height
        xl: ['1.25rem', '1.75rem'], // 20px, 28px line-height
        '2xl': ['1.5rem', '2rem'], // 24px, 32px line-height
        '3xl': ['1.875rem', '2.25rem'], // 30px, 36px line-height
      },
      spacing: {
        2: '0.5rem',
        3: '0.75rem',
        4: '1rem',
        8: '2rem',
        12: '3rem',
        16: '4rem',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'focus-ring': '0 0 0 3px rgba(37, 99, 235, 0.3)', // for custom focus
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#111827', // neutral-900
            h1: { color: '#2563EB', fontWeight: '700' }, // primary
            h2: { color: '#1E40AF', fontWeight: '600' }, // primary-dark
            h3: { color: '#1F2937', fontWeight: '600' }, // neutral-800
            a: { color: '#10B981', textDecoration: 'underline', '&:hover': { color: '#059669' } }, // secondary, secondary-dark
            p: { color: '#4B5563' }, // neutral-600
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class', // Use class-based form styling
    }),
    require('@tailwindcss/typography'),
    // Custom utilities plugin
    function ({ addUtilities }) {
      addUtilities({
        // Truncate text to two lines
        '.truncate-2': {
          display: '-webkit-box',
          '-webkit-line-clamp': '2',
          '-webkit-box-orient': 'vertical',
          overflow: 'hidden',
        },
        // Responsive grid for job cards
        '.grid-rows-jobs': {
          display: 'grid',
          'grid-template-columns': 'repeat(auto-fill, minmax(16rem, 1fr))',
          gap: '1rem',
        },
        // Thicker focus ring utility
        '.focus\\:ring-3:focus': {
          boxShadow: '0 0 0 3px rgba(37, 99, 235, 0.3)',
        },
        // Card hover effect
        '.card-hover': {
          transition: 'transform 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
          },
        },
      });
    },
  ],
  // Important to override Bootstrap styles when needed
  important: true,
};