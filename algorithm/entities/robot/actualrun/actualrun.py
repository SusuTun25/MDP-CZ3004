import time
import threading

def moveForward(distance):
    print(f"Moving forward {distance} units.")

def moveRight(distance):
    print(f"Moving right {distance} units.")

def moveLeft(distance):
    print(f"Moving left {distance} units.")

def moveBack(distance):
    print(f"Moving back {distance} units.")

def ScanImage():
    global isProcessing
    print("Scanning image.")
    time.sleep(5)  # Simulating image processing time
    isProcessing = False

commands = ['f0020', 'r0090', 'f0020', 'l0090', 'l0090', 's0002', 'b0030', 'r0090', 'l0090', 'r0090', 's0003', 'b0020', 'r0090', 'f0080', 's0004', 'b0040', 'r0090', 'f0030', 's0000', 'b0010', 'l0090', 'r0090', 's0001']

isProcessing = False
lock = threading.Lock()

def actualRun(commands):
    global isProcessing

    switch_case = {
        'f': moveForward,
        'r': moveRight,
        'l': moveLeft,
        'b': moveBack,
        's': ScanImage
    }

    for command in commands:
        instruction = command[0]  # Extract the instruction (first character)
        distanceValue = int(command[1:])  # Extract the distanceValue (last 4 characters)

        # Check if the instruction is 's' and there is no image processing ongoing
        if instruction == 's' and not isProcessing:
            with lock:
                # Start a new thread to run the ScanImage function
                isProcessing = True
                image_processing_thread = threading.Thread(target=switch_case[instruction])
                image_processing_thread.start()

        # Execute the corresponding function based on the instruction (except 's')
        elif instruction in switch_case and instruction != 's':
            switch_case[instruction](distanceValue)

        # Handle the case when 's' is encountered while image processing is ongoing
        elif instruction == 's' and isProcessing:
            print("Cannot scan image. Image processing is still ongoing.")

        else:
            print(f"Invalid instruction: {instruction}")

        # After processing, set isProcessing to False
        isProcessing = False if instruction == 's' else isProcessing

# Call the actualRun function with the commands list
actualRun(commands)

print("All commands executed.")
