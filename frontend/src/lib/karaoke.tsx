import React, { ReactNode } from 'react';
import CharacterTooltip from '@/components/CharacterTooltip';
import { splitIntoChunks, stripHtml } from './tts-utils';

/**
 * Syncs visual highlighting with flat TTS chunks while preserving HTML structure.
 */
export function renderRichKaraoke(
    html: string,
    activeChunkIndex: number | null,
    theme: string,
    chapterProgress: number,
    onRef?: (index: number, el: HTMLElement | null) => void
): { nodes: ReactNode[], chunks: string[] } {
    if (typeof window === "undefined") return { nodes: [], chunks: [] };

    const cleanText = stripHtml(html);
    const chunks = splitIntoChunks(cleanText);

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    let currentChunkIdx = 0;
    let currentChunkOffset = 0;

    function walk(node: Node, path: string): ReactNode {
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
                const idx = currentChunkIdx;

                elements.push(
                    <span
                        key={`${path}-${idx}-${textOffset}`}
                        ref={(el) => onRef && onRef(idx, el)}
                        className={`transition-all duration-300 rounded-sm ${activeChunkIndex === idx
                            ? "bg-toxic-green-DEFAULT text-black ring-2 ring-toxic-green-DEFAULT/80 shadow-[0_0_20px_rgba(57,255,20,0.6)] font-bold scale-[1.02] inline-block px-1"
                            : ""
                            }`}
                        style={activeChunkIndex === idx ? undefined : { color: "var(--reader-text)" }}
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

            if (textOffset < text.length) {
                elements.push(
                    <span key={`${path}-rem`} style={{ color: "var(--reader-text)" }}>
                        {text.substring(textOffset)}
                    </span>
                );
            }

            return <React.Fragment key={`text-${path}`}>{elements}</React.Fragment>;
        }

        if (node.nodeName === 'IMG') {
            const img = node as HTMLImageElement;
            return <img key={`img-${path}`} src={img.src} alt={img.alt} className="rounded-lg border border-reader-border my-6 max-w-full h-auto mx-auto block" />;
        }

        if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;
            const tag = el.tagName.toLowerCase() as any;

            const voidTags = ['br', 'hr', 'img', 'input', 'wbr'];
            if (voidTags.includes(tag)) {
                return React.createElement(tag, { key: `tag-${path}` });
            }

            const children = Array.from(el.childNodes).map((child, i) => walk(child, `${path}-${i}`));
            const characterName = el.getAttribute("data-character-name");

            if (characterName) {
                return (
                    <CharacterTooltip
                        key={`tooltip-${path}`}
                        name={characterName}
                        chapterProgress={chapterProgress}
                    >
                        <span className={el.className || undefined}>{children}</span>
                    </CharacterTooltip>
                );
            }

            const validTags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'i', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'blockquote', 'span', 'a', 'section', 'article'];

            if (validTags.includes(tag)) {
                const props: Record<string, unknown> = {
                    key: `tag-${path}`,
                    className: el.className || undefined,
                };

                if (tag === "a") {
                    props.href = el.getAttribute("href") ?? undefined;
                    props.target = el.getAttribute("target") ?? undefined;
                    props.rel = el.getAttribute("rel") ?? undefined;
                }

                return React.createElement(tag, props, children);
            }

            return <React.Fragment key={`frag-${path}`}>{children}</React.Fragment>;
        }

        return null;
    }

    const nodes = Array.from(doc.body.childNodes).map((node, i) => walk(node, `root-${i}`));

    return { nodes, chunks };
}
