import { render } from '@testing-library/react';
import { axe } from 'vitest-axe';
import App from '../App';

describe('Homepage Accessibility', () => {
  it('should have no accessibility violations on the homepage', async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
