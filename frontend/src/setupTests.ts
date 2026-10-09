// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

const mockAxios: any = jest.fn(() => Promise.resolve({ data: {} }));
mockAxios.defaults = { headers: { common: {} } };
mockAxios.get = jest.fn(() => Promise.resolve({ data: {} }));
mockAxios.post = jest.fn(() => Promise.resolve({ data: {} }));
mockAxios.put = jest.fn(() => Promise.resolve({ data: {} }));
mockAxios.patch = jest.fn(() => Promise.resolve({ data: {} }));
mockAxios.delete = jest.fn(() => Promise.resolve({ data: {} }));
mockAxios.create = jest.fn(() => mockAxios);
mockAxios.isAxiosError = jest.fn(() => false);
mockAxios.interceptors = {
  response: {
    use: jest.fn(() => 0),
    eject: jest.fn(),
  },
};

jest.mock('axios', () => mockAxios);
