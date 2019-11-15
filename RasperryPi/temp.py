##content = "blqblqwrnj\r\njuiwrfkuiwfui\r\n"
##
##with open("test.txt", "w") as file:
##    file.write(content)
##

import time

message = [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 0]
print(len(message))
print("".join(map(chr, message)))


with open("data/test.txt", "w") as file:
    file.write("".join(map(chr, message)))
    

with open("data/test_bytes.txt", "wb") as file:
    file.write(bytes(message))

flag = "eof"
print([ord(char) for char in flag])

def create_record():
    now = datetime.now()
    #current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%y%m%d")
    record_path = DATA_PATH + current_date
    try:
        os.mkdir(record_path)
    except FileExistsError:
        pass