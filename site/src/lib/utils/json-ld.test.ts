import { describe, expect, it } from 'vitest';
import { serializeJsonLd } from './json-ld';

describe('serializeJsonLd', () => {
	it('round-trips JSON values', () => {
		const value = {
			text: 'Quotes: "value", slash: \\, newline:\nvalue, tag: <strong>safe</strong>, ampersand: &'
		};

		const serialized = serializeJsonLd(value);

		expect(JSON.parse(serialized)).toEqual(value);
	});

	it('escapes script-significant characters while preserving their values', () => {
		const value = '</script><script>alert(1)</script><!--\u2028\u2029';
		const serialized = serializeJsonLd({ value });

		expect(serialized).not.toContain('<');
		expect(serialized).not.toContain('>');
		expect(serialized).not.toContain('&');
		expect(serialized).toContain('\\u003c');
		expect(serialized).toContain('\\u2028');
		expect(serialized).toContain('\\u2029');
		expect(JSON.parse(serialized).value).toBe(value);
	});

	it('rejects values that JSON.stringify cannot represent', () => {
		expect(() => serializeJsonLd(undefined)).toThrow('JSON-LD value must be serializable');
	});
});
