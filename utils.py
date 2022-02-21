from uiparser import generate_window

def get_window(window_name):
    return generate_window("windows/" + window_name + ".xml")