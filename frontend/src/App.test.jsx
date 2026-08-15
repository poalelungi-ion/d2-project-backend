import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import { describe, it, expect, vi } from 'vitest';

// Mock recharts to avoid errors in JSDOM
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div>{children}</div>,
  BarChart: () => <div>BarChart</div>,
  Bar: () => <div>Bar</div>,
  XAxis: () => <div>XAxis</div>,
  YAxis: () => <div>YAxis</div>,
  CartesianGrid: () => <div>CartesianGrid</div>,
  Tooltip: () => <div>Tooltip</div>,
  LineChart: () => <div>LineChart</div>,
  Line: () => <div>Line</div>,
}));

// Mock AgGrid to avoid errors
vi.mock('ag-grid-react', () => ({
  AgGridReact: () => <div>AgGridReact</div>,
}));

describe('App Component', () => {
  it('renders the Dashboard by default', () => {
    render(<App />);
    expect(screen.getByText('Study Progress Analysis')).toBeInTheDocument();
  });

  it('can navigate to Batch Data Upload', () => {
    render(<App />);
    fireEvent.click(screen.getByText('Batch Data Upload'));
    expect(screen.getByText(/Upload a spreadsheet/i)).toBeInTheDocument();
  });

  it('can navigate to Student LSF Roster', () => {
    render(<App />);
    fireEvent.click(screen.getByText('Student LSF Roster'));
    expect(screen.getByText('LSF Student Roster')).toBeInTheDocument();
  });
});
