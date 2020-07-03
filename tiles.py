import pygame
from utils import COLORS

class TileType:
	def __init__(self, name: str, color: str, width=2, height=2, alpha=0):
		self.name = name
		self.color = COLORS.get(color)
		self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
		self.surf.set_colorkey(self.color)
		self.surf.set_alpha(alpha)

class Tile:
	def __init__(self, field_type: TileType, pos_x: int, pos_y: int, latitude=1):
		self.type = field_type
		self.x = pos_x
		self.y = pos_y
		self.latitude = latitude
		self.surf = field_type.surf

	def __str__(self):
		return f'Tile {self.type.name} ({self.x}, {self.y})'

	def __repr__(self):
		return f'Tile {self.type.name} ({self.x}, {self.y})'

TILE_TYPES = {
	'water': TileType('water', 'blue'),
	'land': TileType('land', 'green'),
	'plain': TileType('plain', 'green'),
	'desert': TileType('desert', 'yellow'),
	'forest': TileType('forest', 'darkgreen'),
	'mountains': TileType('mountains', 'grey'),
	'city': TileType('city', 'lightgrey', alpha=0),
	'snow': TileType('snow', 'white')
}
