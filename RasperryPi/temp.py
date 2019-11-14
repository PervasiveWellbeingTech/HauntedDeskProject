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