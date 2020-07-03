import pygame
import random
import sys
import math
from tiles import Tile, COLORS, TILE_TYPES
from resource import Resource, ResourceType, RESOURCE_TYPE
WINDOW_SIZE = (1050, 700)
TILE_WIDTH, TILE_HEIGHT = 4, 4


def distance(a: tuple, b: tuple):
	return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

MAP_TYPE = {
	'islands': 0.60,
	'archipelagos': 0.55,
	'continents': 0.5,
	'pangea': 0.4,
}

LAND_BIOMS = ['desert', 'snow' ,'plain', 'forest']

class City:
	def __init__(self, name, x, y):
		self.name = name
		self.capital_x = x
		self.capital_y = y
		self.border_range = 3

class MainGame:
	def __init__(self, seed):
		pygame.init()
		self.width = WINDOW_SIZE[0]//TILE_WIDTH
		self.height = WINDOW_SIZE[1]//TILE_HEIGHT
		self.map_type = 'continents'
		if len(sys.argv) > 1:
			self.map_type = sys.argv[1]
		self._tiles = []
		self._cities = []
		self._resources = []
		self.clock = pygame.time.Clock()
		self.font = pygame.font.Font('freesansbold.ttf', 14)
		self.display = pygame.display.set_mode(WINDOW_SIZE)
		self.canvas = pygame.Surface(self.display.get_size(), pygame.SRCALPHA).convert()
		self.canvas.fill((0, 0, 0))
		pygame.display.set_caption("World Map")
		self.generate_map(seed)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
			self.draw_map()
			pygame.display.update()
			self.clock.tick(1)

	def place_seeds(self, seed: int):
		seeds = set()
		while len(seeds) < seed:
			new_x = random.randrange(2, self.width-2)
			new_y = random.randrange(2, self.height-2)
			seed_nearby = any([distance((new_x, new_y), point) < 5 for point in seeds])
			if not seed_nearby:
				seeds.add((new_x, new_y))

		return list(seeds)

	def generate_map(self, seed: int):
		sea_tile = TILE_TYPES.get('water')
		land_tile = TILE_TYPES.get('land')
		seeds = self.place_seeds(seed)
		for x in range(self.width):
			new_row = list()
			for y in range(self.height):
				new_tile = Tile(sea_tile, x, y) if (x, y) not in seeds else Tile(land_tile, x, y)
				new_row.append(new_tile)
			self._tiles.append(new_row)
		self.generate_continents()
		self.generate_bioms()
		self.clear_glitches()
		self.place_resources()
		self.place_states(6)

	def generate_continents(self):
		treshold = MAP_TYPE.get(self.map_type, 0.5)
		for row in self._tiles:
			for tile in row:
				if tile.type == TILE_TYPES.get('land'):
					rand = random.random()
					if rand > treshold:
						self.change_neighbours(tile.x, tile.y, r=1)

	def generate_bioms(self):
		import pdb
		for x, row in enumerate(self._tiles):
			weights = [0.1, 0.0, 0.3, 0.6]

			for y, cell in enumerate(row):
				if cell.type.name == 'land':
					# if (abs(self.height - y) < self.height / 8) or (abs(y) < self.height / 8):
					# 	weights = [0.02, 0.55, 0.05, 0.38]
					chunk = self.get_land_chunk(x, y)
					biom_choice = random.choices(LAND_BIOMS, weights=weights, k=1)[0]
					cell_type = TILE_TYPES.get(biom_choice)
					for line in chunk:
						line.type = cell_type

	def clear_glitches(self):
		for x, row in enumerate(self._tiles):
			for y, cell in enumerate(row):
				neighbours = list(set(self.get_neighbours(x, y, r=1)) - set([cell]))
				is_isolated = all([t.type != cell.type for t in neighbours])
				if is_isolated:
					cell.type = random.choice(neighbours).type

	def place_resources(self, n=20):
		# i = 0
		while n > 0:
			# new_resource_type = random.choice(RESOURCE_TYPE)
			x, y = random.randrange(2, self.width-2), random.randrange(2, self.height-2)
			if self._tiles[x][y].type.name in LAND_BIOMS:
				resource_nearby = any([distance((x, y), (r.tile.x, r.tile.y)) < 5 for r in self._resources])
				if resource_nearby:
					continue
				new_resource = Resource(random.choice(list(RESOURCE_TYPE.values())), tile=self._tiles[x][y])
				self._resources.append(new_resource)
				n -= 1


	def get_land_chunk(self, x, y):
		direction_id = random.randint(1, 8)
		neighbours = None
		r = random.randint(1, 6)

		if 1 <= direction_id <= 2 :
			neighbours = self.get_neighbours(x+1, y, r=r)
		elif 3 <= direction_id <= 4:
			neighbours = self.get_neighbours(x, y+1, r=r)
		elif 5 <= direction_id <= 6:
			neighbours = self.get_neighbours(x-1, y, r=r)
		else:
			neighbours = self.get_neighbours(x, y-1, r=r)

		land_tiles = [tile for tile in neighbours if tile.type.name == 'land']
		return land_tiles

	def get_neighbours(self, x, y, r=1):
		rows = self._tiles[abs(x - r): abs(x + (r+1))]
		neighbours = [cell for row in rows for cell in row[abs(y - r): abs(y + (r+1))]]
		return neighbours

	def change_neighbours(self, x, y, r=1):
		neighbours = self.get_neighbours(x, y, r)
		for tile in neighbours:
			tile.type = TILE_TYPES.get('land')

	def place_states(self, n):
		while n > 0:
			state_x, state_y = random.randrange(2, self.width-2), random.randrange(2, self.height-2)
			if self._tiles[state_x][state_y].type.name in LAND_BIOMS:
				city_nearby = any([distance((state_x, state_y), (c.capital_x, c.capital_y)) < 20 for c in self._cities])
				if city_nearby:
					continue
				# print(f"CITY NO {n}")
				new_city = City(f"City#{n}", state_x, state_y)
				self._cities.append(new_city)
				n -= 1

	def draw_map(self):
		self.display.blit(self.canvas, (0, 0))
		for x, row in enumerate(self._tiles):
			for y, cell in enumerate(row):
				# cell.surf.fill(cell.type.color)
				# self.canvas.blit(cell.surf, (cell.x * TILE_WIDTH, cell.y * TILE_HEIGHT))
				pygame.draw.rect(self.display, cell.type.color , (x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT ))
		import pdb
		for resource in self._resources:
			res_x, res_y = resource.tile.x, resource.tile.y
			color = resource.type.color
			pygame.draw.polygon(self.display, color, ((res_x*TILE_WIDTH - 3*TILE_WIDTH, res_y*TILE_HEIGHT),
												(res_x*TILE_WIDTH + 3*TILE_WIDTH, res_y*TILE_HEIGHT),
												(res_x*TILE_WIDTH, res_y*TILE_HEIGHT - 3*TILE_HEIGHT)))
			pygame.draw.polygon(self.display, COLORS.get('black'), ((res_x * TILE_WIDTH - (3 * TILE_WIDTH)-2, res_y * TILE_HEIGHT),
													  (res_x * TILE_WIDTH + (3 * TILE_WIDTH)+2, res_y * TILE_HEIGHT),
													  (res_x * TILE_WIDTH, res_y * TILE_HEIGHT - 3 * TILE_HEIGHT-2)), 2)

		for city in self._cities:
			print(city.name, city.capital_x, city.capital_y)
			# pdb.set_trace()
			city_color = COLORS.get('black')
			city_borders = [t for t in self.get_neighbours(city.capital_x, city.capital_y, r=city.border_range) if t.type.name != 'water']
			for tile in city_borders:
				# tile.surf.fill(city_color, None)
				# self.canvas.blit(tile.surf, (tile.x * TILE_WIDTH, tile.y * TILE_HEIGHT))
				pygame.draw.rect(self.display, city_color, (
				tile.x * TILE_WIDTH, tile.y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), 1)
			text = self.font.render(city.name, True, COLORS.get('white'), COLORS.get('black'))
			text_rect = text.get_rect()
			text_rect.center = ((city.capital_x * TILE_WIDTH), (city.capital_y * TILE_HEIGHT) + (5 * TILE_HEIGHT))
			if abs((self.width*TILE_WIDTH) - text_rect.center[0]) < text_rect.center[0]/4:
				text_rect.center = (((city.capital_x-2) * TILE_WIDTH), (city.capital_y * TILE_HEIGHT) + (5 * TILE_HEIGHT))
			if abs((self.height*TILE_HEIGHT) - text_rect.center[1]) < city.border_range*2:
				text_rect.center = ((city.capital_x * TILE_WIDTH), (city.capital_y * TILE_HEIGHT) - (2 * TILE_HEIGHT * city.border_range))
			self.display.blit(text, text_rect)

		pygame.display.flip()

if __name__ == '__main__':
	game = MainGame(64)
	game.run()