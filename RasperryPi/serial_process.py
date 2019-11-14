import time


def send_message(usb_port, ser, message, debug=False):
    message_encode = message.encode()
    ser.write(message_encode)
    
    if debug:
        print("Port {}: command '{}' sent.".format(usb_port, message))
    
    
def listen_port(usb_port, ser, debug=False):
    time.sleep(1)
    message = []
    
    while (ser.inWaiting() > 0):
        message.append(ser.read().decode("utf-8"))
        time.sleep(0.01)
        
    if debug:
        print("Port {}: {} byte(s) received.".format(usb_port, len(message)))

    return "".join(message).rstrip("\n")


def run(usb_port, ser, debug=True):
    # Send message to Arduino to get file
    send_message(usb_port, ser, "data", debug)
    message = listen_port(usb_port, ser, debug)
    if debug:
        print(message)
    
    # Listen the answer (file name and file size)
    if message:
        file_name, file_size = message.split("\n")
        if debug:
            print("Port {}: {} file opened ({} byte(s) incoming).".format(usb_port, file_name, file_size))  
        
        # Send message to Arduino to launch the file transfer
        send_message(usb_port, ser, "ok", debug)
        time.sleep(2)
        print("Wait...")
        
        # Get the file
        file_content = listen_port(usb_port, ser, debug)
        
        # Save the file
        with open(file_name, "w") as file:
            file.write(file_content)
            
        if debug:
            print("Port {}: {} file saved.".format(usb_port, file_name))
    else:
        print("Port {}: ERROR: no file name or size received.".format(usb_port))
