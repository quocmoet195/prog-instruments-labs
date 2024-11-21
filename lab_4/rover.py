#!/usr/bin/env python3
import logging
import sys
from dataclasses import dataclass


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def turn(current_direction, turn_direction):
    if turn_direction == 'L':
        directions = ['N', 'W', 'S', 'E']
    elif turn_direction == 'R':
        directions = ['E', 'S', 'W', 'N']
    current_direction_index = directions.index(current_direction)
    new_direction_index = current_direction_index + 1
    new_direction = directions[new_direction_index % len(directions)]
    logging.debug(f'New direction is {new_direction}')
    return new_direction   

def move(position):
    (x, y, direction) = (position.x, position.y, position.heading)
    moves = {'N': lambda x, y: Position(x, y+1, direction),
             'W': lambda x, y: Position(x-1, y, direction),
             'S': lambda x, y: Position(x, y-1, direction),
             'E': lambda x, y: Position(x+1, y, direction),
            }
    new_position = moves[direction](x, y)
    logging.debug(f'Moved from {position} to {new_position}')
    return new_position  
@dataclass
class Position:
    x : int
    y : int
    heading : str

@dataclass
class Plateau:
    max_x : int
    max_y : int
    def __init__(self, max_x, max_y):
        if max_x <= 0 and max_y <= 0:
            logging.error(f'Cannot construct zero or negative sized plateau')
        self.max_x = max_x
        self.max_y = max_y
 
    def contains(self, position):
        return 0 <= position.x <= self.max_x and \
               0 <= position.y <= self.max_y

class Rover:
    def __init__(self, position, plateau):
        self.position = position
        self.plateau = plateau
        
    def move(self):
        new_position = move(self.position)
        if not self.plateau.contains(new_position):
            logging.error(f'Cannot move to {new_position} since it is off edge of plateau')
        self.position = new_position  
        logging.info(f'Moved to {self.position}')

    def turn(self, direction):
        new_heading = turn(self.position.heading, direction)
        self.position = Position(self.position.x, self.position.y, new_heading)
        logging.info(f'Turned to {self.position.heading}')
        
    def __repr__(self):
        return f"Rover({self.position}, {self.plateau})"
    
    def report_position(self):
        return f"{self.position.x} {self.position.y} {self.position.heading}\n"
        
class World:
    def __init__(self, plateau):
        self.plateau = plateau
        self.rovers = []
        self.instructions = []
        
    def add_rover(self, rover):
        self.rovers.append(rover)
        logging.debug(f'Added rover: {rover}')
        
    def add_instructions(self, instructions):
        self.instructions.append(instructions)
        
    def follow_instructions(self):
        for index, rover in enumerate(self.rovers):
            instructions = self.instructions[index]
            logging.debug(f'Rover {index} following instructions: {instructions}')
            for c in instructions:
                if c == 'M':
                    rover.move()
                elif c in ['L', 'R']:
                    rover.turn(c)
                logging.info(f'Rover {index} executed instructions: {c}')
                    

def parse(input):
    lines = filter(lambda l: l.strip(), input.splitlines())
    max_x, max_y = next(lines).split()
    plateau = Plateau(int(max_x), int(max_y))
    world = World(plateau)
    while lines:
        try:
            x, y, heading = next(lines).split()
            instructions = next(lines)
            position=Position(int(x), int(y), heading)
            world.add_rover(Rover(position, plateau))
            world.add_instructions(instructions)
            logging.info(f'Added rover at {position}')
        except StopIteration:
            break
    return world


def main(input):
    world = parse(input)
    world.follow_instructions()
    output = "\n".join([rover.report_position() for rover in world.rovers])
    return output


if __name__ == "__main__":
    input = sys.stdin.read()
    output = main(input)
    print(output)