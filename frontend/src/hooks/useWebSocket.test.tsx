import React from 'react';
import { render } from '@testing-library/react';
import useWebSocket from './useWebSocket';

let mockAuthToken: string | null = 'token-1';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    token: mockAuthToken,
  }),
}));

class MockWebSocket {
  static OPEN = 1;
  static instances: MockWebSocket[] = [];
  readyState = 1;
  onopen: null | (() => void) = null;
  onmessage: null | ((event: { data: string }) => void) = null;
  onclose: null | ((event: CloseEvent) => void) = null;
  onerror: null | ((event: Event) => void) = null;
  close = jest.fn();
  send = jest.fn();

  constructor(_url: string) {
    MockWebSocket.instances.push(this);
  }
}

const HookHost: React.FC<{ onMessage: jest.Mock }> = ({ onMessage }) => {
  useWebSocket('messenger', { onMessage });
  return null;
};

describe('useWebSocket', () => {
  const originalWebSocket = global.WebSocket;
  const originalEnv = process.env.REACT_APP_WEBSOCKET_URL;

  beforeEach(() => {
    jest.useFakeTimers();
    mockAuthToken = 'token-1';
    process.env.REACT_APP_WEBSOCKET_URL = 'ws://localhost:8001';
    MockWebSocket.instances = [];
    (global as any).WebSocket = MockWebSocket as any;
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
    process.env.REACT_APP_WEBSOCKET_URL = originalEnv;
    (global as any).WebSocket = originalWebSocket;
  });

  it('does not connect without token', () => {
    mockAuthToken = null;
    render(<HookHost onMessage={jest.fn()} />);
    expect(MockWebSocket.instances).toHaveLength(0);
  });

  it('cleanup closes socket on unmount', () => {
    const view = render(<HookHost onMessage={jest.fn()} />);
    expect(MockWebSocket.instances).toHaveLength(1);
    view.unmount();
    expect(MockWebSocket.instances[0].close).toHaveBeenCalled();
  });

  it('ignores invalid payload safely', () => {
    const onMessage = jest.fn();
    render(<HookHost onMessage={onMessage} />);
    MockWebSocket.instances[0].onmessage?.({ data: 'not-json' });
    expect(onMessage).not.toHaveBeenCalled();
  });

  it('reconnect attempts are bounded', () => {
    render(<HookHost onMessage={jest.fn()} />);
    for (let i = 0; i < 10; i += 1) {
      MockWebSocket.instances[MockWebSocket.instances.length - 1].onclose?.({ code: 4000 } as CloseEvent);
      jest.runOnlyPendingTimers();
    }
    expect(MockWebSocket.instances.length).toBeLessThanOrEqual(6);
  });
});
