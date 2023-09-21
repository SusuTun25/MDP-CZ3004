import math
from queue import PriorityQueue
from typing import List, Tuple

from entities.settings import settings
from entities.robot.command import Command
from entities.robot.movement.dubins_command import DubinsCommand
from entities.grid.grid import Grid
from entities.grid.node import Node
from entities.grid.position import RobotPosition


class DubinsPath:
    def __init__(self, grid, brain, start: RobotPosition, end: RobotPosition):
        self.grid: Grid = grid.copy()
        self.brain = brain
        self.start = start
        self.end = end

    def get_neighbours(self, pos: RobotPosition) -> List[Tuple[Node, RobotPosition, float, Command]]:
        neighbours = []

        dubins_radius = settings.DUBINS_RADIUS
        dubins_commands = [
            DubinsCommand(90, dubins_radius),
            DubinsCommand(-90, dubins_radius),
            DubinsCommand(180, dubins_radius),
        ]

        for c in dubins_commands:
            after, p = self.check_valid_command(c, pos)
            if after:
                cost = self.calculate_cost(c, dubins_radius)
                neighbours.append((after, p, cost, c))

        return neighbours

    def check_valid_command(self, command: Command, p: RobotPosition):
        p = p.copy()
        command.apply_on_pos(p)
        if self.grid.check_valid_position(p) and (after := self.grid.get_coordinate_node(*p.xy())):
            after.pos.direction = p.direction
            return after.copy(), p
        return None, None

    def calculate_cost(self, command: Command, dubins_radius: float) -> float:
        # Calculate the cost of a Dubins path command
        return command.length() * dubins_radius

    def heuristic(self, curr_pos: RobotPosition):
        dx = abs(curr_pos.x - self.end.x)
        dy = abs(curr_pos.y - self.end.y)
        return math.sqrt(dx ** 2 + dy ** 2)

    def start_astar(self):
        frontier = PriorityQueue()
        backtrack = dict()
        cost = dict()

        goal_node = self.grid.get_coordinate_node(*self.end.xy()).copy()
        goal_node.pos.direction = self.end.direction

        start_node: Node = self.grid.get_coordinate_node(*self.start.xy()).copy()
        start_node.direction = self.start.direction

        offset = 0
        frontier.put((0, offset, (start_node, self.start)))
        cost[start_node] = 0
        backtrack[start_node] = (None, None)

        while not frontier.empty():
            priority, _, (current_node, current_position) = frontier.get()

            if current_node == goal_node:
                self.extract_commands(backtrack, goal_node)
                return current_position

            for new_node, new_pos, weight, c in self.get_neighbours(current_position):
                new_cost = cost.get(current_node) + weight

                if new_node not in backtrack or new_cost < cost[new_node]:
                    offset += 1
                    priority = new_cost + self.heuristic(new_pos)

                    frontier.put((priority, offset, (new_node, new_pos)))
                    backtrack[new_node] = (current_node, c)
                    cost[new_node] = new_cost

        return None

    def extract_commands(self, backtrack, goal_node):
        commands = []
        curr = goal_node
        while curr:
            curr, c = backtrack.get(curr, (None, None))
            if c:
                commands.append(c)
        commands.reverse()
        self.brain.commands.extend(commands)
