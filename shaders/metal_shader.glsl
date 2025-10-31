#version 330 core

in vec3 frag_color;
in vec3 frag_normal;
in vec3 frag_pos;
in vec3 light_pos;

out vec4 final_color;

uniform vec3 view_pos;

uniform float metallic;    
uniform float roughness;  

const float PI = 3.14159265359;


vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}


float DistributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;
    
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
    
    return a2 / max(denom, 0.0001);
}


float GeometrySchlickGGX(float NdotV, float roughness) {
    float r = (roughness + 1.0);
    float k = (r * r) / 8.0;
    
    float denom = NdotV * (1.0 - k) + k;
    return NdotV / denom;
}

void main() {
    
    vec3 N = normalize(frag_normal);
    vec3 V = normalize(view_pos - frag_pos);
    vec3 L = normalize(light_pos - frag_pos);
    vec3 H = normalize(V + L);
    
    
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float NdotH = max(dot(N, H), 0.0);
    float HdotV = max(dot(H, V), 0.0001);
    

    vec3 F0 = mix(vec3(0.04), frag_color, metallic);
    
    vec3 F = fresnelSchlick(HdotV, F0);
    
    float NDF = DistributionGGX(N, H, roughness);
    

    float G = GeometrySchlickGGX(NdotV, roughness) * 
              GeometrySchlickGGX(NdotL, roughness);
    
    vec3 numerator = NDF * G * F;
    float denominator = 4.0 * NdotV * NdotL;
    vec3 specular = numerator / max(denominator, 0.001);
    
    vec3 kD = vec3(1.0) - F;
    kD *= 1.0 - metallic;
    vec3 diffuse = kD * frag_color / PI;
    
    vec3 Lo = (diffuse + specular) * NdotL;
    
    vec3 ambient = vec3(0.03) * frag_color;
    
    vec3 color = ambient + Lo;
    
    
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0/2.2)); 
    
    final_color = vec4(color, 1.0);
}