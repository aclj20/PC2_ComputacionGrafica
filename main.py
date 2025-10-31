from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.Cube import *
from glApp.Triangle import *
from glApp.Axes import *
from glApp.LoadMesh import *
from PIL import Image
from OpenGL.GL import *
import numpy as np

def load_shader_file(filename):
    with open(f'shaders/{filename}', 'rb') as file:
        return file.read()

vertex_shader = load_shader_file('vertex_shader.glsl')
metal_shader = load_shader_file('metal_shader.glsl')
water_shader = load_shader_file('water_shader.glsl')
opaque_shader = load_shader_file('opaque_shader.glsl')

def load_texture(path):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    try:
        img = Image.open(path)
        img_data = img.tobytes("raw", "RGB", 0, -1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, 
                    GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    except:
        print(f"No se pudo cargar la textura: {path}")
    
    return texture

class MaterialDemo(PyOGApp):
    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.axes = None
        self.sphere1 = None
        self.sphere2 = None
        self.sphere3 = None
        self.water_program = None
        self.metal_program = None
        self.opaque_program = None
        self.water_texture = None

    def initialise(self):
        self.water_program = create_program(vertex_shader, water_shader)
        self.metal_program = create_program(vertex_shader, metal_shader)
        self.opaque_program = create_program(vertex_shader, opaque_shader)
        
        self.water_texture = load_texture("textures/water_normal.png")
        self.sphere1 = LoadMesh("models/sphere.obj", self.metal_program,
                              location=pygame.Vector3(-0.5, 0, 0),
                              scale=pygame.Vector3(0.1, 0.1, 0.1),
                              move_rotation=Rotation(1, pygame.Vector3(0, 0, 1)))
        
        self.sphere2 = LoadMesh("models/sphere.obj", self.water_program,
                              location=pygame.Vector3(0, 0, 0),
                              scale=pygame.Vector3(0.1, 0.1, 0.1),
                              move_rotation=Rotation(1, pygame.Vector3(0, 0, 1)))
        
        self.sphere3 = LoadMesh("models/sphere.obj", self.opaque_program,
                              location=pygame.Vector3(0.5, 0, 0),
                              scale=pygame.Vector3(0.1, 0.1, 0.1),
                              move_rotation=Rotation(1, pygame.Vector3(0, 0, 1)))
        
        self.camera = Camera(self.metal_program, self.screen_width, self.screen_height)
        self.camera.position = pygame.Vector3(0, 0, 5)
        self.camera.up = pygame.Vector3(0, 1, 0)
        self.camera.forward = pygame.Vector3(0, 0, -1)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_BLEND)

    def camera_init(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        light_pos = (3.0, 3.0, 3.0)
        
        material_props = [
            {"program": self.metal_program, "metalness": 1.0, "roughness": 0.3, "fresnel": 0.1},
            {"program": self.water_program, "metalness": 0.1, "roughness": 0.2, "fresnel": 0.8},
            {"program": self.metal_program, "metalness": 0.0, "roughness": 0.9, "fresnel": 0.0}
        ]

        for i, sphere in enumerate([self.sphere1, self.sphere2, self.sphere3]):
            if i == 0:  
                current_program = self.metal_program
                glUseProgram(current_program)

                metallic_loc = glGetUniformLocation(self.metal_program, "metallic")
                roughness_loc = glGetUniformLocation(self.metal_program, "roughness")

                glUniform1f(metallic_loc, 1.0)    
                glUniform1f(roughness_loc, 0.0)

            elif i == 1:
                current_program = self.water_program
                glUseProgram(current_program)
                
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.water_texture)
                glUniform1i(glGetUniformLocation(current_program, "water_wave_map"), 0)
                
                glUniform1f(glGetUniformLocation(current_program, "time"), 
                            pygame.time.get_ticks() / 1000.0)
                
                glUniform3f(glGetUniformLocation(current_program, "light_pos"), 
                            3.0, 3.0, 3.0)
                glUniform3f(glGetUniformLocation(current_program, "light_color"), 
                            1.0, 1.0, 1.0)
                glUniform3f(glGetUniformLocation(current_program, "view_pos"), 
                            self.camera.position.x, 
                            self.camera.position.y, 
                            self.camera.position.z)
                
                glUniform3f(glGetUniformLocation(current_program, "deep_water_color"),
                            0.0, 0.3, 0.5)
                glUniform3f(glGetUniformLocation(current_program, "shallow_water_color"), 
                            0.5, 0.8, 0.9)
                glUniform1f(glGetUniformLocation(current_program, "wave_speed"), 0.3)
                glUniform1f(glGetUniformLocation(current_program, "wave_strength"), 0.08)
                glUniform1f(glGetUniformLocation(current_program, "specular_power"), 128.0)
                glUniform1f(glGetUniformLocation(current_program, "specular_intensity"), 0.8)
                glUniform1f(glGetUniformLocation(current_program, "fresnel_power"), 2.0)
                glUniform1f(glGetUniformLocation(current_program, "fresnel_scale"), 0.8)
                glUniform1f(glGetUniformLocation(current_program, "fresnel_bias"), 0.1)
                glUniform1f(glGetUniformLocation(current_program, "refraction_strength"), 0.1)
            
            elif i == 2:
                current_program = self.opaque_program
                glUseProgram(current_program)

                color_loc = glGetUniformLocation(current_program, "object_color")
                if color_loc != -1:
                    glUniform3f(color_loc, 0.5, 0.5, 0.5)
                
                roughness_loc = glGetUniformLocation(current_program, "roughness")
                if roughness_loc != -1:
                    glUniform1f(roughness_loc, 1.0)

            light_pos_loc = glGetUniformLocation(current_program, "light_position")
            glUniform3f(light_pos_loc, *light_pos)
            
            if hasattr(self.camera, 'position'):
                view_pos_loc = glGetUniformLocation(current_program, "view_pos")
                glUniform3f(view_pos_loc, 
                        self.camera.position.x, 
                        self.camera.position.y, 
                        self.camera.position.z)
            
            self.camera.update()
            
            props = material_props[i]
                
            for uniform_name, value in props.items():
                loc = glGetUniformLocation(current_program, uniform_name)
                if loc != -1:
                    glUniform1f(loc, value)
                    
            sphere.draw()

if __name__ == "__main__":
    MaterialDemo().mainloop()