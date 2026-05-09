import React from 'react';
import { AlertCircle, RefreshCcw } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends React.Component<React.PropsWithChildren, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <div className="bg-red-500/10 text-red-400 p-4 rounded-full mb-4 ring-1 ring-red-500/20">
          <AlertCircle size={32} />
        </div>
        <h3 className="text-lg font-bold text-white mb-2">This panel could not render</h3>
        <button
          type="button"
          onClick={() => this.setState({ hasError: false })}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-all"
        >
          <RefreshCcw size={16} />
          Try again
        </button>
      </div>
    );
  }
}
