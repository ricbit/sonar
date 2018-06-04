from abc import ABC, abstractmethod
import random


class Pos(object):
    def __init__(self, y, x):
        self.x = x
        self.y = y

    def add(self, pos):
        return Pos(self.y + pos.y, self.x + pos.x)

    def __str__(self):
        return "(%d, %d)" % (self.y, self.x)

    def __hash__(self):
        return hash((self.y, self.x))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Scenario(object):
    def __init__(self, filename):
        self.map = []
        f = open(filename, "rt")
        self.rows, self.cols = map(int, f.readline().split())
        for _ in range(self.rows):
            line = f.readline()
            while not line.strip():
                line = f.readline()
            self.map.append("".join(c for c in line if c in ".X"))
            print(self.map[-1])

    def create_submarine(self, pos):
        return Submarine(self, pos)

    def bounded(self, coord, limit):
        return 0 <= coord < limit

    def inside_bounds(self, pos):
        return (self.bounded(pos.x, self.cols)
                and self.bounded(pos.y, self.rows))

    def island(self, pos):
        return self.map[pos.y][pos.x] == 'X'

    def valid(self, pos):
        return self.inside_bounds(pos) and not self.island(pos)


class InvalidAction(Exception):
    pass


class Action(ABC):
    def __init__(self, submarine):
        self.submarine = submarine

    @abstractmethod
    def action(self):
        pass

    @abstractmethod
    def valid(self):
        return False


class MoveAction(Action):
    def __init__(self, submarine, delta, name):
        super().__init__(submarine)
        self.delta = delta
        self.name = name
        self.newpos = self.submarine.pos.add(self.delta)

    def valid(self):
        return (self.submarine.scenario.valid(self.newpos)
                and self.newpos not in self.submarine.visited)

    def action(self):
        self.submarine.pos = self.newpos
        self.submarine.visited.add(self.newpos)


class Submarine(object):
    POSSIBLE_DIRECTIONS = [
        (Pos(-1, 0), "North"),
        (Pos(1, 0), "South"),
        (Pos(0, 1), "East"),
        (Pos(0, -1), "West")
    ]

    def __init__(self, scenario, start_pos):
        self.scenario = scenario
        self.visited = set()
        self.mines = set()
        self.pos = start_pos
        if not self.scenario.valid(self.pos):
            raise InvalidAction()

    def available_actions(self):
        actions = (MoveAction(self, action[0], action[1])
                   for action in Submarine.POSSIBLE_DIRECTIONS)
        return [action for action in actions if action.valid()]

    def map(self):
        output = []
        for y in range(self.scenario.rows):
            for x in range(self.scenario.cols):
                pos = Pos(y, x)
                if self.scenario.island(pos):
                    output.append("X")
                elif pos in self.visited:
                    output.append("*")
                else:
                    output.append(".")
            output.append("\n")
        return "".join(output)


scenario = Scenario("scenario.txt")
print(scenario.map)
sub = scenario.create_submarine(Pos(0, 0))
while sub.available_actions():
    action = random.choice(sub.available_actions())
    action.action()
    print(action.name, sub.pos)
    print(sub.map())
