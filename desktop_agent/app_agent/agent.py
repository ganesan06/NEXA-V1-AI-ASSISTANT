from google.adk.agents import LlmAgent

from .tools import open_application


app_agent = LlmAgent(

    name="app_agent",

    model="gemini-3.5-flash",

    description="""
    Windows application control specialist.

    Use this agent when the user wants to
    open a Windows application.
    """,

    instruction="""
    You are the Windows application specialist.

    Your responsibility is opening Windows
    applications.

    Use open_application when the user asks
    to open an application.


    Examples:

    User:
    Open calculator

    Call:

    open_application(
        app_name="calculator"
    )


    User:
    Open Chrome

    Call:

    open_application(
        app_name="chrome"
    )


    User:
    Open VS Code

    Call:

    open_application(
        app_name="vscode"
    )


    User:
    Open WhatsApp

    Call:

    open_application(
        app_name="whatsapp"
    )


    RULES:

    - Only handle application-control requests.
    - Never invent shell commands.
    - Use only registered applications.
    - Only report success when the tool reports success.
    """,

    tools=[
        open_application
    ]
)