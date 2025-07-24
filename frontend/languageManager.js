import { supportedLanguages } from './constants.js';

/**
 * Определяет язык для распознавания речи.
 * @param {boolean} isAutoLanguage - автоопределение или вручную выбранный.
 * @param {number} currentLangIndex - индекс выбранного языка (0 = AUTO).
 * @returns {string} код языка, например "de-DE".
 */
export function getRecognitionLanguage(isAutoLanguage, currentLangIndex) {
  if (!isAutoLanguage) {
    return supportedLanguages[currentLangIndex - 1].code;
  }
  const browserLang = navigator.language || navigator.userLanguage;
  const supportedLangCodes = supportedLanguages.map((l) => l.code);
  if (supportedLangCodes.includes(browserLang)) return browserLang;

  const mainLang = browserLang.split('-')[0];
  const langMap = { de: 'de-DE', ru: 'ru-RU', en: 'en-US' };
  return langMap[mainLang] || 'de-DE';
}

/**
 * Переключает язык и возвращает новую конфигурацию.
 * @param {number} currentLangIndex - текущий индекс языка.
 * @returns {{ newIndex: number, isAuto: boolean, selectedLang: object|null }}
 */
export function toggleLanguage(currentLangIndex) {
  const newIndex = (currentLangIndex + 1) % (supportedLanguages.length + 1);
  const isAuto = newIndex === 0;
  const selectedLang = !isAuto ? supportedLanguages[newIndex - 1] : null;
  return { newIndex, isAuto, selectedLang };
} 