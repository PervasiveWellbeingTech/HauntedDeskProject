import time

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
    TODO: simplify
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
            return True, (file_name, file_size)
    return False, ("", "")


def receive_file(radio, file_name, file_size, debug=False):
    if debug:
        print("Start receiving file {} ({} bytes)".format(file_name, file_size))
    
    radio.startListening()
    counter = 0
    
    with open(file_name, "wb") as file:
        line = listen_message_light(radio, debug=DEBUG)
        while line and line != EOF_LINE:
            counter += 32
            print(counter, file_size)
            file.write(bytes(line))
            line = listen_message_light(radio)
    
    radio.stopListening()
    
    if debug:
        print("File received.")