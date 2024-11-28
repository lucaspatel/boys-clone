from datetime import datetime

def process_messages(input_file, phone_to_name):
    """Process messages from an input file and return a list of processed blocks."""
    processed_blocks = []

    with open(input_file, 'r') as infile:
        current_block = []  # store lines for the current message block
        empty_line_seen = False  

        for line in infile:
            if line.strip() == '':
                current_block.append(line)
                empty_line_seen = True 
            elif empty_line_seen and line.strip() != '':
                # process the current block and start a new one.
                current_block = current_block[:-1]
                processed_blocks.append(process_block(current_block, phone_to_name))
                current_block = [line]  
                empty_line_seen = False  
            else:
                current_block.append(line)

        if current_block: 
            processed_blocks.append(process_block(current_block, phone_to_name))

    return processed_blocks

def write_messages_to_file(processed_blocks, output_file):
    """Write a list of processed message blocks to an output file."""
    with open(output_file, 'w') as outfile:
        for block in processed_blocks:
            outfile.writelines(block)
            outfile.write('\n')

