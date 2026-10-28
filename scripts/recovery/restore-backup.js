(function () {
  'use strict';
  const decode = value => Uint8Array.from(atob(value), character => character.charCodeAt(0));
  async function decryptBackup(text, recoverySecret) {
    const backup = JSON.parse(text);
    if (backup.format !== 'salati-signing-backup' || backup.version !== 1 ||
        backup.cipher !== 'AES-256-GCM' || backup.kdf !== 'PBKDF2-HMAC-SHA256' ||
        backup.iterations !== 600000) throw new Error('Unsupported backup format');
    const salt = decode(backup.salt), nonce = decode(backup.nonce);
    if (salt.length !== 16 || nonce.length !== 12) throw new Error('Invalid backup');
    const password = await crypto.subtle.importKey('raw', new TextEncoder().encode(recoverySecret),
      'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt,
      iterations: backup.iterations }, password, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    const result = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: nonce,
      additionalData: new TextEncoder().encode('salati-signing-backup-v1') }, key, decode(backup.ciphertext));
    return new Uint8Array(result);
  }
  globalThis.SalatiRecovery = Object.freeze({ decryptBackup });
})();
