import React, { ReactNode } from 'react';
import { splitIntoChunks, stripHtml } from './tts-utils';

/**
 * Syncs visual highlighting with flat TTS chunks while preserving HTML structure.
 */
export function renderRichKaraoke(
    html: string,
    activeChunkIndex: number | null,
    theme: string,
    onRef?: (index: number, el: HTMLElement | null) => void
): { nodes: ReactNode[], chunks: string[] } {
    if (typeof window === "undefined") return { nodes: [], chunks: [] };

    const cleanText = stripHtml(html);
    const chunks = splitIntoChunks(cleanText);

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    let currentChunkIdx = 0;
    let currentChunkOffset = 0; // characters consumed in chunks[currentChunkIdx]

    function walk(node: Node, path: string): ReactNode {
        // Text Node
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent || "";
            if (!text) return null;

            const elements: ReactNode[] = [];
            let textOffset = 0;

            while (textOffset < text.length && currentChunkIdx < chunks.length) {
                const chunk = chunks[currentChunkIdx];
                const needed = chunk.length - currentChunkOffset;
                const available = text.length - textOffset;
                const toTake = Math.min(needed, available);

                const slice = text.substring(textOffset, textOffset + toTake);
                const isFullChunk = currentChunkOffset === 0 && toTake === chunk.length;

                // For simplicity, we assign the chunk index to the span
                // If a chunk is split across multiple nodes, they will all have the same index
                const idx = currentChunkIdx;

                elements.push(
                    <span
                        key={`${path}-${idx}-${textOffset}`}
                        ref={(el) => onRef && onRef(idx, el)}
                        className={`transition-all duration-300 rounded-sm ${activeChunkIndex === idx
                            ? theme === 'dark'
                                ? "bg-toxic-green-DEFAULT/40 text-white shadow-[0_0_25px_rgba(0,255,159,0.4)] ring-1 ring-toxic-green-DEFAULT/50 scale-[1.02] inline-block"
                                : "bg-toxic-green-DEFAULT/50 text-black ring-1 ring-toxic-green-DEFAULT/60 scale-[1.02] inline-block"
                            : ""
                            }`}
                    >
                        {slice}
                    </span>
                );

                textOffset += toTake;
                currentChunkOffset += toTake;

                if (currentChunkOffset >= chunk.length) {
                    currentChunkIdx++;
                    currentChunkOffset = 0;
                }
            }

            // Remainder text (if any - should be none if logic is perfect)
            if (textOffset < text.length) {
                elements.push(<span key={`${path}-rem`}>{text.substring(textOffset)}</span>);
            }

            return <>{elements}</>;
        }

        // Image Node
        if (node.nodeName === 'IMG') {
            const img = node as HTMLImageElement;
            return <img key={`img-${path}`} src={img.src} alt={img.alt} className="rounded-lg border border-reader-border my-6 max-w-full h-auto mx-auto block" />;
        }

        // Element Node (p, div, b, i, etc.)
        if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;

            // Map common tags to React equivalents or generic tags
            const Tag = el.tagName.toLowerCase() as any;

            // Void elements: cannot have children in React
            const voidTags = ['br', 'hr', 'img', 'input', 'wbr'];
            if (voidTags.includes(Tag)) {
                return React.createElement(Tag, { key: `tag-${path}` });
            }

            const children = Array.from(el.childNodes).map((child, i) => walk(child, `${path}-${i}`));

            const validTags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'i', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'blockquote', 'span', 'a', 'section', 'article'];

            if (validTags.includes(Tag)) {
                return React.createElement(Tag, { key: `tag-${path}`, className: el.className || undefined }, children);
            }
            return <React.Fragment key={`frag-${path}`}>{children}</React.Fragment>;
        }

        return null;
    }

    const nodes = Array.from(doc.body.childNodes).map((node, i) => walk(node, `root-${i}`));

    return { nodes, chunks };
}
