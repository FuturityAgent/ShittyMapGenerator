from utils import COLORS

class ResourceType:
	def __init__(self, name, color):
		self.name = name
		self.color = color

class Resource:
	def __init__(self, type, tile, owner=None):
		self.type = type
		self.tile = tile
		self.owner = owner

RESOURCE_TYPE = {
	'iron': ResourceType('iron', COLORS.get('darkgrey')),
	'gold': ResourceType('gold', COLORS.get('gold')),
	'stone': ResourceType('stone', COLORS.get('grey')),
	'livestock': ResourceType('livestock', COLORS.get('green'))
}