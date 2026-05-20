/**
 * Constitution of India RAG Chatbot — Frontend Logic
 */

const API_URL = window.location.origin;
const chatArea = document.getElementById("chat-area");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const errorToast = document.getElementById("error-toast");
const welcomeScreen = document.getElementById("welcome-screen");
let isLoading = false;

document.addEventListener("DOMContentLoaded", () => { chatInput.focus(); });
sendBtn.addEventListener("click", handleSend);
chatInput.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } });
chatInput.addEventListener("input", autoResize);
clearBtn.addEventListener("click", clearChat);
document.querySelectorAll(".suggestion-chip").forEach(c => { c.addEventListener("click", () => { chatInput.value = c.textContent; handleSend(); }); });

async function handleSend() {
    const msg = chatInput.value.trim();
    if (!msg || isLoading) return;
    if (welcomeScreen) welcomeScreen.style.display = "none";
    appendMessage("user", msg);
    chatInput.value = ""; autoResize();
    isLoading = true; sendBtn.disabled = true;
    const typing = showTyping();
    try {
        const res = await fetch(`${API_URL}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: msg }) });
        const data = await res.json();
        typing.remove();
        if (!res.ok) throw new Error(data.error || "Something went wrong.");
        appendMessage("bot", data.response, true);
    } catch (err) {
        typing.remove();
        showError(err.message === "Failed to fetch" ? "Cannot connect to server. Is the backend running?" : err.message);
        appendMessage("bot", "Sorry, I encountered an error. Please try again.");
    } finally { isLoading = false; sendBtn.disabled = false; chatInput.focus(); }
}

function appendMessage(role, text, animate = false) {
    const el = document.createElement("div");
    el.className = `message ${role}`;
    const avatar = role === "bot" ? "\u2696\uFE0F" : "\uD83D\uDC64";
    const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    el.innerHTML = `<div class="message-avatar">${avatar}</div><div class="message-content"><div class="message-bubble">${animate ? "" : escapeHTML(text)}</div><div class="message-time">${time}</div></div>`;
    chatArea.appendChild(el);
    if (animate) typeText(el.querySelector(".message-bubble"), text); else scrollBottom();
}

function typeText(el, text) {
    const esc = escapeHTML(text); let i = 0;
    (function t() {
        if (i < esc.length) {
            if (esc[i] === "&") { const e = esc.indexOf(";", i); if (e !== -1) { el.innerHTML += esc.substring(i, e+1); i = e+1; } else { el.innerHTML += esc[i]; i++; } }
            else { el.innerHTML += esc[i]; i++; }
            scrollBottom(); requestAnimationFrame(() => setTimeout(t, 12));
        }
    })();
}

function showTyping() {
    const el = document.createElement("div");
    el.className = "typing-indicator";
    el.innerHTML = `<div class="message-avatar" style="background:linear-gradient(135deg,#7c3aed,#a78bfa);box-shadow:0 0 16px rgba(139,92,246,.15)">\u2696\uFE0F</div><div class="typing-dots"><span></span><span></span><span></span></div>`;
    chatArea.appendChild(el); scrollBottom(); return el;
}

function clearChat() {
    const msgs = chatArea.querySelectorAll(".message,.typing-indicator");
    if (!msgs.length) return;
    msgs.forEach((m, i) => { m.style.transition = `opacity .2s ease ${i*.03}s,transform .2s ease ${i*.03}s`; m.style.opacity = "0"; m.style.transform = "translateY(-10px)"; });
    setTimeout(() => { msgs.forEach(m => m.remove()); if (welcomeScreen) welcomeScreen.style.display = "flex"; }, msgs.length * 30 + 250);
}

function scrollBottom() { requestAnimationFrame(() => chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: "smooth" })); }
function autoResize() { chatInput.style.height = "auto"; chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px"; }
function escapeHTML(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
let et; function showError(m) { errorToast.textContent = m; errorToast.classList.add("visible"); clearTimeout(et); et = setTimeout(() => errorToast.classList.remove("visible"), 4000); }
