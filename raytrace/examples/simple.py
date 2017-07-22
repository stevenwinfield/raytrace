from raytrace.scene import Scene
from raytrace.camera import Perspective
from raytrace.colour import WHITE, RED
from raytrace.vector import Vector
from raytrace.primitive import Sphere, Plane
from raytrace.renderer import Renderer
from raytrace.material import Material
from raytrace.light import Point

def render():
    scene = Scene()

    eye = Vector(0.0, 0.0, 1.0)
    up = Vector(0.0, 0.0, 1.0)
    forward = Vector(0.0, 1.0, 0.0)
    camera = Perspective(eye, up, forward, 3.2, 1.8, 1.0)

    floor = Plane(Vector(0.0, 0.0, 0.0), up, Material(WHITE * 0.3, WHITE * 0.3, 0.3))
    ball = Sphere(Vector(0.0, 3.0, 1.0), 1.0, Material(RED, RED, 0.5, WHITE, 30))

    light = Point(Vector(-3.0, 0.0, 10.0), WHITE, 50.0)

    scene.objects.add(floor)
    scene.objects.add(ball)
    scene.lights.add(light)

    renderer = Renderer(recursion_depth=2)

    result = renderer.render(scene, camera, 320, 180)
    result.view()

if __name__ == "__main__":
    render()