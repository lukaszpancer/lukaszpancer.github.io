from typing import Deque, List, Set
from dataclasses import dataclass
from math import sqrt
import pygame
from enum import Enum, unique
import sys
import random
from queue import PriorityQueue, Empty
import asyncio
import time

INIT_LENGTH = 4

WIDTH = 480
HEIGHT = 480
GRID_SIDE = 24
GRID_WIDTH = WIDTH // GRID_SIDE
GRID_HEIGHT = HEIGHT // GRID_SIDE

BRIGHT_BG = (103, 223, 235)
DARK_BG = (78, 165, 173)

SNAKE_COL = (6, 38, 7)
FOOD_COL = (224, 160, 38)
OBSTACLE_COL = (209, 59, 59)
VISITED_COL = (24, 42, 142)
RESTART = False
FPS = 30


@unique
class Direction(tuple, Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def reverse(self):
        x, y = self.value
        return Direction((x * -1, y * -1))

    def __str__(self):
        return str(self.value)


@dataclass
class Position:
    x: int
    y: int

    def check_bounds(self, width: int, height: int):
        return (self.x >= width) or (self.x < 0) or (self.y >= height) or (self.y < 0)

    def draw_node(self, surface: pygame.Surface, color: tuple, background: tuple):
        r = pygame.Rect(
            (int(self.x * GRID_SIDE), int(self.y * GRID_SIDE)), (GRID_SIDE, GRID_SIDE)
        )
        pygame.draw.rect(surface, color, r)
        pygame.draw.rect(surface, background, r, 1)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Position):
            return (self.x == o.x) and (self.y == o.y)
        else:
            return False

    def __str__(self):
        return f"X{self.x};Y{self.y};"

    def __hash__(self):
        return hash(str(self))

    def __add__(self, dir: Direction):
        x, y = dir.value
        return Position(self.x + x, self.y + y)

    def __sub__(self, dir: object):
        if isinstance(dir, Position):
            return self.x - dir.x, self.y - dir.y
        else:
            raise ValueError


class GameNode:
    nodes: Set[Position] = set()

    def __init__(self):
        self.position = Position(0, 0)
        self.color = (0, 0, 0)

    def randomize_position(self):
        try:
            GameNode.nodes.remove(self.position)
        except KeyError:
            pass

        condidate_position = Position(
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
        )

        if condidate_position not in GameNode.nodes:
            self.position = condidate_position
            GameNode.nodes.add(self.position)
        else:
            self.randomize_position()

    def draw(self, surface: pygame.Surface):
        self.position.draw_node(surface, self.color, BRIGHT_BG)


class Food(GameNode):
    def __init__(self):
        super(Food, self).__init__()
        self.color = FOOD_COL
        self.randomize_position()


class Obstacle(GameNode):
    def __init__(self):
        super(Obstacle, self).__init__()
        self.color = OBSTACLE_COL
        self.randomize_position()


class Snake:
    def __init__(self, screen_width, screen_height, init_length):
        self.color = SNAKE_COL
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.init_length = init_length
        self.reset()

    def reset(self):
        self.length = self.init_length
        self.positions = [Position((GRID_SIDE // 2), (GRID_SIDE // 2))]
        self.direction = random.choice([e for e in Direction])
        self.score = 0
        self.hasReset = True

    def get_head_position(self) -> Position:
        return self.positions[0]

    def turn(self, direction: Direction):
        if self.length > 1 and direction.reverse() == self.direction:
            return
        else:
            self.direction = direction

    def move(self):
        self.hasReset = False
        cur = self.get_head_position()
        x, y = self.direction.value
        new = Position(
            cur.x + x,
            cur.y + y,
        )
        if self.collide(new):
            self.reset()
        else:
            self.positions.insert(0, new)
            while len(self.positions) > self.length:
                self.positions.pop()

    def collide(self, new: Position):
        return (new in self.positions) or (new.check_bounds(GRID_WIDTH, GRID_HEIGHT))

    def eat(self, food: Food):
        if self.get_head_position() == food.position:
            self.length += 1
            self.score += 1
            while food.position in self.positions:
                food.randomize_position()

    def hit_obstacle(self, obstacle: Obstacle):
        if self.get_head_position() == obstacle.position:
            self.length -= 1
            self.score -= 1
            if self.length == 0:
                self.reset()

    def draw(self, surface: pygame.Surface):
        for p in self.positions:
            p.draw_node(surface, self.color, BRIGHT_BG)


class Player:
    def __init__(self) -> None:
        self.visited_color = VISITED_COL
        self.visited: Set[Position] = set()
        self.chosen_path: List[Direction] = []

    def move(self, snake: Snake) -> bool:
        try:
            next_step = self.chosen_path.pop(0)
            snake.turn(next_step)
            return False
        except IndexError:
            return True

    def search_path(self, snake: Snake, food: Food, *obstacles: Set[Obstacle]):
        """
        Do nothing, control is defined in derived classes
        """
        pass

    def turn(self, direction: Direction):
        """
        Do nothing, control is defined in derived classes
        """
        pass

    def draw_visited(self, surface: pygame.Surface):
        for p in self.visited:
            p.draw_node(surface, self.visited_color, BRIGHT_BG)


class SnakeGame:
    def __init__(self, snake: Snake, player: Player) -> None:
        pygame.init()
        pygame.display.set_caption("AIFundamentals - SnakeGame")

        self.snake = snake
        self.food = Food()
        self.obstacles: Set[Obstacle] = set()
        for _ in range(40):
            ob = Obstacle()
            while any([ob.position == o.position for o in self.obstacles]):
                ob.randomize_position()
            self.obstacles.add(ob)

        self.player = player

        self.fps_clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(
            (snake.screen_height, snake.screen_width), 0, 32
        )
        self.surface = pygame.Surface(self.screen.get_size()).convert()
        self.myfont = pygame.font.SysFont("monospace", 16)

    def drawGrid(self):
        for y in range(0, int(GRID_HEIGHT)):
            for x in range(0, int(GRID_WIDTH)):
                p = Position(x, y)
                if (x + y) % 2 == 0:
                    p.draw_node(self.surface, BRIGHT_BG, BRIGHT_BG)
                else:
                    p.draw_node(self.surface, DARK_BG, DARK_BG)

    def drawPath(self, head_pos: Position, path: List[Direction]):
        pos = head_pos
        if path:
            for i, turn in enumerate(path):
                brightness = 55 + i * (200 / len(path))
                pos += turn
                pos.draw_node(self.surface, (0, brightness, 0), (0, brightness, 0))

    def drawSnakeHead(self, head_pos: Position):
        head_pos.draw_node(self.surface, (0, 0, 255), (0, 0, 255))

    async def run(self):
        path = []
        while not self.handle_events():
            self.fps_clock.tick(FPS)
            self.drawGrid()
            if self.player.move(self.snake) or self.snake.hasReset:
                path = self.player.search_path(self.snake, self.food, self.obstacles)
                self.player.move(self.snake)
            self.snake.move()
            self.snake.eat(self.food)
            for ob in self.obstacles:
                self.snake.hit_obstacle(ob)
            for ob in self.obstacles:
                ob.draw(self.surface)
            self.player.draw_visited(self.surface)
            self.drawPath(self.snake.get_head_position(), path)
            self.snake.draw(self.surface)
            self.drawSnakeHead(self.snake.get_head_position())
            self.food.draw(self.surface)
            self.screen.blit(self.surface, (0, 0))
            text = self.myfont.render(
                "Score {0}".format(self.snake.score), 1, (0, 0, 0)
            )
            self.screen.blit(text, (5, 10))
            pygame.display.update()
            await asyncio.sleep(0)

    def handle_events(self):
        global RESTART
        if RESTART:
            RESTART = False
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_UP:
                    self.player.turn(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.player.turn(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.player.turn(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.player.turn(Direction.RIGHT)
        return False


class HumanPlayer(Player):
    def __init__(self):
        super(HumanPlayer, self).__init__()

    def turn(self, direction: Direction):
        self.chosen_path.append(direction)


def dfs(startpos: Position, endpos: Position, obstacles: Set[Position]):
    visited = set()

    def dfs_inner(path: List[Position], cur_pos: Position):
        if cur_pos == endpos:
            # path.append(cur_pos)
            return path

        if cur_pos.check_bounds(GRID_WIDTH, GRID_HEIGHT):
            return
        if cur_pos in obstacles:
            return

        if cur_pos not in visited:
            visited.add(cur_pos)
            for d in Direction:
                new_path = list(path)
                new_path.append(d)
                res = dfs_inner(new_path, cur_pos + d)
                if res:
                    return res
        return

    return dfs_inner([], startpos)


def bfs(start_pos: Position, end_pos: Position, obstacles: Set[Position]):
    queue: Deque[Position] = Deque()
    visited = set((start_pos,))
    queue.append(start_pos)
    parents = {start_pos: "END"}
    while queue:
        cur_pos = queue.popleft()

        for d in Direction:
            new_pos = cur_pos + d
            if new_pos not in visited:
                visited.add(new_pos)
                if new_pos not in obstacles and not new_pos.check_bounds(
                    GRID_WIDTH, GRID_HEIGHT
                ):
                    parents[new_pos] = cur_pos
                    queue.append(new_pos)
                    if new_pos == end_pos:
                        path = []
                        while parents[new_pos] != "END":
                            path.append(Direction(new_pos - parents[new_pos]))
                            new_pos = parents[new_pos]
                        return list(reversed(path))


def heuristic_search(
    start_pos: Position,
    end_pos: Position,
    obstacles: Set[Position],
    snake_positions: Set[Position],
):
    def heuristic(pos: Position):
        return abs(pos.x - end_pos.x) + abs(pos.y - end_pos.y)

    queue: PriorityQueue[Position] = PriorityQueue()
    visited = set((start_pos,))
    queue.put((heuristic(start_pos), 0, start_pos))
    parents = {start_pos: "END"}
    i = 1
    while True:
        try:
            cur_pos = queue.get(block=False)[2]
        except Empty:
            return

        for d in Direction:
            new_pos = cur_pos + d
            if new_pos not in visited:
                visited.add(new_pos)
                if new_pos not in snake_positions and not new_pos.check_bounds(
                    GRID_WIDTH, GRID_HEIGHT
                ):
                    parents[new_pos] = cur_pos
                    penalty = 50 if new_pos in obstacles else 0
                    queue.put((heuristic(new_pos) + penalty, i, new_pos))
                    i += 1
                    if new_pos == end_pos:
                        path = []
                        while parents[new_pos] != "END":
                            path.append(Direction(new_pos - parents[new_pos]))
                            new_pos = parents[new_pos]
                        return list(reversed(path))


def a_star(
    start_pos: Position,
    end_pos: Position,
    obstacles: Set[Position],
    snake_positions: Set[Position],
):
    def heuristic(pos: Position):
        return abs(pos.x - end_pos.x) + abs(pos.y - end_pos.y)

    queue: PriorityQueue[Position] = PriorityQueue()
    visited = set((start_pos,))
    queue.put((heuristic(start_pos), 0, start_pos))
    parents = {start_pos: "END"}
    g_scores = {
        Position(x, y): 100000.0 for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
    }
    g_scores[start_pos] = 0
    i = 1
    while True:
        try:
            cur_pos = queue.get(block=False)[2]
        except Empty:
            return

        if cur_pos == end_pos:
            path = []
            while parents[cur_pos] != "END":
                path.append(Direction(cur_pos - parents[cur_pos]))
                cur_pos = parents[cur_pos]
            return list(reversed(path))

        for d in Direction:
            new_pos = cur_pos + d
            if (
                not new_pos.check_bounds(GRID_WIDTH, GRID_HEIGHT)
                and g_scores[new_pos] > g_scores[cur_pos] + 1
            ):
                parents[new_pos] = cur_pos
                g_scores[new_pos] = g_scores[cur_pos] + 1
                if new_pos not in visited:
                    visited.add(new_pos)
                    if new_pos not in snake_positions:
                        penalty = 50 if new_pos in obstacles else 0

                        queue.put(
                            (
                                heuristic(new_pos) + g_scores[new_pos] + penalty,
                                i,
                                new_pos,
                            )
                        )
                        i += 1


class AStarPlayer(Player):
    def __init__(self):
        super(AStarPlayer, self).__init__()

    def search_path(self, snake: Snake, food: Food, obstacles: Set[Obstacle]):
        obstacles = set(s.position for s in obstacles)
        path = a_star(
            snake.get_head_position(),
            food.position,
            obstacles,
            set(snake.positions[1:]),
        )
        if path:
            self.chosen_path = path
        else:
            snake.reset()
        return self.chosen_path


class BFSPlayer(Player):
    def __init__(self):
        super(BFSPlayer, self).__init__()

    def search_path(self, snake: Snake, food: Food, obstacles: Set[Obstacle]):
        obstacles = set(s.position for s in obstacles)
        obstacles.update(snake.positions[1:])
        path = bfs(snake.get_head_position(), food.position, obstacles)
        if path:
            self.chosen_path = path
        else:
            snake.reset()
        return self.chosen_path


class DFSPlayer(Player):
    def __init__(self):
        super(DFSPlayer, self).__init__()

    def search_path(self, snake: Snake, food: Food, obstacles: Set[Obstacle]):
        obstacles = set(s.position for s in obstacles)
        obstacles.update(snake.positions[1:])
        path = dfs(snake.get_head_position(), food.position, obstacles)
        if path:
            self.chosen_path = path
        else:
            snake.reset()
        return self.chosen_path


async def main(player="human"):
    snake = Snake(WIDTH, WIDTH, INIT_LENGTH)
    match (player):
        case "human":
            player = HumanPlayer()
        case "A*":
            player = AStarPlayer()
        case "BFS":
            player = BFSPlayer()
        case "DFS":
            player = DFSPlayer()
    game = SnakeGame(snake, player)
    await game.run()


def change_player(name: str):
    global RESTART
    print("button has be clicked", name)
    time.sleep(0.1)
    RESTART = True
    asyncio.run(main(name))


def change_FPS(fps: int):
    global FPS
    FPS = int(fps)


if __name__ == "__main__":
    asyncio.run(main())
