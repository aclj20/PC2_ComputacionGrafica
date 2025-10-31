#version 330 core

in vec3 frag_pos;
in vec3 frag_normal;

out vec4 frag_color;

uniform vec3 light_pos;
uniform vec3 view_pos;
uniform vec3 object_color;  
uniform float roughness;    
void main() {

    vec3 base_color = object_color;
    float ambient_strength = 0.5;  

    vec3 ambient = ambient_strength * base_color;
    
    
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * base_color;
    
    vec3 result = (ambient + diffuse) * base_color;
    frag_color = vec4(result, 1.0);
}