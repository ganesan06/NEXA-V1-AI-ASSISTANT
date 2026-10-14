from google.adk.agents import LlmAgent

from .tools import (
    open_apple_music,
    play_apple_music,
    open_spotify,
    play_spotify,
    play_pause_music,
    next_song,
    previous_song
)


music_agent = LlmAgent(
    name="music_agent",

    model="gemini-3.5-flash",

    description="""
    Controls Apple Music and Spotify on Windows.
    """,

    instruction="""
    You are the music agent.

    If the user asks to open Apple Music,
    call open_apple_music().

    If the user asks to play a song,
    artist, album or playlist on Apple Music,
    call play_apple_music(query).

    Example:

    User:
    Play Rasathi Unna on Apple Music

    Call:
    play_apple_music(query="Rasathi Unna")


    If the user asks to open Spotify,
    call open_spotify().

    If the user asks to play something
    on Spotify,
    call play_spotify(query).


    If no music service is specified,
    use Apple Music.


    Pause or resume:
    play_pause_music()

    Next song:
    next_song()

    Previous song:
    previous_song()


    IMPORTANT:

    When the user asks to play something,
    use the play tool, not only the open tool.

    Never claim success when a tool
    reports an error.
    """,

    tools=[
        open_apple_music,
        play_apple_music,
        open_spotify,
        play_spotify,
        play_pause_music,
        next_song,
        previous_song
    ]
)