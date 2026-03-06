
def progress_bar(current, total):
    bar_length = 18
    filled = int(bar_length * current / total)
    bar = "━" * filled + "●" + "─" * (bar_length - filled)
    return f"{current} {bar} {total}"
