// frontend/src/components/ErrorBoundary.tsx

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state to display fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to the console or an external service
    console.error('Uncaught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <>
          <ToastContainer position="top-end" className="p-3">
            <Toast
              onClose={() => this.setState({ hasError: false, error: null })}
              show={true}
              bg="danger"
            >
              <Toast.Header>
                <strong className="me-auto">Something went wrong</strong>
              </Toast.Header>
              <Toast.Body>{this.state.error.message}</Toast.Body>
            </Toast>
          </ToastContainer>
          {/* Optionally, render a fallback UI */}
        </>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
