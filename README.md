# CG-Mario-in-the-wonderland

"Mario goes to an adventure in a mystic castle to save peach, but berely he knows that the princess is in another castle."

Este projeto da diciplina SCC0250 - Computação Gráfica visa produzir uma cena artísticas com o pipeline gráfico da biblioteca OpenGL, em Python, usando objetos 3D, transformações geométricas, texturas, movimento de câmera e, futuramente, iluminação. Quanto a temática, o grupo optou por representar uma cena do jogo Mario 64.

---

## Integrantes do gurpo

- Gabriel Antunes Afonso de Araujo - 14571077
- Lázaro Pereira Vinaud Neto - 14675396

## Requisitos da cena

- Todos os objetos devem ser em 3d com texturas.
- Deve haver dois ambientes: Um interno e outro externo (o externo será feito com a técnica SkyBox).
- A câmera deve explorá-los livremente, mas nunca sair das bordas prédefinidas do cenário.
- Deve haver no mínimo 3 objetos no ambiente interno e 3 no externo.
- Objetos diferentes devem executar transformação geométricas diferentes.

## Requisitos da illuminação

- Um objeto transladável do ambiente externo deve ser iluminado.
- Dois objetos no ambiente interno devem ser fonte de luz.
- As fontes de luz de um ambiente interno devem afetar apenas os objetos desse ambiente interno.
- As fontes de luz devem poder ser desligadas ou ligadas independentemente.
- Deve haver eventos de teclado para incrementar ou decrementar a luz ambiente.
- Deve haver eventos de teclado para incrementar ou decrementar a reflexão difusa.
- Deve haver eventos de teclado para incrementar ou decrementar a reflexão especular.

  Obs: Para mostrar isso, os eventos da entrega 2 (em 'requisitos da cena') não precisam estar ativos.

## Composição da Cena

- **Ambiente interno:** Um cômodo do castelo da princesa `Peach` com um quadro mágico que leva para o ambiente externo.
- **Ambiente externo:** Uma fase do Mário personalizada e infestada pelos seus inimigos!
- **Fluxo da apresentação:** Câmera começa no ambiente interno, o qual ela explora livremente até decidir atravessar o quadro. Nisso, o ambiente ineterno deixa de ser renderizado e ela explora o novo ambiente (limitado pela colisão com o SkyBox).

| Nome | Localização | Transformação a ser aplicada | É fonte de iluminação | Objeto já criado? |
|----|----|----|----|----|
| Quadro | Interno | Nenhuma | a definir... | sim |
| Tocha | interno | Nenhuma | a definir... | sim |
| Toad | Interno | Translação | a definir... | sim |
| Mario | Externo | Translação | a definir... | sim |
| Estrela | Externo | Rotação | a definir... | sim |
| Boo | Externo | Translação | a definir... | sim |
| Arvores | Externo | Nenhuma | a definir... | sim |
| Cano do mario | Externo | Escala | a definir... | sim |
| Chão externo | Externo | Nenhuma | a definir | sim |
| Quarto do castelo | Interno | Nenhuma | a definir... | sim |
| Moedas | Externas e internas | Rotação | a definir... | sim |
| Plataforma | Externas | Nenhuma | a definir... | sim |


## Arquitetura do código

Durante o desenvolvimento, optamos por priorizar abstrações que facilitassem a instanciação de diferentes objetos gráficos e alcançassem um nível de modularização que facilitasse a legibilidade do código. Dessa forma, utilizamos orientação a objetos para encapsular cada comportamento do código em classes bem definidas, sendo elas:

- **`main.py`** — ponto de entrada do código. Monta a cena, configura os shaders e callbacks do GLFW e roda o loop principal.
- **`gl_setup.py`** — inicializa a janela GLFW e o estado base do OpenGL (depth test, blending, etc.).
- **`shader.py`** — carrega e compila os shaders GLSL e expõe o programa pronto para uso.
- **`obj_parser.py`** — lê arquivos `.obj` (vértices, UVs, faces) e triangula faces de mais de 3 lados.
- **`mesh_registry.py`** — dono dos VBOs e das texturas. Acumula a geometria de todos os modelos em um único buffer e devolve um `MeshHandle` (offset + count) para cada um.
- **`graphic_object.py`** — `ObjetoGrafico`: Encapsula a lógica e estado de interação na memória principal de cada objeto desenhável. Guarda posição, rotação, escala e o `MeshHandle` do objeto.
- **`skybox.py`** — caixa grande estática que envolve o mundo, usando o mesmo shader dos demais objetos.
- **`scene.py`** — agrupa câmera, skybox e a lista de objetos; coordena a ordem de desenho.
- **`camera.py`** — câmera FPS com WASD + mouse, no mesmo padrão da Aula 13. Aplica colisão (no formato de campling) nos limites do mundo.
- **`transforms.py`** — funções puras que constroem as matrizes de model, view e projection (PyGLM).
- **`input_manager.py`** — registra callbacks por tecla com semântica de "while held", separando intenção de input do glue do GLFW.
- **`scene_editor.py`** — salva e carrega o `scene_layout.json` com posição, rotação e escala de cada objeto (e da câmera). Esse módulo foi desenvolvido para facilitar a adição e posicionamento dos objetos.

## Como rodar

Certifique-se de que o computador possui python3 instalado (de preferência na versão 3.14)

1. Entre em `src/` com `cd src/`
2. crie um ambiente virtual Python com `python3 -m venv .venv`
3. Ative o ambiente como `source .venv/bin/activate`
4. Instale as dependências com `pip install glfw PyOpenGL PyGLM Pillow numpy`
5. saia de `src` com `cd ../`
6. Rode todo o programa com: `python3 -m src.main`
