import { cookies, headers } from "next/headers";

import {
    DEFAULT_LOCALE,
    LOCALE_COOKIE,
    type Locale,
    normalizeLocale,
    stripLocaleFromPath,
} from "./config";

export async function getCurrentLocale(): Promise<Locale> {
    const requestHeaders = await headers();
    const headerLocale = requestHeaders.get("x-mt-locale");
    if (headerLocale) {
        return normalizeLocale(headerLocale);
    }

    const cookieStore = await cookies();
    return normalizeLocale(cookieStore.get(LOCALE_COOKIE)?.value ?? DEFAULT_LOCALE);
}

export async function getCurrentCanonicalPath(): Promise<string> {
    const requestHeaders = await headers();
    return requestHeaders.get("x-mt-path") || "/";
}

export async function getUnlocalizedPath(): Promise<string> {
    return stripLocaleFromPath(await getCurrentCanonicalPath());
}
