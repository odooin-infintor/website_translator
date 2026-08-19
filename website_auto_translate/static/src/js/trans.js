/** @odoo-module **/

const lang = document.documentElement.lang;

if (lang && !lang.startsWith('en')) {

    // Collect all direct text nodes from the page
    function getTextNodes(root) {
        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode(node) {
                    const text = node.textContent.trim();

                    // Skip empty or too short
                    if (!text || text.length < 3) return NodeFilter.FILTER_REJECT;

                    // Skip script/style tags
                    const parent = node.parentElement;
                    const tag = parent?.tagName?.toLowerCase();
                    if (['script', 'style', 'noscript'].includes(tag)) return NodeFilter.FILTER_REJECT;

                    // Skip already translated
                    if (parent?.dataset?.translated === '1') return NodeFilter.FILTER_REJECT;

                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        const nodes = [];
        let node;
        while ((node = walker.nextNode())) nodes.push(node);
        return nodes;
    }

    const textNodes = getTextNodes(document.body);

    // FIX: "return" is not allowed at the top level of a module.
    // Wrapped the rest of the logic in an "if (textNodes.length)" block instead,
    // which is what was causing a hard SyntaxError and silently killing this
    // entire script (no translation would ever run).
    if (textNodes.length) {

        const texts = textNodes.map(n => n.textContent.trim());

        fetch('/auto_translate_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': odoo.csrf_token,
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: { texts, target_lang: lang, source_lang: 'en' },
            }),
        })
        .then(res => res.json())
        .then(data => {
            const translated = data.result?.translations || [];
            textNodes.forEach((node, i) => {
                if (translated[i] && translated[i] !== texts[i]) {
                    node.textContent = translated[i];
                    if (node.parentElement) {
                        node.parentElement.dataset.translated = '1';
                    }
                }
            });
        })
        .catch(err => console.error('[AutoTranslate]', err));
    }
}