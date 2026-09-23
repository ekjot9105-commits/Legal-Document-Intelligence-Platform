/// <reference types="vite/client" />
/// <reference types="vitest/globals" />
/// <reference types="@testing-library/jest-dom" />

import 'vitest-axe/matchers';

declare module 'vitest' {
  export interface Assertion<T = any> extends jest.Matchers<void, T> {
    toHaveNoViolations(): Promise<void>;
  }
}
