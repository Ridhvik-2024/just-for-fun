import { deriveKey, encryptMessage, decryptMessage } from "./crypto.js";

console.log("[CHAT] chat.js loaded");

let chatKey = null;
let socket = null;
let socketConnected = false;

// -----------------------------
// Initialize chat
// -----------------------------
export async function initChat(passphrase) {
  console.log("[CHAT] Initializing chat");
  chatKey = await deriveKey(passphrase);
}

// -----------------------------
// Send message
// -----------------------------
export async function sendChatMessage(_ignored, text) {
  if (!chatKey) {
    alert("Chat not initialized");
    return;
  }

  if (!socket || socket.readyState !== WebSocket.OPEN) {
    alert("WebSocket not connected");
    return;
  }

  const encrypted = await encryptMessage(chatKey, text);
  socket.send(JSON.stringify(encrypted));
}

// -----------------------------
// Connect WebSocket
// -----------------------------
export function connectWebSocket(token) {
  console.log("[WS] Connecting WebSocket");

  socket = new WebSocket(
    `ws://localhost:8000/chat/ws/chat?token=${token}`
  );

  socket.onopen = () => {
    console.log("[WS] Connected");
    socketConnected = true;
    window.dispatchEvent(new Event("ws-open"));
  };

  socket.onclose = () => {
    console.log("[WS] Disconnected");
    socketConnected = false;
    window.dispatchEvent(new Event("ws-close"));
  };

  socket.onmessage = async (event) => {
    const data = JSON.parse(event.data);

    const text = await decryptMessage(
      chatKey,
      data.iv,
      data.ciphertext
    );

    window.dispatchEvent(
      new CustomEvent("ws-message", {
        detail: {
          sender: data.sender,
          text: text,
          created_at: data.created_at,
        }
      })
    );
  };
}

// -----------------------------
// Socket state
// -----------------------------
export function isSocketConnected() {
  return socketConnected;
}
