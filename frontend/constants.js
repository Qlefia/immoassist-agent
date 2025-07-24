export const supportedLanguages = [
  { code: 'de-DE', name: 'DE', full: 'Deutsch' },
  { code: 'ru-RU', name: 'RU', full: 'Русский' },
  { code: 'en-US', name: 'EN', full: 'English' },
];

export const audioConstraints = {
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
  },
};

/**
 * Returns a sensible default recognition language based on the browser settings.
 */
export function getDefaultRecognitionLanguage() {
  const browserLang = navigator.language || navigator.userLanguage;
  const supportedLangCodes = supportedLanguages.map((l) => l.code);
  if (supportedLangCodes.includes(browserLang)) return browserLang;

  const mainLang = browserLang.split('-')[0];
  const langMap = { de: 'de-DE', ru: 'ru-RU', en: 'en-US' };
  return langMap[mainLang] || 'de-DE';
} 