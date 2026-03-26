function escapeRegExp(value: string): string {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeCharacterNames(characterNames: string[]): string[] {
    return Array.from(
        new Set(
            characterNames
                .map((name) => name.trim())
                .filter((name) => name.length >= 2)
        )
    ).sort((left, right) => right.length - left.length);
}

export function annotateCharacterNames(html: string, characterNames: string[]): string {
    if (typeof window === "undefined") return html;

    const names = normalizeCharacterNames(characterNames);
    if (names.length === 0) return html;

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const pattern = new RegExp(
        `(^|[^\\p{L}\\p{N}_])(${names.map(escapeRegExp).join("|")})(?=$|[^\\p{L}\\p{N}_])`,
        "giu"
    );

    const walker = doc.createTreeWalker(
        doc.body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode(node) {
                const text = node.textContent ?? "";
                const parent = node.parentElement;
                if (!parent || text.trim().length === 0) {
                    return NodeFilter.FILTER_REJECT;
                }

                if (parent.closest("[data-character-name], a, code, pre, script, style")) {
                    return NodeFilter.FILTER_REJECT;
                }

                return NodeFilter.FILTER_ACCEPT;
            },
        }
    );

    const textNodes: Text[] = [];
    while (walker.nextNode()) {
        textNodes.push(walker.currentNode as Text);
    }

    for (const node of textNodes) {
        const text = node.textContent ?? "";
        pattern.lastIndex = 0;

        const fragment = doc.createDocumentFragment();
        let cursor = 0;
        let hasMatch = false;
        let match: RegExpExecArray | null;

        while ((match = pattern.exec(text)) !== null) {
            const boundary = match[1] ?? "";
            const matchedName = match[2];
            const nameStart = match.index + boundary.length;
            const nameEnd = nameStart + matchedName.length;

            if (nameStart > cursor) {
                fragment.append(text.slice(cursor, nameStart));
            }

            const span = doc.createElement("span");
            span.className = "char-highlight";
            span.setAttribute("data-character-name", matchedName);
            span.textContent = text.slice(nameStart, nameEnd);
            fragment.append(span);

            cursor = nameEnd;
            hasMatch = true;
        }

        if (!hasMatch) {
            continue;
        }

        if (cursor < text.length) {
            fragment.append(text.slice(cursor));
        }

        node.parentNode?.replaceChild(fragment, node);
    }

    return doc.body.innerHTML;
}
