const SOCIAL_GRAPH_UPDATED_EVENT = 'social-graph-updated';

export const emitSocialGraphUpdated = () => {
  window.dispatchEvent(new CustomEvent(SOCIAL_GRAPH_UPDATED_EVENT));
};

export const subscribeSocialGraphUpdated = (callback: () => void) => {
  const handler = () => callback();
  window.addEventListener(SOCIAL_GRAPH_UPDATED_EVENT, handler);
  return () => {
    window.removeEventListener(SOCIAL_GRAPH_UPDATED_EVENT, handler);
  };
};
