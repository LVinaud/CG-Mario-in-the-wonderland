#version 120

attribute vec3 position;
attribute vec2 texture_coord;
attribute vec3 normal;          // Vetores normais do objeto

varying vec2 out_texture;
varying vec3 frag_normal;
varying vec3 frag_position;    // Posição do fragmento no espaço do mundo

// Matrizes para calcular a posição final
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main(){
    gl_Position = projection * view * model * vec4(position, 1.0);
    out_texture = texture_coord;

    // Calculando a posição do vértice no espaço do mundo para sabermos a distância até a luz
    frag_position = vec3(model * vec4(position, 1.0));

    // Transformando a normal usando a matriz do modelo corrigida para escala (matriz normal)
    // Se você não usar escalas não-uniformes, model normal funciona bem em 3x3
    frag_normal = mat3(model) * normal;
}
