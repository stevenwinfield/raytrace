"""
material.

Defines how objects interact with rays.
"""

from .colour import WHITE

class Material:
    """A Material defines how an object interacts with light."""

    def __init__(self, ambient, diffuse=None, reflectivity=0.0, specular=None,
                 shinyness=10):
        """Initialise a material."""
        self.ambient = ambient
        self.diffuse = diffuse or ambient
        self.reflectivity = reflectivity
        self.specular = specular or WHITE
        self.shinyness = shinyness
