#version 120

varying vec2 out_texture;
uniform sampler2D imagem;

void main(){
    gl_FragColor = texture2D(imagem, out_texture);
}
