#!/bin/bash

# Build Tailwind CSS for PeelJobs
echo "🔨 Building Tailwind CSS..."

# Build the CSS
npm run build-css

# Copy to clean version for backwards compatibility
cp static/css/tailwind-output.css static/css/tailwind-clean.css

echo "✅ Tailwind CSS build complete!"
echo "📊 Generated $(wc -l < static/css/tailwind-output.css) lines of CSS"
echo "📦 Files created:"
echo "   - static/css/tailwind-output.css (main build)"
echo "   - static/css/tailwind-clean.css (backwards compatibility)"
