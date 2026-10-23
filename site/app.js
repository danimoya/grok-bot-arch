const button = document.getElementById('copy');
button.addEventListener('click', async () => {
  const status = document.getElementById('copy-status');
  try {
    await navigator.clipboard.writeText(document.getElementById('command').textContent);
    status.textContent = 'Command copied.';
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = 'Copy'; }, 2000);
  } catch {
    status.textContent = 'Select the command above and copy it manually.';
  }
});

const sources = new Set(['reddit', 'linkedin', 'discord', 'x', 'mastodon', 'devto', 'hn', 'github', 'newsletter']);
const source = new URLSearchParams(location.search).get('source');
if (sources.has(source)) {
  for (const link of document.querySelectorAll('a[href^="/download/"]')) {
    const url = new URL(link.href);
    url.searchParams.set('source', source);
    link.href = url.toString();
  }
}
