/**
 * Root layout configuration.
 *
 * The app's own links are written with trailing slashes (/dashboard/, /login/)
 * and CLAUDE.md requires them, but without this every one of those navigations
 * ate a 308 redirect. Matches site/src/routes/+layout.js.
 */
export const trailingSlash = 'always';
