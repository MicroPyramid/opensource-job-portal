import { describe, expect, it } from 'vitest';
import { sanitizeApiHtml } from './html';

describe('sanitizeApiHtml', () => {
	it('preserves supported formatting', () => {
		const result = sanitizeApiHtml(
			'<p><strong>Important</strong> <em>details</em></p><ul><li>One</li><li>Two</li></ul>'
		);

		expect(result).toContain('<p><strong>Important</strong> <em>details</em></p>');
		expect(result).toContain('<ul><li>One</li><li>Two</li></ul>');
	});

	it('removes executable elements and attributes', () => {
		const result = sanitizeApiHtml(
			'<p onclick="alert(1)">Safe</p><script>alert(1)</script><img src="https://example.com/logo.png" onerror="alert(1)">'
		);

		expect(result).toContain('<p>Safe</p>');
		expect(result).toContain('src="https://example.com/logo.png"');
		expect(result).not.toContain('<script');
		expect(result).not.toContain('onclick');
		expect(result).not.toContain('onerror');
	});

	it('removes unsafe URL schemes', () => {
		const result = sanitizeApiHtml(
			'<a href="javascript:alert(1)" target="_blank">Unsafe</a><a href="JaVaScRiPt:alert(1)">Mixed case</a><img src="data:text/html,alert(1)">'
		);

		expect(result).not.toMatch(/href\s*=\s*["']?\s*javascript:/i);
		expect(result).not.toContain('data:text/html');
		expect(result).toContain('rel="noopener noreferrer"');
	});

	it('removes styles and dangerous embedded content', () => {
		const result = sanitizeApiHtml(
			'<p style="background:url(javascript:alert(1))">Text</p><style>body { display: none; }</style><iframe src="https://evil.example"></iframe><object data="payload"></object><embed src="payload"><svg><script>alert(1)</script></svg><math><mtext>payload</mtext></math>'
		);

		expect(result).toContain('<p>Text</p>');
		expect(result).not.toContain('style=');
		expect(result).not.toContain('<style');
		expect(result).not.toContain('<iframe');
		expect(result).not.toContain('<object');
		expect(result).not.toContain('<embed');
		expect(result).not.toContain('<svg');
		expect(result).not.toContain('<math');
		expect(result).not.toContain('<script');
	});

	it('returns an empty string for non-string values', () => {
		expect(sanitizeApiHtml(null)).toBe('');
		expect(sanitizeApiHtml(undefined)).toBe('');
		expect(sanitizeApiHtml(42)).toBe('');
	});
});
