import tools.keyboard as keyboard
import time

def skip_song():
    keyboard.press_key("next_track")
    return "The song has been skipped"

def previous_song():
    keyboard.press_key("previous_track")
    time.sleep(0.1)
    keyboard.press_key("previous_track")

    return "The previous song is now playing"