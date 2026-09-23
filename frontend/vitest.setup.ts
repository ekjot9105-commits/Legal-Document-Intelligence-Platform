import '@testing-library/jest-dom';
import * as matchers from 'vitest-axe/matchers';
import { expect } from 'vitest';

expect.extend(matchers);

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, // deprecated
    removeListener: () => {}, // deprecated
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});
