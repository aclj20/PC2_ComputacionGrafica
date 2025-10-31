#version 330 core

in vec3 frag_pos;
in vec3 frag_normal;
in vec2 tex_coords;

out vec4 frag_color;

uniform sampler2D water_wave_map; 
uniform float time;
uniform vec3 light_pos;
uniform vec3 view_pos;
uniform vec3 light_color;
uniform vec3 deep_water_color = vec3(0.0, 0.3, 0.5);
uniform vec3 shallow_water_color = vec3(0.5, 0.8, 0.9);
uniform float wave_speed = 0.3;
uniform float wave_strength = 0.08;
uniform float transparency = 0.9;
uniform float refraction_strength = 0.1;

void main() {
    vec2 uv1 = tex_coords * 2.0 + vec2(time * wave_speed * 0.5, 0.0);
    vec2 uv2 = tex_coords * 1.5 + vec2(0.0, time * wave_speed * 0.7);
    
    vec3 normal1 = texture(water_wave_map, uv1).rgb * 2.0 - 1.0;
    vec3 normal2 = texture(water_wave_map, uv2).rgb * 2.0 - 1.0;
    vec3 wave_vector = normalize(normal1 + normal2) * wave_strength;
    
    vec3 N = normalize(frag_normal + wave_vector);
    vec3 V = normalize(view_pos - frag_pos);
    vec3 L = normalize(light_pos - frag_pos);
    vec3 H = normalize(L + V);
    
    float depth_factor = smoothstep(0.0, 1.0, dot(N, vec3(0, 1, 0))); 
    vec3 water_color = mix(shallow_water_color, deep_water_color, 1.0 - depth_factor);
    
    float fresnel_factor = pow(1.0 - max(0.0, dot(N, V)), 5.0); 
    
    vec3 ambient = 0.3 * water_color;
    float diff = max(dot(N, L), 0.0);
    vec3 diffuse = diff * light_color * water_color;
    
    float spec = pow(max(dot(N, H), 0.0), 256.0) * 1.5;
    vec3 specular = spec * light_color;
    vec3 reflection_color_adjusted = water_color * 1.5; 
    vec3 lit_color = ambient + diffuse + specular;
    vec3 final_color_rgb = mix(water_color * lit_color, reflection_color_adjusted, fresnel_factor * 0.8);
    float alpha = transparency * (0.3 + fresnel_factor * 0.7); 
    alpha = clamp(alpha, 0.0, 1.0); 
    final_color_rgb = pow(final_color_rgb, vec3(1.0/2.2)); 
    
    frag_color = vec4(final_color_rgb, alpha);
}