export function stripHtml(html: string): string {
    if (typeof window === "undefined") {
        // Simple regex fallback for server-side or if DOM is not available
        return html.replace(/<[^>]*>?/gm, '');
    }
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return doc.body.textContent || "";
}

export function splitIntoChunks(text: string, maxLen = 180): string[] {
    const chunks: string[] = [];
    let remaining = text;
    while (remaining.length > 0) {
        if (remaining.length <= maxLen) { chunks.push(remaining.trim()); break; }
        let cutAt = -1;
        const slice = remaining.substring(0, maxLen);
        // If maxLen <= 200 (Google TTS), prioritize commas and spaces to fit strictly.
        // If maxLen > 200 (Edge TTS), only split at actual sentence endings to avoid choppiness!
        const separators = maxLen <= 200
            ? ['. ', '! ', '? ', ', ', '; ', ' ']
            : ['. ', '! ', '? '];
        for (const sep of separators) {
            const idx = slice.lastIndexOf(sep);
            if (idx > 40) { cutAt = idx + sep.length; break; }
        }
        if (cutAt === -1) cutAt = maxLen;
        chunks.push(remaining.substring(0, cutAt));
        remaining = remaining.substring(cutAt);
    }
    return chunks.filter(c => c.length > 0);
}
