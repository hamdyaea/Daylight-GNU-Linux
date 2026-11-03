// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
for (const button of document.querySelectorAll('[data-copy]')) {
  button.addEventListener('click', async () => {
    const code = button.parentElement.querySelector('code');
    const status = document.querySelector('#copy-status');
    try {
      await navigator.clipboard.writeText(code.textContent);
      if (status) status.textContent = document.documentElement.lang === 'fr' ? 'Commande copiée.' : 'Command copied.';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      if (status) status.textContent = document.documentElement.lang === 'fr' ? 'Sélectionnez et copiez la commande.' : 'Select and copy the command.';
    }
  });
}

// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
// Native <details> keeps all pages reachable even without JavaScript.
const siteMenu = document.querySelector('.site-menu');
if (siteMenu) {
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && siteMenu.open) {
      siteMenu.open = false;
      siteMenu.querySelector('summary').focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (siteMenu.open && !siteMenu.contains(event.target)) siteMenu.open = false;
  });
  document.addEventListener('focusin', (event) => {
    if (siteMenu.open && !siteMenu.contains(event.target)) siteMenu.open = false;
  });
}
for (const button of document.querySelectorAll('[data-share]')) {
  button.addEventListener('click', async () => {
    const status = document.getElementById('copy-status');
    const french = document.documentElement.lang === 'fr';
    const data = {
      title: 'Daylight GNU/Linux — Raspberry Pi',
      text: french ? 'Un bureau Fluxbox et des outils Rust pour Raspberry Pi OS 64 bits. Version candidate.' : 'A Fluxbox desktop and Rust tools for 64-bit Raspberry Pi OS. Release candidate.',
      url: button.dataset.shareUrl
    };
    try {
      if (navigator.share) await navigator.share(data);
      else {
        await navigator.clipboard.writeText(data.url);
        status.textContent = french ? 'Lien de Daylight copié.' : 'Daylight link copied.';
      }
    } catch (error) {
      if (error.name !== 'AbortError') status.textContent = (french ? 'Lien à partager : ' : 'Link to share: ') + data.url;
    }
  });
}
