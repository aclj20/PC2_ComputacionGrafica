#version 330 core

in vec3 position;
in vec3 vertex_color;
in vec3 vertex_normal;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;
uniform vec3 light_position;

out vec3 frag_color;
out vec3 frag_normal;
out vec3 frag_pos;
out vec3 light_pos;

void main()
{
    light_pos = light_position; 
    gl_Position = projection_mat * inverse(view_mat) * model_mat * vec4(position, 1.0);
    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    frag_pos = vec3(model_mat * vec4(position, 1.0));
    frag_color = vertex_color;
}