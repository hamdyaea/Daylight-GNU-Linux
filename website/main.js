// Developer: Hamdy Abou El Anein
// Contact: contact@daylightlinux.ch
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
