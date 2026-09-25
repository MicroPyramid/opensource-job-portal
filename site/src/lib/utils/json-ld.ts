/**
 * Serialize values for raw JSON-LD script elements without allowing HTML
 * parser delimiters to terminate the script element.
 */
const replacements: Record<string, string> = {
	'<': '\\u003c',
	'>': '\\u003e',
	'&': '\\u0026',
	'\u2028': '\\u2028',
	'\u2029': '\\u2029'
};

export function serializeJsonLd(value: unknown): string {
	const serialized = JSON.stringify(value);

	if (serialized === undefined) {
		throw new Error('JSON-LD value must be serializable');
	}

	return serialized.replace(/[<>&\u2028\u2029]/g, (character) => replacements[character]);
}
