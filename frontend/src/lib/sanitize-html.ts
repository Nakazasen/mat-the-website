export function sanitizeHtmlClient(html: string): string {
    if (typeof window === "undefined") return html;
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    doc.querySelectorAll("script,iframe,object,embed,link,meta,style").forEach((el) => el.remove());
    doc.querySelectorAll("*").forEach((el) => {
        for (const attr of Array.from(el.attributes)) {
            const name = attr.name.toLowerCase();
            const value = attr.value.trim().toLowerCase();
            if (name.startsWith("on")) {
                el.removeAttribute(attr.name);
                continue;
            }
            if ((name === "href" || name === "src") && value.startsWith("javascript:")) {
                el.removeAttribute(attr.name);
            }
        }
    });

    return doc.body.innerHTML;
}
