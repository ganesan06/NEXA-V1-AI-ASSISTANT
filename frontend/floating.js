const promptText =
    document.getElementById(
        "promptText"
    );

const responseText =
    document.getElementById(
        "responseText"
    );

const input =
    document.getElementById(
        "floatingInput"
    );

const sendButton =
    document.getElementById(
        "floatingSend"
    );

const thinking =
    document.getElementById(
        "floatingThinking"
    );

const messages =
    document.getElementById(
        "floatingMessages"
    );


let chatId = null;

let floatingId = null;

let sending = false;


/* ====================================================== */
/* GET FLOAT ID */
/* ====================================================== */

const params =
    new URLSearchParams(
        window.location.search
    );


floatingId =
    params.get("id");


console.log(
    "NEXA FLOAT ID:",
    floatingId
);


/* ====================================================== */
/* LOAD FLOAT DATA */
/* ====================================================== */

async function loadFloatingChat() {

    if (!floatingId) {

        promptText.textContent =
            "Missing floating ID.";

        responseText.textContent =
            "This floating window does not have an ID.";

        return;
    }


    try {

        const response =
            await fetch(
                `/floating-data/${floatingId}`,
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        console.log(
            "FLOAT DATA:",
            data
        );


        if (
            data.status ===
            "error"
        ) {

            throw new Error(
                data.response ||
                "Floating chat not found."
            );
        }


        chatId =
            data.chat_id;


        promptText.textContent =
            data.prompt ||
            "No prompt.";


        responseText.textContent =
            data.response ||
            "No response.";


    } catch (error) {

        console.error(
            "FLOAT LOAD ERROR:",
            error
        );


        promptText.textContent =
            "Unable to load prompt.";


        responseText.textContent =
            "Unable to load floating chat.";
    }
}


/* ====================================================== */
/* ADD MESSAGE */
/* ====================================================== */

function addMessage(
    role,
    text
) {

    const section =
        document.createElement(
            "section"
        );


    section.className =
        role === "user"
            ? "message user"
            : "message";


    const label =
        document.createElement(
            "div"
        );


    label.className =
        "label";


    label.textContent =
        role === "user"
            ? "YOU"
            : "NEXA";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        role === "user"
            ? "bubble user-bubble"
            : "bubble";


    bubble.textContent =
        text;


    section.appendChild(
        label
    );


    section.appendChild(
        bubble
    );


    messages.appendChild(
        section
    );


    scrollBottom();


    return bubble;
}


/* ====================================================== */
/* SEND */
/* ====================================================== */

async function sendMessage() {

    const message =
        input.value.trim();


    if (
        !message ||
        sending
    ) {

        return;
    }


    if (!chatId) {

        addMessage(
            "assistant",
            "This floating chat is not connected to browser history."
        );

        return;
    }


    sending = true;


    input.value = "";


    resizeInput();


    addMessage(
        "user",
        message
    );


    const assistantBubble =
        addMessage(
            "assistant",
            "Working..."
        );


    thinking.classList.remove(
        "hidden"
    );


    sendButton.disabled =
        true;


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
                                chatId
                        })
                }
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        console.log(
            "FLOAT CHAT RESPONSE:",
            data
        );


        assistantBubble.textContent =
            data.response ||
            "No response returned.";


        /*
            server.py saves this prompt + response
            into chatId.

            Browser script.js polls /history,
            so it appears in the same browser chat.
        */


    } catch (error) {

        console.error(
            "FLOAT CHAT ERROR:",
            error
        );


        assistantBubble.textContent =
            "Unable to connect to NEXA.";


    } finally {

        sending = false;


        thinking.classList.add(
            "hidden"
        );


        sendButton.disabled =
            false;


        input.focus();
    }
}


/* ====================================================== */
/* INPUT HEIGHT */
/* ====================================================== */

function resizeInput() {

    input.style.height =
        "auto";


    input.style.height =
        Math.min(
            input.scrollHeight,
            110
        ) + "px";
}


/* ====================================================== */
/* SCROLL */
/* ====================================================== */

function scrollBottom() {

    messages.scrollTop =
        messages.scrollHeight;
}


/* ====================================================== */
/* EVENTS */
/* ====================================================== */

sendButton.addEventListener(
    "click",
    sendMessage
);


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


/* ====================================================== */
/* START */
/* ====================================================== */

async function initialize() {

    await loadFloatingChat();

    scrollBottom();

    input.focus();
}


initialize();