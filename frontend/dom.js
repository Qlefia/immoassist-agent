// DOM helpers for markup conversion and math rendering
// All comments are in English intentionally.

/**
 * Normalize backend text by trimming and collapsing excessive blank lines.
 * @param {string} text
 * @returns {string}
 */
export function normalizeText(text) {
  if (!text) return text;
  let result = text.trim();
  // Replace 3+ consecutive newlines with just two
  result = result.replace(/\n{3,}/g, '\n\n');
  return result;
}

/**
 * Convert Markdown string to safe HTML using marked + DOMPurify.
 * Falls back to simple escaping if libraries are missing.
 * @param {string} text
 * @returns {string}
 */
export function convertMarkdownToHtml(text) {
  if (window.marked && window.DOMPurify) {
    const normalizedText = normalizeText(text);
    marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: false,
      mangle: false,
      pedantic: false,
      smartLists: true,
      smartypants: false,
    });

    const rawHtml = marked.parse(normalizedText);
    const safeHtml = DOMPurify.sanitize(rawHtml, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'del',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'span', 'div',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'a', 'img', 'hr',
      ],
      ALLOWED_ATTR: ['class', 'id', 'href', 'src', 'alt', 'title', 'target', 'rel'],
      ALLOW_DATA_ATTR: false,
    });
    return safeHtml;
  }

  // Fallback – escape HTML entities and convert \n to <br>
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\n/g, '<br>');
}

/**
 * Render KaTeX formulas inside a given DOM element (if KaTeX is loaded).
 * @param {HTMLElement} element
 */
export function renderMathFormulas(element) {
  if (window.renderMathInElement && window.katex) {
    try {
      window.renderMathInElement(element, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true },
        ],
        throwOnError: false,
        errorColor: '#cc0000',
        strict: false,
        trust: false,
        macros: {
          '\\RR': '\\mathbb{R}',
          '\\NN': '\\mathbb{N}',
          '\\ZZ': '\\mathbb{Z}',
          '\\QQ': '\\mathbb{Q}',
          '\\CC': '\\mathbb{C}',
        },
      });
    } catch (err) {
      console.error('KaTeX rendering failed', err);
    }
  }
} 