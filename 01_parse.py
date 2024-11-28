from util import process_messages, write_messages_to_file
from collections import Counter
from datetime import datetime, timedelta
import os

def parse_datetime(date_str):
    """Parse a datetime string into a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

def process_block(block, phone_to_name):
    """Process each message block, applying various transformations."""
    clean_block = []
    skip_lines = False

    for i, line in enumerate(block):
        stripped_line = line.strip()

        # skip lines starting from "Reactions:" up to an empty line
        if any(stripped_line.startswith(prefix) for prefix in ["Reactions:", "Laughed by", "Loved by", "Emphasized by", "Disliked by"]) or "renamed the conversation to" in stripped_line:
            skip_lines = True
            continue 
        if skip_lines and stripped_line == "":
            skip_lines = False  
            continue  # also skip the empty line immediately following the reactions block

        # replace phone number with name
        if stripped_line in phone_to_name:
            line = line.replace(stripped_line, phone_to_name[stripped_line])

        # delete "Read by you after" statements
        if "(Read by you after" in stripped_line:
            line = line.split("(Read")[0] + '\n'

        clean_block.append(line)

    # attempt to convert the date on the first line of the clean_block, if it exists
    if clean_block:
        try:
            # extract the first line and try to convert the date
            date_str = clean_block[0].strip()
            date_obj = parse_datetime(date_str)
            clean_block[0] = date_obj.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        except ValueError:
            pass 

    return clean_block

def group_conversations(blocks, time_lapse_hours=6):
    """Group messages into conversations based on a time lapse between messages."""
    conversations = []
    current_conversation = []
    previous_time = None

    for block in blocks:
        if not block:
            continue
        # extract the timestamp from the first line of the block
        timestamp_str = block[0].strip()
        try:
            timestamp = parse_datetime(timestamp_str)
        except ValueError:
            print(f"Skipping block due to invalid timestamp: {timestamp_str}")
            continue

        if previous_time and (timestamp - previous_time > timedelta(hours=time_lapse_hours)):
            # start a new conversation if the time lapse exceeds the threshold
            conversations.append(current_conversation)
            current_conversation = [block]
        else:
            current_conversation.append(block)

        previous_time = timestamp

    if current_conversation:
        conversations.append(current_conversation)

    return conversations

def write_conversations_to_files(conversations, output_dir):
    """Write each conversation to a separate text file, named by the first datetime in the conversation."""
    for conversation in conversations:
        if not conversation or not conversation[0]:
            continue

        # get the filename from the first date in the conversation
        timestamp_str = conversation[0][0].strip()
        try:
            timestamp = parse_datetime(timestamp_str)
            filename = timestamp.strftime("%Y-%m-%d_%H-%M-%S.txt")
            write_messages_to_file(conversation, f"{output_dir}/{filename}")
        except ValueError:
            print(f"Skipping conversation due to invalid timestamp: {timestamp_str}")

phone_to_name = {
    'Me': 'Lucas',
}

input_file = 'out/boys.txt'

processed_blocks = process_messages(input_file, phone_to_name)

# data exploration
# TODO: filter out nonsense, ie one-line block
# block_lengths = Counter(processed_blocks))
# print Counter(block_lengths)

# split into conversations which are groups of messages with <6 hour lapse between
conversations = group_conversations(processed_blocks)
output_dir = 'out/conversations'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
write_conversations_to_files(conversations, output_dir)
