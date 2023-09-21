import sys
import time
import re
from typing import List

from entities.settings import settings
from app import AlgoSimulator, AlgoMinimal
from entities.settings.direction import Direction
from entities.rpi.rpi_client import RPiClient
from entities.rpi.rpi_server import RPiServer
from entities.map.obstacle import Obstacle
from entities.robot.actualrun.actualrun import actualRun


def parse_obstacle_data(data) -> List[Obstacle]:
    obs = []
    for obstacle_params in data:
        obs.append(Obstacle(obstacle_params[0],
                            obstacle_params[1],
                            Direction(obstacle_params[2]),
                            obstacle_params[3]))
    # [[x, y, orient, index], [x, y, orient, index]]
    return obs


def run_simulator(string):
    # Fill in obstacle positions with respect to lower bottom left corner.
    # (x-coordinate, y-coordinate, Direction)

    # Assuming direction is represented as 'N', 'E', 'S', 'W' for North, East, South, West respectively
    #obstacles = []
    #for i in range(5):
        #user_input = input("Enter x, y, and direction (separated by commas): ")
        #x, y, direction = user_input.split(",")
        #direction_mapping = {'N': 90, 'E': 0, 'S': -90, 'W': 180}
        #direction_angle = direction_mapping.get(direction.upper(), 0)
        #obstacles.append((int(x), int(y), direction_angle,i))


    string = "PC,Startpoint,1,1,nPC,Obstacle,10,7,nPC,PC,Obstacle,14,4,n,PC,Obstacle,2,9,ePC,Obstacle,2,18,sPC,Obstacle,15,15,w"
    #string = "PC,Startpoint,1,1,nPC,Obstacle,7,5,n"
    # Extract all occurrences of "Obstacle" followed by three comma-separated values
    matches = re.findall(r"Obstacle,(\d+),(\d+),(\w)", string)
    direction_mapping = {'N': 90, 'E': 0, 'S': -90, 'W': 180}
    obstacles = [[int(x)*10 + 5, int(y)*10 + 5, direction_mapping[direction.upper()], i] for i, (x, y, direction) in enumerate(matches)]

    #obstacles = [[105, 75, 90, 0], [145, 45, 90, 1], [25, 95, 0, 2], [25, 185, -90, 3], [155, 155, 180, 4]]
    #obstacles = [[105, 75, 90, 0]]
    obs = parse_obstacle_data(obstacles)
    #app = AlgoSimulator(obs)
    #app.init()
    #app.execute()

    app = AlgoMinimal(obs)
    app.init()
    app.execute()

    # Send the list of commands over.
    print("Sending list of commands to RPi...")
    commands = app.robot.convert_all_commands()
    # Using a loop to print each string command
    return commands
    #for command in commands:
        #print(command)



def run_minimal(also_run_simulator):
    # Create a client to connect to the RPi.
    print(f"Attempting to connect to {settings.RPI_HOST}:{settings.RPI_PORT}")
    client = RPiClient(settings.RPI_HOST, settings.RPI_PORT)
    # Wait to connect to RPi.
    while True:
        try:
            client.connect()
            break
        except OSError:
            pass
        except KeyboardInterrupt:
            client.close()
            sys.exit(1)
    print("Connected to RPi!\n")

    print("Waiting to receive obstacle data from RPi...")
    # Create a server to receive information from the RPi.
    server = RPiServer(settings.PC_HOST, settings.PC_PORT)
    # Wait for the RPi to connect to the PC.
    try:
        server.start()
    except OSError or KeyboardInterrupt as e:
        print(e)
        server.close()
        client.close()
        sys.exit(1)

    # At this point, both the RPi and the PC are connected to each other.
    # Create a synchronous call to wait for RPi data.
    obstacle_data: list = server.receive_data()
    server.close()
    print("Got data from RPi:")
    print(obstacle_data)

    obstacles = parse_obstacle_data(obstacle_data)
    if also_run_simulator:
        app = AlgoSimulator(obstacles)
        app.init()
        app.execute()
    app = AlgoMinimal(obstacles)
    app.init()
    app.execute()

    # Send the list of commands over.
    print("Sending list of commands to RPi...")
    commands = app.robot.convert_all_commands()
    client.send_message(commands)
    client.close()


def run_rpi():
    while True:
        run_minimal(False)
        time.sleep(5)


if __name__ == '__main__':
    #Listen from Android, return the string we are listening
    #string = listenfromAndroid()

    #Put the string into Algo, generate the command
    string = "PC,Startpoint,1,1,nPC,Obstacle,10,7,nPC,PC,Obstacle,14,4,n,PC,Obstacle,2,9,ePC,Obstacle,2,18,sPC,Obstacle,15,15,w"
    commands = run_simulator(string)

    #Put the command into driving function
    actualRun(commands)

    #run_simulator()
