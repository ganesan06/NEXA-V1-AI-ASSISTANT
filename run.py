import socket
import threading
import time
import webbrowser

import uvicorn
import webview

from server import floating_window_queue


# =========================================================
# SETTINGS
# =========================================================

HOST = "127.0.0.1"
PORT = 8000

SERVER_URL = f"http://{HOST}:{PORT}"


# =========================================================
# SERVER CHECK
# =========================================================

def server_is_ready():

    try:
        connection = socket.create_connection(
            (HOST, PORT),
            timeout=1
        )

        connection.close()

        return True

    except OSError:
        return False


# =========================================================
# START FASTAPI
# =========================================================

def start_server():

    print()
    print("[NEXA] Starting FastAPI server...")

    config = uvicorn.Config(
        "server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )

    server = uvicorn.Server(
        config
    )

    server.run()


# =========================================================
# WAIT FOR SERVER
# =========================================================

def wait_for_server():

    print("[NEXA] Waiting for server...")

    for _ in range(50):

        if server_is_ready():

            print("[NEXA] Server ready.")

            return True

        time.sleep(0.2)

    return False


# =========================================================
# OPEN MAIN NEXA IN BROWSER
# =========================================================

def open_browser():

    print()
    print("[NEXA] Opening browser...")
    print("[NEXA]", SERVER_URL)

    webbrowser.open(
        SERVER_URL
    )


# =========================================================
# FLOATING WINDOW
# =========================================================

def create_float_window(
    floating_id
):

    url = (
        f"{SERVER_URL}/floating"
        f"?id={floating_id}"
    )

    print()
    print("=" * 55)
    print("[NEXA] FLOAT WINDOW REQUEST")
    print("ID:", floating_id)
    print("URL:", url)
    print("=" * 55)
    print()

    try:

        window = webview.create_window(
            title="NEXA Float",
            url=url,

            width=500,
            height=600,

            min_size=(
                380,
                350
            ),

            resizable=True,

            on_top=True,

            hidden=False
        )

        print(
            "[NEXA] Floating window created."
        )

        return window

    except Exception as error:

        print()
        print("=" * 55)
        print("[NEXA FLOAT WINDOW ERROR]")
        print(type(error).__name__)
        print(error)
        print("=" * 55)
        print()

        return None


# =========================================================
# FLOAT QUEUE WATCHER
# =========================================================

def watch_float_requests():

    print()
    print(
        "[NEXA] Float manager started."
    )
    print()

    while True:

        try:

            floating_id = (
                floating_window_queue.get()
            )

            print()
            print(
                "[NEXA] Received float:",
                floating_id
            )

            create_float_window(
                floating_id
            )

            floating_window_queue.task_done()

        except Exception as error:

            print()
            print(
                "[FLOAT MANAGER ERROR]"
            )
            print(
                type(error).__name__
            )
            print(error)
            print()


# =========================================================
# START FLOAT MANAGER
# =========================================================

def start_float_manager():

    thread = threading.Thread(
        target=watch_float_requests,
        daemon=True
    )

    thread.start()


# =========================================================
# WEBVIEW READY
# =========================================================

def after_webview_started():

    print()
    print(
        "[NEXA] Native window engine ready."
    )
    print()

    start_float_manager()

    time.sleep(0.5)

    open_browser()


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 55)
    print("                     NEXA")
    print("              DESKTOP AI SYSTEM")
    print("=" * 55)
    print()


    # -----------------------------------------------------
    # START FASTAPI
    # -----------------------------------------------------

    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()


    # -----------------------------------------------------
    # WAIT FOR FASTAPI
    # -----------------------------------------------------

    if not wait_for_server():

        print()
        print(
            "[NEXA] ERROR:"
        )

        print(
            "FastAPI server did not start."
        )

        return


    # -----------------------------------------------------
    # CREATE HIDDEN WEBVIEW WINDOW
    #
    # pywebview needs at least one native window before
    # webview.start().
    # -----------------------------------------------------

    webview.create_window(
        title="NEXA Engine",
        html="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NEXA</title>
        </head>
        <body>
        </body>
        </html>
        """,

        width=1,
        height=1,

        hidden=True
    )


    # -----------------------------------------------------
    # START WEBVIEW
    #
    # after_webview_started runs after the GUI engine
    # has initialized.
    # -----------------------------------------------------

    print(
        "[NEXA] Starting native window engine..."
    )

    webview.start(
        after_webview_started,
        debug=False
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()