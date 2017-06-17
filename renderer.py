"""
renderer.

Defines renderer classes.
"""

from .colour import Colour, BLACK
from .light import Ambient, Point
from .ray import Ray
from .result import RenderResult, ResultComponent
from .constants import INTERSECTION_TOLERANCE


class Renderer:
    """The renderer class."""

    def __init__(self, recursion_depth=2):
        """Initialise this Renderer."""
        self.recursion_depth = recursion_depth

    def render(self, scene, camera, width, height,
               xmin=0, xmax=None, ymin=0, ymax=None):
        """Render the scene, viewed with the given camera.

        Output is an image of size width x height.
        """
        r = ResultComponent.red
        g = ResultComponent.green
        b = ResultComponent.blue

        result = RenderResult(width, height, (r, g, b))

        total_rays = camera.ray_count(width, height, xmin, xmax, ymin, ymax)

        for i, (x, y, ray) in enumerate(camera.rays(width, height,
                                                    xmin, xmax, ymin, ymax)):
            if i % 10000 == 0:
                print("{:0.2%}".format(i / total_rays))
            try:
                colour = self._compute_colour(ray, scene)
            except Exception as exc:
                raise ValueError("Error while rendering pixel ({}, {})"
                                 .format(x, y)) from exc
            result[x, y, r] = colour.red
            result[x, y, g] = colour.green
            result[x, y, b] = colour.blue
            # TODO: depth, count, object id

        return result

    def _compute_colour(self, ray, scene, depth=0, source_object=None):
        """Recursively compute the colour where a ray intersects an object."""
        colour = Colour()
        obj, distance, normal = scene.intersection(ray, True, source_object)
        if distance is None:  # No intersections
            return colour

        intersection_point = ray.point(distance)

        for light in scene.lights:
            if isinstance(light, Ambient):
                colour += self._compute_ambient(obj, intersection_point,
                                                normal, light, scene)
            elif isinstance(light, Point):
                colour += self._compute_diffuse(obj, intersection_point,
                                                normal, light, scene)
                colour += self._compute_specular(obj, intersection_point,
                                                 normal, light, scene)

        # Compute the contribution from reflected light
        if obj.material.reflectivity == 0.0 or depth >= self.recursion_depth:
            return colour.clamped()

        reflected_ray = Ray(intersection_point,
                            ray.direction.reflected(normal))
        reflected_colour = self._compute_colour(reflected_ray, scene,
                                                depth=depth + 1,
                                                source_object=obj)
        reflected_colour *= obj.material.reflectivity
        colour += reflected_colour

        return colour.clamped()

    def _compute_ambient(_self, obj, _intersection_point, normal, light,
                         _scene):
        """Compute the ambient light contribution to an object's colour."""
        return (obj.material.ambient * light.colour).clamped()

    def _compute_diffuse(self, obj, intersection_point, normal, light,
                         scene):
        # Can the light see the object?
        ray = Ray(light.position, intersection_point - light.position)
        closest_obj, distance, _ = scene.intersection(ray,
                                                      compute_normal=False)
        if (closest_obj is not obj or
            # obscured by a different part of self
            ((intersection_point - light.position).norm() - distance)
            > INTERSECTION_TOLERANCE):
                return BLACK  # We are obscured
        else:
            intensity = light.intensity / (distance * distance)
            cos_angle = -ray.direction @ normal
            colour = (obj.material.diffuse * light.colour *
                      cos_angle * intensity).clamped()
            return colour

    def _compute_specular(self, obj, intersection_point, normal, light,
                          scene):
        # Can the light see the object?
        # TODO get the light to provide this. can then add polarisation, etc.
        ray = Ray(light.position, intersection_point - light.position)
        closest_obj, distance, _ = scene.intersection(ray,
                                                      compute_normal=False)
        if (closest_obj is not obj or
            # obscured by a different part of self
            ((intersection_point - light.position).norm()
              - distance) > INTERSECTION_TOLERANCE):
            # We are obscured
            return BLACK
        else:
            attenuation = light.intensity / (distance * distance)
            cos_angle = -ray.direction @ normal
            specular = (pow(cos_angle, obj.material.shinyness)
                        * obj.material.specular)
            return (specular * light.colour * attenuation).clamped()
