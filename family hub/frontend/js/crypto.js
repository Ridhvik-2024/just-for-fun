console.log("[CRYPTO] crypto.js loaded");

// -----------------------------
// Helpers
// -----------------------------
function strToUint8(str) {
  return new TextEncoder().encode(str);
}

function uint8ToStr(buf) {
  return new TextDecoder().decode(buf);
}

function uint8ToBase64(arr) {
  return btoa(String.fromCharCode(...arr));
}

function base64ToUint8(base64) {
  return Uint8Array.from(atob(base64), c => c.charCodeAt(0));
}


// -----------------------------
// Key derivation (PBKDF2)
// -----------------------------
export async function deriveKey(passphrase) {
  console.log("[CRYPTO] Deriving key");

  const baseKey = await crypto.subtle.importKey(
    "raw",
    strToUint8(passphrase),
    { name: "PBKDF2" },
    false,
    ["deriveKey"]
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: strToUint8("family-hub-salt"), // fixed salt for family
      iterations: 100000,
      hash: "SHA-256",
    },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}

// -----------------------------
// Encrypt
// -----------------------------
export async function encryptMessage(key, plaintext) {
  console.log("[CRYPTO] Encrypting message");

  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    strToUint8(plaintext)
  );

  return {
  iv: uint8ToBase64(iv),
  ciphertext: uint8ToBase64(new Uint8Array(ciphertext)),
};

}

// -----------------------------
// Decrypt
// -----------------------------
export async function decryptMessage(key, iv, ciphertext) {
  console.log("[CRYPTO] Decrypting message");

  const plainBuffer = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: base64ToUint8(iv) },
    key,
    base64ToUint8(ciphertext)

  );

  return uint8ToStr(plainBuffer);
}
