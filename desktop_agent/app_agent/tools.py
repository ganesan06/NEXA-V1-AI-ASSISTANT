import os
import subprocess


APPLICATIONS = {
    "calculator": {
        "command": ["calc.exe"]
    },

    "notepad": {
        "command": ["notepad.exe"]
    },

    "vscode": {
        "command": [
            "cmd",
            "/c",
            "start",
            "",
            "code"
        ]
    },

    "visual studio code": {
        "command": [
            "cmd",
            "/c",
            "start",
            "",
            "code"
        ]
    },

    "chrome": {
        "command": [
            "cmd",
            "/c",
            "start",
            "",
            "chrome"
        ]
    },

    "edge": {
        "command": [
            "cmd",
            "/c",
            "start",
            "",
            "msedge"
        ]
    },

    "whatsapp": {
        "protocol": "whatsapp:"
    },

    "apple music": {
        "protocol": "music:"
    },

    "spotify": {
        "protocol": "spotify:"
    }
}


def open_application(app_name: str) -> dict:
    """Open an approved Windows application."""

    app_name = app_name.lower().strip()

    app = APPLICATIONS.get(app_name)

    if app is None:
        return {
            "status": "error",
            "message": f"{app_name} is not registered."
        }

    try:

        if "protocol" in app:
            os.startfile(app["protocol"])

        else:
            subprocess.Popen(
                app["command"]
            )

        return {
            "status": "success",
            "message": f"{app_name} opened successfully."
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }