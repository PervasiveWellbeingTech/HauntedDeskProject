import time
from datetime import datetime

EOF_LINE = [101, 111, 102, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # e, o, f, 0, 0, 0...
TIME_EXCEEDED_FLAG = "time_exceeded"
SIZE_EXCEEDED_FLAG = "size_exceeded"


def pipe_string_to_hexa(pipe):
    """
    Converts a string id to an hexadecimal list.
    Ex: "2DECAF0001" -> [0x2D, 0xEC, 0xAF, 0x00, 0x01]
    """
    return [int("0x" + pipe[i:i+2], 16) for i in range(0, len(pipe)-1, 2)]


def get_desks_info():
    lines = []
    with open("desks_register.txt") as file:
        for line in file:
            lines.append(line.rstrip())

    names, pipes = [], []
    for i in range(0, len(lines), 3):
        names.append(lines[i])
        pipes.append([pipe_string_to_hexa(lines[i + 1]),
                      pipe_string_to_hexa(lines[i + 2])])

    return names, pipes
        

def send_message(radio, message, debug=False):    
    result = radio.write(message)
    print("Result of sending:", result)
    if debug:
        print("Message sent: {}".format(message))


def listen_message_light(radio, time_out=2, debug=False):
    """
    Waits for a certain time (time_out).
    If a message is received, the message is read and store in a list.
    Else, returns an empty list.
    """
    start = time.time()
    while not radio.available():
        time.sleep(0.01)
        
        if time.time() - start > time_out:
            if debug:
                print("WARNING: Time out - Stop listening.")
            return []
        
    message_received = []
    radio.read(message_received, radio.getDynamicPayloadSize())
    
    if debug:
        print("Message received.")
    
    return message_received


def listen_message(radio, time_out=2, debug=False):
    """
    Same as listen_message_light but with a start/stop listening
    at the begining/end of the function
    """
    if debug:
        print("Start listening.")
        
    radio.startListening()
    message_received = listen_message_light(radio, time_out, debug)
    radio.stopListening()
    
    if debug:
        print("Stop listening.")
        
    return message_received


def clean_message(message, debug=False):
    """
    message -> list
    Removes the last character of the message.
    Converts the message in ASCII.
    Returns the message as a string.
    """
    if message:
        message = "".join(map(chr, message))
        if debug:
            print("Message cleaned:", message)
        return message
    return ""


def listen_file_info(radio, debug=False):
    """
    Listens for two piece of information:
        - a file name
        - a file size
    If both pieces of information are received,
    returns a True flag and the information.
    Else, returns a False flag and empty strings.
    """
    file_name_message = listen_message(radio, debug=debug)
    if file_name_message:
        file_size_message = listen_message(radio, debug=debug)
        if file_size_message:
            file_name = clean_message(file_name_message, debug).rstrip(chr(0))
            file_size = clean_message(file_size_message, debug).rstrip(chr(0))
            if file_name.endswith(".txt") and file_size.isnumeric():
                return True, (file_name, file_size)
            else:
                if debug:
                    print("WARNING: bad file name and/or file size")
                return False, ("File info received but bad format", "")
        return False, ("File name received but not file size", "")
    return False, ("Nothing received", "")


def receive_file(radio, file_name, file_size, debug=False):
    """
    Receives a file line by line.
    End of the reception when an EOF_LINE is received or
    if the reception time for a line exceeds a given duration (defined
    in the listen_message_light function).
    """
    if debug:
        print("Start receiving file {} ({} bytes)".format(file_name, file_size))
    
    radio.startListening()
    counter = 0
    
    with open(file_name, "wb") as file:
        line = listen_message_light(radio, debug=debug)
        while line and line != EOF_LINE:
            counter += 32
            print(counter, file_size)
            file.write(bytes(line))
            line = listen_message_light(radio)
    
    radio.stopListening()
    
    if debug:
        print("File received.")
        

def timed_receive_file(radio, file_name, file_size, stop_time, debug=False):
    if debug:
        print("Start receiving file {} ({} bytes)".format(file_name, file_size))
    
    radio.startListening()
    counter = 0
    
    with open(file_name, "wb") as file:
        line = listen_message_light(radio, debug=debug)
        while line and line != EOF_LINE:
            counter += 32
            print(counter, file_size)
            file.write(bytes(line))
            line = listen_message_light(radio)
            
            if datetime.now().second > stop_time:
                if debug:
                    print("WARNING: File transmission interrupted - Time > Stop time")
                return "interrupted"
    
    radio.stopListening()
    
    if debug:
        print("File received.")


def get_time_in_seconds():
    """Gets the current time and gives this time in seconds."""
    
    current_time = datetime.now()
    
    current_second = current_time.second
    current_minute = current_time.minute
    current_hour = current_time.hour
    
    current_time_in_seconds = current_second + 60 * current_minute + 3600 * current_hour
    
    return current_time_in_seconds


def real_timed_receive_file(radio, file_name, file_size, stop_time, start_time, debug=False):
    """Same as the receive file function but with a given timelapse to receive the file."""
    
    if debug:
        print("Start receiving file {} ({} bytes)".format(file_name, file_size))
    
    radio.startListening()
    bytes_counter = 0
    file_size = int(file_size)
    
    with open(file_name, "wb") as file:
        line = listen_message_light(radio, debug=debug)
        while line and line != EOF_LINE:
            bytes_counter += 32
            print(bytes_counter, file_size)
            file.write(bytes(line))
            line = listen_message_light(radio)
            
            current_time_in_seconds = get_time_in_seconds()
            
            if stop_time < current_time_in_seconds < start_time:
                if debug:
                    print("WARNING: File transmission interrupted - Time > Stop time")
                return TIME_EXCEEDED_FLAG

            if bytes_counter > file_size:
                if debug:
                    print("WARNING: File transmission interrupted - Bytes counter > File size")
                return SIZE_EXCEEDED_FLAG
    
    radio.stopListening()
    
    if debug:
        print("File received.")
