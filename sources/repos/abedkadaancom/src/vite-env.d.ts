/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_PUBLISHABLE_KEY?: string;
  /** Optional verified contact for Harness Master conversation requests. */
  readonly VITE_HM_CONTACT_EMAIL?: string;
  /** Optional verified booking link (e.g. a scheduling page). */
  readonly VITE_HM_BOOKING_URL?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module 'troika-three-text' {
  export function configureTextBuilder(config: { unicodeFontsURL?: string; useWorker?: boolean; defaultFontURL?: string }): void;
}
