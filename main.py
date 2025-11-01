from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.Cube import *
from glApp.Triangle import *
from glApp.Axes import *
from glApp.LoadMesh import *
import numpy as np

import pygame
from pygame.locals import *
from OpenGL.GL import *

pygame.init()
pygame.display.set_mode((1000, 800), DOUBLEBUF | OPENGL)

vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertex_color;
in vec3 vertex_normal;
in vec2 texcoord;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;
uniform vec3 light_position;

out vec3 frag_color;
out vec3 frag_normal;
out vec3 frag_pos;
out vec2 frag_uv;
out vec3 light_pos;

void main()
{
    light_pos = light_position;
    gl_Position = projection_mat * inverse(view_mat) * model_mat * vec4(position, 1.0);
    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    frag_pos = vec3(model_mat * vec4(position, 1.0));
    frag_uv = texcoord;
    frag_color = vertex_color;
}
'''

fragment_shader = r'''
#version 330 core

in vec3 frag_color;
in vec3 frag_normal;
in vec3 frag_pos;
in vec2 frag_uv;
in vec3 light_pos;

out vec4 final_color;

uniform vec3 view_pos;
uniform float metalness;
uniform float roughness;
uniform float fresnel_strength;
uniform sampler2D base_texture;
uniform int use_texture;

void main()
{
    vec3 light_color = vec3(1.0);
    float ambient_strength = 0.2;
    float specular_strength = mix(1.0 - roughness, 1.0, metalness);
    int shininess = int(mix(8.0, 64.0, 1.0 - roughness));

    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);
    vec3 view_dir = normalize(view_pos - frag_pos);
    vec3 halfway_dir = normalize(light_dir + view_dir);

    vec3 ambient = ambient_strength * frag_color;
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * frag_color * (1.0 - metalness);
    float spec = pow(max(dot(norm, halfway_dir), 0.0), shininess);
    vec3 specular_color = mix(vec3(1.0), frag_color, metalness);
    vec3 specular = specular_strength * spec * specular_color;
    float fresnel = pow(1.0 - max(dot(view_dir, norm), 0.0), 3.0) * fresnel_strength;
    vec3 result = ambient + diffuse + specular + fresnel * light_color;

    if (use_texture == 1) {
        vec3 tex_col = texture(base_texture, frag_uv).rgb;
        result *= tex_col;
    }

    final_color = vec4(result, 1.0);
}
'''

class MaterialDemo(PyOGApp):
    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.axes = None
        self.sphere1 = None
        self.sphere2 = None
        self.sphere3 = None

    def initialise(self):
        self.program_id = create_program(vertex_shader, fragment_shader)

        self.sphere1 = LoadMesh("models/sphere.obj", self.program_id,
                              location=pygame.Vector3(-0.5, 0, 0),
                              scale=pygame.Vector3(0.1, 0.1, 0.1),
                              move_rotation=Rotation(1, pygame.Vector3(0, 0, 1)))

        self.sphere2 = LoadMesh("models/sphere.obj", self.program_id,
                              location=pygame.Vector3(0, 0, 0),
                              scale=pygame.Vector3(0.1, 0.1, 0.1),
                              move_rotation=Rotation(1, pygame.Vector3(0, 0, 1)))

        self.sphere3 = LoadMesh("models/sphere.obj", self.program_id,
                              location=pygame.Vector3(0.5, 0, 0),
                              scale=pygame.Vector3(0.1, 0.1, 0.1),
                              move_rotation=Rotation(1, pygame.Vector3(0, 0, 1)))

        def load_texture(path):
            try:
                surf = pygame.image.load(path)
                image = pygame.transform.flip(surf, False, True)
                image_data = pygame.image.tostring(image, "RGB", True)
                width, height = image.get_size()
            except Exception:
                width, height = 1, 1
                image_data = bytes([255, 255, 255])
            tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                        0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
            return tex_id

        self.sphere1.texture_id = load_texture("textures/metal.png")
        self.sphere2.texture_id = load_texture("textures/water.png")
        self.sphere3.texture_id = load_texture("textures/opaque.png")

        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        self.camera.position = pygame.Vector3(0, 0, 5)
        self.camera.up = pygame.Vector3(0, 1, 0)
        self.camera.forward = pygame.Vector3(0, 0, -1)
        glEnable(GL_DEPTH_TEST)

    def camera_init(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)

        light_pos = (3.0, 3.0, 3.0)
        light_pos_loc = glGetUniformLocation(self.program_id, "light_position")
        if light_pos_loc != -1:
            glUniform3f(light_pos_loc, *light_pos)

        if hasattr(self.camera, 'position'):
            view_pos_loc = glGetUniformLocation(self.program_id, "view_pos")
            if view_pos_loc != -1:
                glUniform3f(view_pos_loc,
                          self.camera.position.x,
                          self.camera.position.y,
                          self.camera.position.z)

        self.camera.update()

        spheres = [self.sphere1, self.sphere2, self.sphere3]
        material_props = [
            {"metalness": 1.0, "roughness": 0.2, "fresnel_strength": 0.1,
             "use_texture": 1, "base_tint": (1.0, 0.9, 0.7)},
            {"metalness": 0.1, "roughness": 0.05, "fresnel_strength": 1.0,
             "use_texture": 1, "base_tint": (0.2, 0.5, 1.0)},
            {"metalness": 0.0, "roughness": 0.9, "fresnel_strength": 0.0,
             "use_texture": 1, "base_tint": (0.8, 0.8, 0.8)},
        ]

        for i, sphere in enumerate(spheres):
            props = material_props[i]

            for uniform_name, value in props.items():
                loc = glGetUniformLocation(self.program_id, uniform_name)
                if loc == -1:
                    continue
                if isinstance(value, (tuple, list)) and len(value) == 3:
                    glUniform3f(loc, float(value[0]), float(value[1]), float(value[2]))
                elif isinstance(value, int):
                    glUniform1i(loc, value)
                else:
                    glUniform1f(loc, float(value))

            tex_id = getattr(sphere, 'texture_id', None)
            if tex_id is not None:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, tex_id)
                tex_loc = glGetUniformLocation(self.program_id, "base_texture")
                if tex_loc != -1:
                    glUniform1i(tex_loc, 0)

            sphere.draw()

            if tex_id is not None:
                glBindTexture(GL_TEXTURE_2D, 0)

if __name__ == "__main__":
    MaterialDemo().mainloop()