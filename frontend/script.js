// ========================================================
// ELEMENTS
// ========================================================

const app =
    document.getElementById("app");

const chat =
    document.getElementById("chat");

const input =
    document.getElementById(
        "messageInput"
    );

const sendButton =
    document.getElementById(
        "sendButton"
    );

const stopButton =
    document.getElementById(
        "stopButton"
    );

const newChatButton =
    document.getElementById(
        "newChatButton"
    );

const historyList =
    document.getElementById(
        "historyList"
    );

const collapseButton =
    document.getElementById(
        "collapseButton"
    );

const openHistoryButton =
    document.getElementById(
        "openHistoryButton"
    );

const agentCard =
    document.getElementById(
        "agentCard"
    );

const agentIcon =
    document.getElementById(
        "agentIcon"
    );

const agentName =
    document.getElementById(
        "agentName"
    );

const agentStatus =
    document.getElementById(
        "agentStatus"
    );

const agentAnimation =
    document.getElementById(
        "agentAnimation"
    );

const thinking =
    document.getElementById(
        "thinking"
    );

const headerStatus =
    document.getElementById(
        "headerStatus"
    );

const headerAgent =
    document.getElementById(
        "headerAgent"
    );

const footerAgent =
    document.getElementById(
        "footerAgent"
    );


// ========================================================
// STATE
// ========================================================

let chats = [];

let currentChatId = null;

let controller = null;

let lastHistorySignature = "";


// ========================================================
// AGENTS
// ========================================================

const AGENTS = {

    nexa: {
        name: "NEXA",
        icon: "✦",
        working: "Thinking...",
        ready: "Ready"
    },

    app: {
        name: "App Agent",
        icon: "▦",
        working:
            "Controlling application...",
        ready:
            "Application ready"
    },

    instagram: {
        name:
            "Instagram Agent",
        icon: "◎",
        working:
            "Working with Instagram...",
        ready:
            "Instagram ready"
    },

    mail: {
        name: "Mail Agent",
        icon: "✉",
        working:
            "Working with mail...",
        ready:
            "Mail ready"
    },

    music: {
        name: "Music Agent",
        icon: "♫",
        working:
            "Controlling music...",
        ready:
            "Music ready"
    },

    messaging: {
        name:
            "Messaging Agent",
        icon: "◌",
        working:
            "Working with messages...",
        ready:
            "Messaging ready"
    }
};


// ========================================================
// CREATE CHAT ID
// ========================================================

function createChatId() {

    return (
        "chat_" +
        Date.now() +
        "_" +
        Math.random()
            .toString(36)
            .slice(2, 8)
    );
}


// ========================================================
// CURRENT CHAT
// ========================================================

function getCurrentChat() {

    return chats.find(
        item =>
            item.id ===
            currentChatId
    );
}


// ========================================================
// LOAD HISTORY
// ========================================================

async function loadHistory(
    forceRender = false
) {

    try {

        const response =
            await fetch(
                "/history",
                {
                    cache:
                        "no-store"
                }
            );


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        const newChats =
            Array.isArray(
                data.chats
            )
                ? data.chats
                : [];


        const signature =
            JSON.stringify(
                newChats
            );


        const changed =
            signature !==
            lastHistorySignature;


        chats =
            newChats;


        lastHistorySignature =
            signature;


        if (
            !currentChatId &&
            chats.length > 0
        ) {

            currentChatId =
                chats[
                    chats.length - 1
                ].id;
        }


        if (
            currentChatId &&
            !chats.some(
                item =>
                    item.id ===
                    currentChatId
            )
        ) {

            currentChatId =
                chats.length
                    ? chats[
                        chats.length - 1
                    ].id
                    : null;
        }


        if (
            changed ||
            forceRender
        ) {

            renderHistory();

            renderChat();
        }

    } catch (error) {

        console.error(
            "History error:",
            error
        );
    }
}


// ========================================================
// CREATE CHAT
// ========================================================

async function createNewChat() {

    const chatId =
        createChatId();


    try {

        const response =
            await fetch(
                "/history/create",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            chat_id:
                                chatId
                        })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Could not create chat."
            );
        }


        currentChatId =
            chatId;


        lastHistorySignature =
            "";


        await loadHistory(
            true
        );


        input.focus();


    } catch (error) {

        console.error(
            error
        );
    }
}


// ========================================================
// OPEN CHAT
// ========================================================

function openChat(chatId) {

    currentChatId =
        chatId;

    renderHistory();

    renderChat();

    input.focus();
}


// ========================================================
// DELETE CHAT
// ========================================================

async function deleteChat(
    chatId,
    event
) {

    event.stopPropagation();


    await fetch(
        `/history/${chatId}`,
        {
            method:
                "DELETE"
        }
    );


    if (
        currentChatId ===
        chatId
    ) {

        currentChatId =
            null;
    }


    lastHistorySignature =
        "";


    await loadHistory(
        true
    );


    if (!currentChatId) {

        await createNewChat();
    }
}


// ========================================================
// HISTORY
// ========================================================

function renderHistory() {

    historyList.innerHTML =
        "";


    if (!chats.length) {

        const empty =
            document.createElement(
                "div"
            );


        empty.textContent =
            "No conversations yet.";


        empty.style.padding =
            "20px 8px";


        empty.style.color =
            "#697384";


        historyList.appendChild(
            empty
        );

        return;
    }


    const ordered =
        [...chats].reverse();


    for (
        const item
        of ordered
    ) {

        const row =
            document.createElement(
                "div"
            );


        row.className =
            "history-item";


        if (
            item.id ===
            currentChatId
        ) {

            row.classList.add(
                "active"
            );
        }


        const open =
            document.createElement(
                "button"
            );


        open.className =
            "history-open";


        const title =
            document.createElement(
                "span"
            );


        title.className =
            "history-title";


        title.textContent =
            item.title ||
            "New Chat";


        open.appendChild(
            title
        );


        open.addEventListener(
            "click",
            () => {

                openChat(
                    item.id
                );
            }
        );


        const remove =
            document.createElement(
                "button"
            );


        remove.className =
            "history-delete";


        remove.textContent =
            "×";


        remove.addEventListener(
            "click",
            event => {

                deleteChat(
                    item.id,
                    event
                );
            }
        );


        row.appendChild(
            open
        );


        row.appendChild(
            remove
        );


        historyList.appendChild(
            row
        );
    }
}


// ========================================================
// CHAT
// ========================================================

function renderChat() {

    chat.innerHTML =
        "";


    const current =
        getCurrentChat();


    if (
        !current ||
        !current.turns ||
        !current.turns.length
    ) {

        renderWelcome();

        return;
    }


    for (
        const turn
        of current.turns
    ) {

        renderTurn(
            turn
        );
    }


    scrollBottom();
}


// ========================================================
// WELCOME
// ========================================================

function renderWelcome() {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "message";


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    const meta =
        document.createElement(
            "div"
        );


    meta.className =
        "message-meta";


    meta.textContent =
        "NEXA";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "message-bubble";


    bubble.textContent =
        "Ready. What would you like me to do?";


    content.appendChild(
        meta
    );


    content.appendChild(
        bubble
    );


    wrapper.appendChild(
        content
    );


    chat.appendChild(
        wrapper
    );
}


// ========================================================
// TURN
// ========================================================

function renderTurn(turn) {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "chat-turn";


    // USER

    const user =
        document.createElement(
            "div"
        );


    user.className =
        "message user";


    const userContent =
        document.createElement(
            "div"
        );


    userContent.className =
        "message-content";


    const userMeta =
        document.createElement(
            "div"
        );


    userMeta.className =
        "message-meta";


    userMeta.textContent =
        "YOU";


    const userBubble =
        document.createElement(
            "div"
        );


    userBubble.className =
        "message-bubble";


    userBubble.textContent =
        turn.prompt || "";


    userContent.appendChild(
        userMeta
    );


    userContent.appendChild(
        userBubble
    );


    user.appendChild(
        userContent
    );


    // NEXA

    const assistant =
        document.createElement(
            "div"
        );


    assistant.className =
        "message";


    const assistantContent =
        document.createElement(
            "div"
        );


    assistantContent.className =
        "message-content";


    const assistantMeta =
        document.createElement(
            "div"
        );


    assistantMeta.className =
        "message-meta";


    assistantMeta.textContent =
        "NEXA";


    const assistantBubble =
        document.createElement(
            "div"
        );


    assistantBubble.className =
        "message-bubble";


    assistantBubble.textContent =
        turn.response ||
        "Working...";


    assistantContent.appendChild(
        assistantMeta
    );


    assistantContent.appendChild(
        assistantBubble
    );


    assistant.appendChild(
        assistantContent
    );


    wrapper.appendChild(
        user
    );


    wrapper.appendChild(
        assistant
    );


    // FLOAT

    if (turn.response) {

        const actions =
            document.createElement(
                "div"
            );


        actions.className =
            "turn-actions";


        const floatButton =
            document.createElement(
                "button"
            );


        floatButton.className =
            "float-button";


        floatButton.textContent =
            "Float ↗";


        floatButton.addEventListener(
            "click",
            () => {

                floatTurn(
                    turn,
                    floatButton
                );
            }
        );


        actions.appendChild(
            floatButton
        );


        wrapper.appendChild(
            actions
        );
    }


    chat.appendChild(
        wrapper
    );
}


// ========================================================
// FLOAT TURN
// ========================================================

async function floatTurn(
    turn,
    button
) {

    console.log(
        "CURRENT CHAT ID:",
        currentChatId
    );


    console.log(
        "TURN:",
        turn
    );


    if (!currentChatId) {

        button.textContent =
            "No Chat";

        return;
    }


    const prompt =
        String(
            turn.prompt || ""
        );


    const result =
        String(
            turn.response || ""
        );


    if (!prompt) {

        button.textContent =
            "No Prompt";

        return;
    }


    if (!result) {

        button.textContent =
            "No Result";

        return;
    }


    const originalText =
        button.textContent;


    button.disabled =
        true;


    button.textContent =
        "Opening...";


    const payload = {

        chat_id:
            currentChatId,

        prompt:
            prompt,

        response:
            result
    };


    console.log(
        "FLOAT PAYLOAD:",
        payload
    );


    try {

        const response =
            await fetch(
                "/float-chat",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const data =
            await response.json();


        console.log(
            "FLOAT SERVER RESPONSE:",
            data
        );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );
        }


        if (
            data.status !==
            "success"
        ) {

            throw new Error(
                data.message ||
                "Float failed."
            );
        }


        button.textContent =
            "Opened ✓";


    } catch (error) {

        console.error(
            "FLOAT FAILED:",
            error
        );


        button.textContent =
            "Failed";


    } finally {

        setTimeout(
            () => {

                button.disabled =
                    false;


                button.textContent =
                    originalText;

            },
            1500
        );
    }
}


// ========================================================
// DETECT AGENT
// ========================================================

function detectAgent(message) {

    const text =
        message.toLowerCase();


    if (
        text.includes(
            "instagram"
        )
    ) {

        return "instagram";
    }


    if (
        text.includes("gmail") ||
        text.includes("email") ||
        text.includes("mail")
    ) {

        return "mail";
    }


    if (
        text.includes("spotify") ||
        text.includes("music") ||
        text.includes("song")
    ) {

        return "music";
    }


    if (
        text.includes(
            "whatsapp"
        )
    ) {

        return "messaging";
    }


    if (
        text.includes(
            "calculator"
        ) ||
        text.includes(
            "notepad"
        ) ||
        text.includes(
            "chrome"
        ) ||
        text.includes(
            "vscode"
        ) ||
        text.startsWith(
            "open "
        )
    ) {

        return "app";
    }


    return "nexa";
}


// ========================================================
// SET AGENT
// ========================================================

function setAgent(
    type,
    status,
    working
) {

    const selected =
        AGENTS[type] ||
        AGENTS.nexa;


    agentIcon.textContent =
        selected.icon;


    agentName.textContent =
        selected.name;


    agentStatus.textContent =
        status;


    headerAgent.textContent =
        selected.name;


    headerStatus.textContent =
        status;


    footerAgent.textContent =
        selected.name
            .toUpperCase();


    agentCard.classList.toggle(
        "working",
        working
    );


    agentAnimation.classList.toggle(
        "hidden",
        !working
    );
}


// ========================================================
// SEND MESSAGE
// ========================================================

async function sendMessage() {

    const message =
        input.value.trim();


    if (
        !message ||
        controller
    ) {

        return;
    }


    if (!currentChatId) {

        await createNewChat();
    }


    if (!currentChatId) {
        return;
    }


    const detectedAgent =
        detectAgent(
            message
        );


    const selected =
        AGENTS[detectedAgent] ||
        AGENTS.nexa;


    input.value =
        "";


    resizeInput();


    setAgent(
        detectedAgent,
        selected.working,
        true
    );


    thinking.classList.remove(
        "hidden"
    );


    stopButton.classList.remove(
        "hidden"
    );


    sendButton.disabled =
        true;


    controller =
        new AbortController();


    try {

        const response =
            await fetch(
                "/chat",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:
                                message,

                            chat_id:
                                currentChatId
                        }),

                    signal:
                        controller.signal
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server error "
                + response.status
            );
        }


        const data =
            await response.json();


        if (data.chat_id) {

            currentChatId =
                data.chat_id;
        }


        let finalAgent =
            detectedAgent;


        if (
            data.agent &&
            AGENTS[data.agent]
        ) {

            finalAgent =
                data.agent;
        }


        const ready =
            AGENTS[finalAgent] ||
            AGENTS.nexa;


        setAgent(
            finalAgent,
            ready.ready,
            false
        );


        lastHistorySignature =
            "";


        await loadHistory(
            true
        );


    } catch (error) {

        if (
            error.name ===
            "AbortError"
        ) {

            setAgent(
                "nexa",
                "Stopped",
                false
            );

        } else {

            console.error(
                error
            );


            setAgent(
                "nexa",
                "Connection error",
                false
            );
        }


    } finally {

        controller =
            null;


        thinking.classList.add(
            "hidden"
        );


        stopButton.classList.add(
            "hidden"
        );


        sendButton.disabled =
            false;


        input.focus();
    }
}


// ========================================================
// HISTORY CLOSE
// ========================================================

function closeHistory() {

    app.classList.add(
        "history-closed"
    );


    if (openHistoryButton) {

        openHistoryButton
            .classList
            .remove(
                "hidden"
            );
    }


    localStorage.setItem(
        "nexa_history_closed",
        "true"
    );
}


// ========================================================
// HISTORY OPEN
// ========================================================

function openHistory() {

    app.classList.remove(
        "history-closed"
    );


    if (openHistoryButton) {

        openHistoryButton
            .classList
            .add(
                "hidden"
            );
    }


    localStorage.setItem(
        "nexa_history_closed",
        "false"
    );
}


// ========================================================
// RESIZE INPUT
// ========================================================

function resizeInput() {

    input.style.height =
        "auto";


    input.style.height =
        Math.min(
            input.scrollHeight,
            130
        ) + "px";
}


// ========================================================
// SCROLL
// ========================================================

function scrollBottom() {

    chat.scrollTop =
        chat.scrollHeight;
}


// ========================================================
// EVENTS
// ========================================================

sendButton.addEventListener(
    "click",
    sendMessage
);


stopButton.addEventListener(
    "click",
    () => {

        if (controller) {

            controller.abort();
        }
    }
);


newChatButton.addEventListener(
    "click",
    createNewChat
);


if (collapseButton) {

    collapseButton.addEventListener(
        "click",
        closeHistory
    );
}


if (openHistoryButton) {

    openHistoryButton.addEventListener(
        "click",
        openHistory
    );
}


input.addEventListener(
    "input",
    resizeInput
);


input.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


// ========================================================
// HISTORY SYNC
// ========================================================

function startHistorySync() {

    setInterval(
        async () => {

            if (!controller) {

                await loadHistory();
            }

        },
        1000
    );
}


// ========================================================
// INITIALIZE
// ========================================================

async function initialize() {

    const historyClosed =
        localStorage.getItem(
            "nexa_history_closed"
        );


    if (
        historyClosed ===
        "true"
    ) {

        closeHistory();

    } else {

        openHistory();
    }


    await loadHistory(
        true
    );


    if (!chats.length) {

        await createNewChat();
    }


    setAgent(
        "nexa",
        "Ready",
        false
    );


    startHistorySync();


    input.focus();
}


initialize();