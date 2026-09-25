/**
 * The only boundary for API-sourced rich text before it is rendered with
 * {@html}. Keep this server-only and sanitize data in server loaders.
 */
import sanitizeHtml from 'sanitize-html';

const allowedTags = [
	'a',
	'b',
	'blockquote',
	'br',
	'code',
	'del',
	'div',
	'em',
	'h1',
	'h2',
	'h3',
	'h4',
	'h5',
	'h6',
	'hr',
	'i',
	'img',
	'li',
	'ol',
	'p',
	'pre',
	's',
	'span',
	'strong',
	'sub',
	'sup',
	'table',
	'tbody',
	'td',
	'tfoot',
	'th',
	'thead',
	'tr',
	'u',
	'ul'
];

const sanitizeOptions: sanitizeHtml.IOptions = {
	allowedTags,
	allowedAttributes: {
		a: ['href', 'title', 'target', 'rel'],
		img: ['src', 'alt', 'title', 'width', 'height'],
		ol: ['start'],
		td: ['colspan', 'rowspan'],
		th: ['colspan', 'rowspan', 'scope']
	},
	allowedSchemes: ['http', 'https', 'mailto'],
	allowedSchemesByTag: {
		img: ['http', 'https']
	},
	allowProtocolRelative: false,
	disallowedTagsMode: 'discard',
	nonTextTags: [
		'script',
		'style',
		'textarea',
		'option',
		'noscript',
		'iframe',
		'object',
		'embed',
		'template',
		'svg',
		'math',
		'foreignobject'
	],
	transformTags: {
		a: (tagName, attribs) => {
			if (attribs.target !== '_blank') {
				return { tagName, attribs };
			}

			const rel = new Set((attribs.rel ?? '').split(/\s+/).filter(Boolean));
			rel.add('noopener');
			rel.add('noreferrer');

			return {
				tagName,
				attribs: {
					...attribs,
					rel: [...rel].join(' ')
				}
			};
		}
	}
};

export function sanitizeApiHtml(value: unknown): string {
	if (typeof value !== 'string') {
		return '';
	}

	return sanitizeHtml(value, sanitizeOptions);
}
