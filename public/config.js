// Einstellungen des Dashboards.
// Solange supabaseUrl und supabaseKey leer sind, läuft die Seite im Demo-Modus
// (erfundene Daten, nichts wird gespeichert). Anleitung: SUPABASE-ANLEITUNG.md
//
// Der "anon"/"publishable" Key ist für den Browser gedacht und darf hier stehen.
// NIEMALS den "service_role"-Key hier eintragen.
window.APP_CONFIG = {
  supabaseUrl: "https://kiwdhjnarfyfleobfnqp.supabase.co",
  supabaseKey: "sb_publishable_pjX_UGjHw8VimOwJV8POXg_LPYGhDPJ",
  // Standort des Werkhofs auf der Karte
  depot: { lat: 47.2340, lng: 8.8600 }
};
