// EduPredict Hybrid Offline/Online AI Chatbot

const ChatState = {
    isOpen: false,
    isOffline: !navigator.onLine
};

// 1. Core NLP rules for Offline Mode 
// Simple keyword matching mimicking an intent system when no LLM is available
const OFFLINE_KNOWLEDGE_BASE = [
    {
        keywords: ['hello', 'hi', 'hey', 'start'],
        response: "👋 Hello! I am the EduPredict Assistant. I can help you understand your AI predictions or navigate the platform. How can I help?"
    },
    {
        keywords: ['how', 'work', 'predict', 'score', 'calculate'],
        response: "🧠 We use a Machine Learning model trained on historical student data. It analyzes factors like your **Attendance**, **Study Hours**, and **Sleep** to compare your profile against successful patterns and predict your final grade tier."
    },
    {
        keywords: ['improve', 'better', 'low', 'help', 'bad'],
        response: "📈 To improve your score, I recommend tweaking the sliders in the Student Profiler! Generally, increasing **Study Hours** (aim for 15+ a week) and maintaining **Attendance above 85%** yields the highest impact."
    },
    {
        keywords: ['offline', 'internet', 'connection'],
        response: "📶 I am currently running in **Offline Mode** directly in your browser! The core prediction tool and my FAQ knowledge base will continue to work even without an internet connection."
    },
    {
        keywords: ['save', 'history', 'track'],
        response: "💾 If you are logged in as a Student, click the 'Save to Profiler History' button at the bottom of the prediction report to record your current score so you can track your progress over time!"
    },
    {
        keywords: ['radar', 'chart', 'graph'],
        response: "📊 The Radar Chart compares your inputs (Purple) against the 'Ideal Student' (Green). It's a quick visual way to see if you are sleeping enough or falling behind on study hours!"
    }
];

// Fallback for unknown intents
const OFFLINE_FALLBACK = "I'm running in Offline Mode right now, so my knowledge is limited to platform FAQs! Try asking how the prediction works or how to improve your score. 🔌";

// 2. Chatbot UI Injection
document.addEventListener('DOMContentLoaded', () => {
    
    // Inject CSS
    const chatCSS = `
    .chat-widget-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: var(--primary-light);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        z-index: 9999;
        transition: transform 0.3s ease;
    }
    .chat-widget-btn:hover { transform: scale(1.1); }
    
    .chat-window {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 350px;
        height: 500px;
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        display: none;
        flex-direction: column;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        z-index: 9998;
        overflow: hidden;
    }
    .chat-header {
        background: rgba(0,0,0,0.3);
        padding: 1rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--glass-border);
    }
    .chat-body {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .chat-message {
        max-width: 80%;
        padding: 0.8rem 1rem;
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    .chat-ai {
        background: rgba(99, 102, 241, 0.2);
        color: var(--text-primary);
        align-self: flex-start;
        border-top-left-radius: 0;
    }
    .chat-user {
        background: var(--primary-light);
        color: white;
        align-self: flex-end;
        border-top-right-radius: 0;
    }
    .chat-input-area {
        padding: 1rem;
        background: rgba(0,0,0,0.2);
        border-top: 1px solid var(--glass-border);
        display: flex;
        gap: 0.5rem;
    }
    .chat-input {
        flex: 1;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        outline: none;
    }
    .chat-send {
        background: var(--primary-light);
        color: white;
        border: none;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        cursor: pointer;
    }
    `;
    const styleSheet = document.createElement("style");
    styleSheet.innerText = chatCSS;
    document.head.appendChild(styleSheet);

    // Inject HTML
    const chatHTML = `
        <button id="chat-toggle" class="chat-widget-btn"><i class="fa-solid fa-robot"></i></button>
        <div id="chat-window" class="chat-window">
            <div class="chat-header">
                <div>
                    <i class="fa-solid fa-microchip"></i> <strong>EduAssistant</strong>
                    <span id="ai-status-indicator" style="font-size: 0.7rem; margin-left:8px; padding: 2px 6px; border-radius: 10px; background: ${ChatState.isOffline ? 'var(--warning)' : 'var(--success)'}; color: #000;">
                        ${ChatState.isOffline ? 'Offline Mode' : 'Online'}
                    </span>
                </div>
                <i class="fa-solid fa-xmark" id="chat-close" style="cursor: pointer;"></i>
            </div>
            <div id="chat-body" class="chat-body">
                <div class="chat-message chat-ai">👋 Hello! I am the EduPredict Assistant. I can help guide you on how to boost your scores.</div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="chat-input" class="chat-input" placeholder="Ask me something...">
                <button id="chat-send" class="chat-send"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', chatHTML);

    // Logic bindings
    const toggleBtn = document.getElementById('chat-toggle');
    const closeBtn = document.getElementById('chat-close');
    const windowEl = document.getElementById('chat-window');
    const sendBtn = document.getElementById('chat-send');
    const inputEl = document.getElementById('chat-input');
    const bodyEl = document.getElementById('chat-body');
    const indicator = document.getElementById('ai-status-indicator');

    // Handle Network Changes
    window.addEventListener('online',  updateStatus);
    window.addEventListener('offline', updateStatus);

    function updateStatus() {
        ChatState.isOffline = !navigator.onLine;
        indicator.textContent = ChatState.isOffline ? 'Offline Mode' : 'Online';
        indicator.style.background = ChatState.isOffline ? 'var(--warning)' : 'var(--success)';
    }

    toggleBtn.addEventListener('click', () => {
        ChatState.isOpen = !ChatState.isOpen;
        windowEl.style.display = ChatState.isOpen ? 'flex' : 'none';
        if(ChatState.isOpen) inputEl.focus();
    });
    closeBtn.addEventListener('click', () => {
        ChatState.isOpen = false;
        windowEl.style.display = 'none';
    });

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `chat-message ${sender === 'user' ? 'chat-user' : 'chat-ai'}`;
        div.innerHTML = text; // allow bolding internal links
        bodyEl.appendChild(div);
        bodyEl.scrollTop = bodyEl.scrollHeight;
    }

    // Processing the User's Message
    async function handleSend() {
        const text = inputEl.value.trim();
        if(!text) return;

        addMessage(text, 'user');
        inputEl.value = '';

        // 1. If currently offline, skip Network directly to Regex matching
        if (ChatState.isOffline) {
            setTimeout(() => addMessage(getOfflineResponse(text), 'ai'), 400); // fake thinking delay
            return;
        }

        // 2. If online, try the Backend Server.
        try {
            const formData = new FormData();
            formData.append('message', text);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                body: formData
            });

            // 3. Fallback tracking: if server returns 503 (intercepted by ServiceWorker) 
            // or backend drops, fallback to Offline AI processing.
            if (!response.ok) {
                if (response.status === 503) {
                     addMessage("*" + getOfflineResponse(text) + "*", 'ai');
                } else {
                     addMessage("Server unreachable. Switching to local cache: " + getOfflineResponse(text), 'ai');
                }
                return;
            }

            const data = await response.json();
            addMessage(data.reply, 'ai');

        } catch (error) {
            // Hard network failure
            addMessage(getOfflineResponse(text), 'ai');
        }
    }

    // Simple NLP offline matcher
    function getOfflineResponse(query) {
        const normalized = query.toLowerCase().replace(/[^\w\s]/g, '');
        const words = normalized.split(' ');

        for (const rule of OFFLINE_KNOWLEDGE_BASE) {
            // Check if any keyword intersects with query words
            if (rule.keywords.some(kw => words.includes(kw))) {
                return rule.response;
            }
        }
        return OFFLINE_FALLBACK;
    }

    sendBtn.addEventListener('click', handleSend);
    inputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
});
