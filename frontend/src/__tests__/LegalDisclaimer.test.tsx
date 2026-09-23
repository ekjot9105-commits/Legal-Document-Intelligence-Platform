import { render, screen } from '@testing-library/react';
import { axe } from 'vitest-axe';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

describe('LegalDisclaimer Component', () => {
  it('renders correctly', () => {
    render(<LegalDisclaimer />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/legal information, not legal advice/i)).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<LegalDisclaimer />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
