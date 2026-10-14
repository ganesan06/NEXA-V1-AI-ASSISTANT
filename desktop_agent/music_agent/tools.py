import os
import time
import subprocess

import pyautogui
from pywinauto import Desktop


# =========================================================
# SETTINGS
# =========================================================

APP_OPEN_WAIT = 4
SEARCH_WAIT = 4


# =========================================================
# FIND APPLE MUSIC WINDOW
# =========================================================

def find_apple_music_window():

    try:
        windows = Desktop(
            backend="uia"
        ).windows()

    except Exception:
        return None


    # -----------------------------------------------------
    # METHOD 1
    # Look for Apple Music in window title
    # -----------------------------------------------------

    for window in windows:

        try:

            title = (
                window
                .window_text()
                .strip()
                .lower()
            )

            if "apple music" in title:

                return window

        except Exception:
            continue


    # -----------------------------------------------------
    # METHOD 2
    # Detect Apple Music using its sidebar controls
    # -----------------------------------------------------

    for window in windows:

        try:

            texts = []

            for control in window.descendants():

                try:

                    text = (
                        control
                        .window_text()
                        .strip()
                        .lower()
                    )

                    if text:
                        texts.append(text)

                except Exception:
                    continue


            if (
                "home" in texts
                and
                "radio" in texts
                and
                "library" in texts
            ):

                return window

        except Exception:
            continue


    return None


# =========================================================
# FOCUS WINDOW
# =========================================================

def focus_window(window):

    if window is None:
        return False

    try:

        window.set_focus()

        time.sleep(0.5)

        return True

    except Exception:
        return False


# =========================================================
# OPEN APPLE MUSIC
# =========================================================

def open_apple_music() -> dict:

    try:

        os.startfile(
            "music:"
        )

        time.sleep(
            APP_OPEN_WAIT
        )

        return {
            "status": "success",
            "message": "Apple Music opened."
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# SEARCH APPLE MUSIC
# =========================================================

def search_apple_music(query: str):

    window = (
        find_apple_music_window()
    )


    if window:

        focus_window(
            window
        )


    # -----------------------------------------------------
    # Open search
    # -----------------------------------------------------

    pyautogui.hotkey(
        "ctrl",
        "f"
    )

    time.sleep(1)


    # -----------------------------------------------------
    # Clear old search
    # -----------------------------------------------------

    pyautogui.hotkey(
        "ctrl",
        "a"
    )

    time.sleep(0.3)


    # -----------------------------------------------------
    # Type new search
    # -----------------------------------------------------

    pyautogui.write(
        query,
        interval=0.05
    )

    time.sleep(0.5)


    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    pyautogui.press(
        "enter"
    )

    time.sleep(
        SEARCH_WAIT
    )


# =========================================================
# GET CONTROL TEXT
# =========================================================

def get_control_text(control):

    try:

        return (
            control
            .window_text()
            .strip()
        )

    except Exception:

        return ""


# =========================================================
# FIND SEARCH RESULT
# =========================================================

def find_search_result(
    window,
    query
):

    if window is None:

        return None


    query = (
        query
        .strip()
        .lower()
    )


    try:

        controls = (
            window
            .descendants()
        )

    except Exception:

        return None


    # =====================================================
    # EXACT MATCH FIRST
    #
    # rasathi unna == Rasathi Unna
    # =====================================================

    for control in controls:

        try:

            text = (
                get_control_text(
                    control
                )
                .lower()
            )


            if text == query:

                return control

        except Exception:

            continue


    # =====================================================
    # PARTIAL MATCH
    # =====================================================

    for control in controls:

        try:

            text = (
                get_control_text(
                    control
                )
                .lower()
            )


            if (
                query in text
                and
                text
            ):

                return control

        except Exception:

            continue


    return None


# =========================================================
# ACTIVATE APPLE MUSIC RESULT
# =========================================================

def activate_apple_music_result(
    result
):

    if result is None:

        return False


    # =====================================================
    # FIRST TRY:
    #
    # Double-click the actual song text.
    # =====================================================

    try:

        rect = (
            result
            .rectangle()
        )


        width = rect.width()

        height = rect.height()


        if (
            width > 5
            and
            height > 5
        ):

            x = (
                rect.left
                +
                width // 2
            )


            y = (
                rect.top
                +
                height // 2
            )


            pyautogui.doubleClick(
                x=x,
                y=y,
                interval=0.15
            )


            time.sleep(2)


            return True


    except Exception:

        pass


    # =====================================================
    # SECOND TRY:
    #
    # Move upward through the UI hierarchy and find
    # a result-card-sized parent.
    # =====================================================

    current = result


    for _ in range(6):

        try:

            parent = (
                current
                .parent()
            )


            if parent is None:

                break


            rect = (
                parent
                .rectangle()
            )


            width = (
                rect.width()
            )


            height = (
                rect.height()
            )


            # -------------------------------------------------
            # Approximate dimensions of an Apple Music
            # search-result card.
            #
            # NOT fixed screen coordinates.
            # -------------------------------------------------

            if (
                width >= 150
                and
                width <= 1000
                and
                height >= 40
                and
                height <= 300
            ):

                x = (
                    rect.left
                    +
                    width // 2
                )


                y = (
                    rect.top
                    +
                    height // 2
                )


                pyautogui.doubleClick(
                    x=x,
                    y=y,
                    interval=0.15
                )


                time.sleep(2)


                return True


            current = parent


        except Exception:

            break


    return False


# =========================================================
# PLAY APPLE MUSIC
# =========================================================

def play_apple_music(
    query: str
) -> dict:

    query = (
        query
        .strip()
    )


    if not query:

        return {
            "status": "error",
            "message": (
                "Please provide a song, "
                "artist, album or playlist."
            )
        }


    try:

        # =================================================
        # STEP 1
        # OPEN APPLE MUSIC
        # =================================================

        os.startfile(
            "music:"
        )


        time.sleep(
            APP_OPEN_WAIT
        )


        # =================================================
        # STEP 2
        # SEARCH
        # =================================================

        search_apple_music(
            query
        )


        # =================================================
        # STEP 3
        # FIND WINDOW
        # =================================================

        window = (
            find_apple_music_window()
        )


        if window is None:

            return {
                "status": "error",
                "message": (
                    "Apple Music searched correctly, "
                    "but its window controls could "
                    "not be accessed."
                )
            }


        focus_window(
            window
        )


        # =================================================
        # STEP 4
        # FIND EXACT SONG
        # =================================================

        result = (
            find_search_result(
                window,
                query
            )
        )


        if result is None:

            return {
                "status": "error",
                "message": (
                    f'Apple Music searched for "{query}", '
                    "but I could not identify the "
                    "matching Top Result."
                )
            }


        # =================================================
        # STEP 5
        # DOUBLE CLICK MATCHED RESULT
        # =================================================

        activated = (
            activate_apple_music_result(
                result
            )
        )


        if not activated:

            return {
                "status": "error",
                "message": (
                    f'Found "{query}" in Apple Music, '
                    "but could not activate the result."
                )
            }


        # =================================================
        # SUCCESS
        # =================================================

        return {
            "status": "success",
            "message": (
                f'Activated "{query}" '
                "in Apple Music."
            )
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# OPEN SPOTIFY
# =========================================================

def open_spotify() -> dict:

    try:

        os.startfile(
            "spotify:"
        )


        time.sleep(
            APP_OPEN_WAIT
        )


        return {
            "status": "success",
            "message": "Spotify opened."
        }


    except Exception:

        try:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    "spotify"
                ]
            )


            time.sleep(
                APP_OPEN_WAIT
            )


            return {
                "status": "success",
                "message": "Spotify opened."
            }


        except Exception as error:

            return {
                "status": "error",
                "message": str(error)
            }


# =========================================================
# SEARCH SPOTIFY
# =========================================================

def search_spotify(
    query: str
):

    pyautogui.hotkey(
        "ctrl",
        "k"
    )


    time.sleep(1)


    pyautogui.hotkey(
        "ctrl",
        "a"
    )


    time.sleep(0.3)


    pyautogui.write(
        query,
        interval=0.05
    )


    time.sleep(
        SEARCH_WAIT
    )


# =========================================================
# PLAY SPOTIFY
# =========================================================

def play_spotify(
    query: str
) -> dict:

    query = (
        query
        .strip()
    )


    if not query:

        return {
            "status": "error",
            "message": "Please provide a song or artist."
        }


    try:

        try:

            os.startfile(
                "spotify:"
            )

        except Exception:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    "spotify"
                ]
            )


        time.sleep(
            APP_OPEN_WAIT
        )


        search_spotify(
            query
        )


        pyautogui.press(
            "down"
        )


        time.sleep(0.5)


        pyautogui.press(
            "enter"
        )


        time.sleep(2)


        pyautogui.press(
            "space"
        )


        return {
            "status": "success",
            "message": (
                f'Searched for "{query}" '
                "on Spotify and sent "
                "the playback command."
            )
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# PLAY / PAUSE
# =========================================================

def play_pause_music() -> dict:

    try:

        pyautogui.press(
            "playpause"
        )


        return {
            "status": "success",
            "message": "Play/pause command sent."
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# NEXT SONG
# =========================================================

def next_song() -> dict:

    try:

        pyautogui.press(
            "nexttrack"
        )


        return {
            "status": "success",
            "message": "Next song command sent."
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# PREVIOUS SONG
# =========================================================

def previous_song() -> dict:

    try:

        pyautogui.press(
            "prevtrack"
        )


        return {
            "status": "success",
            "message": "Previous song command sent."
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }