import { dictionaries } from './src/lib/i18n/dictionaries';
import { SUPPORTED_LOCALES } from './src/lib/i18n/config';

console.log("Validating locales:", SUPPORTED_LOCALES);

SUPPORTED_LOCALES.forEach(locale => {
    try {
        const dict = dictionaries[locale];
        if (!dict) {
            console.error(`Missing dictionary for locale: ${locale}`);
            process.exit(1);
        }
        // Check a field
        if (!dict.hud || !dict.hud.title) {
            console.error(`Missing hud.title for locale: ${locale}`);
            process.exit(1);
        }
        console.log(`Locale ${locale} is valid.`);
    } catch (e) {
        console.error(`Error validating locale ${locale}:`, e);
        process.exit(1);
    }
});

console.log("All locales are valid.");
