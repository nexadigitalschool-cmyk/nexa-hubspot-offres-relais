// Helper GTM : on alimente uniquement window.dataLayer.
// Aucun GA4 configure dans le code (c'est le role de GTM).

declare global {
  interface Window {
    dataLayer?: Record<string, unknown>[];
  }
}

type NexaEventName =
  | 'cta_card_click'
  | 'modal_open'
  | 'outbound_click'
  | 'video_play';

export function pushDataLayer(event: NexaEventName, payload: Record<string, unknown> = {}): void {
  if (typeof window === 'undefined') return;
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, ...payload });
}
