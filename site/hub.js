// Preserve a coarse campaign label on download links; no visitor identifiers.
const sources = new Set(['reddit', 'linkedin', 'discord', 'x', 'mastodon', 'devto', 'hn', 'github', 'newsletter']);
const source = new URLSearchParams(location.search).get('source');
if (sources.has(source)) {
  for (const link of document.querySelectorAll('a[href^="/download/"]')) {
    const url = new URL(link.href);
    url.searchParams.set('source', source);
    link.href = url.toString();
  }
}
