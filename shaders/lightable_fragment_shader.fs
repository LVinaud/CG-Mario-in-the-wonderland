#version 120

varying vec2 out_texture;
varying vec3 frag_normal;
varying vec3 frag_position;

uniform sampler2D imagem;
uniform vec3 view_pos; // Posição da câmera (X, Y, Z) no mundo

// Estrutura para simplificar o gerenciamento das luzes
struct Light {
    vec3 position;
    vec3 color;
    float is_on; // 1.0 se ligada, 0.0 se desligada
};

// Estrutura para configurar os niveis de refração e brilho do fragmento
struct Material {
    float k_diffuse;            // Refletir luz difusa (de 0.0 a 1.0)
    float k_specular;           // Refletir luz de brilho especular (0.0 a 1.0)
    float shininess;            // Concentração do brilho no framento 4.0 a 128.0)
};
uniform Material material;

#define NR_LIGHTS 4

uniform Light lights[NR_LIGHTS]; // 0 e 1: Internas, 2: Externa

// Constantes para controlar as intensidades da reflexão
uniform float global_diffuse_factor;
uniform float global_specular_factor;
uniform float global_ambient_factor;

void main(){
    vec4 tex_color = texture2D(imagem, out_texture);

    // Se o fragmento for totalmente transparente, descarta (bom para texturas com alpha)
    if(tex_color.a < 0.1) discard;

    vec3 normal = normalize(frag_normal);
    vec3 view_dir = normalize(view_pos - frag_position);

    // Configurando a luz ambiente
    vec3 ambient_light_color = vec3(0.15, 0.15, 0.15); // Luz de fundo fraca
    vec3 ambient = ambient_light_color * tex_color.rgb;

    vec3 total_diffuse = vec3(0.0);
    vec3 total_specular = vec3(0.0);

    // Loop pelas N fontes de luz definidas
    for(int i = 0; i < NR_LIGHTS; i++) {
        // Pular se a luz estiver desligada ou isolada pelo ambiente
        if (lights[i].is_on < 0.5) continue;

        // Vetor que aponta do fragmento para a luz
        vec3 light_dir = normalize(lights[i].position - frag_position);

        // Calculando a luz difusa final
        float diff = max(dot(normal, light_dir), 0.0);
        vec3 diffuse = diff * lights[i].color;
        total_diffuse += diffuse;

        // Calculando a luz especular final com o modelo de Phong
        // O número '32.0' é o brilho (shininess). Quanto maior, mais concentrado o brilho.
        vec3 reflect_dir = reflect(-light_dir, normal);
        float spec = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
        vec3 specular = spec * lights[i].color;
        total_specular += specular;
    }

    // Aplica os modificadores globais sobre as reflexões
    total_diffuse *= global_diffuse_factor * material.k_diffuse;
    total_specular *= global_specular_factor * material.k_specular;
    ambient *= global_ambient_factor;

    // Cor final: luz ambiente + difusa + especular sobre a cor de textura do fragmento
    vec3 final_color = ambient + (total_diffuse * tex_color.rgb) + total_specular;

    gl_FragColor = vec4(final_color, tex_color.a);
}
