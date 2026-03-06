
QUEUE = {}

def add_to_queue(chat_id, song_data):
    if chat_id not in QUEUE:
        QUEUE[chat_id] = []
    QUEUE[chat_id].append(song_data)
    return len(QUEUE[chat_id])

def get_next_song(chat_id):
    if chat_id not in QUEUE or not QUEUE[chat_id]:
        return None
    return QUEUE[chat_id].pop(0)

def get_queue(chat_id):
    if chat_id not in QUEUE:
        return []
    return QUEUE[chat_id]

def clear_queue(chat_id):
    QUEUE[chat_id] = []
