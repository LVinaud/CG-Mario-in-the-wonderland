# CG-Mario-in-the-wonderland

"Mario goes to an adventure in a mystic castle to save peach".

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

## Composição da Cena

- **Ambiente interno:** Um cômodo do castelo da princesa `Peach` com um quadro mágico que leva para o ambiente externo.
- **Ambiente externo:** Uma fase do Mário personalizada e infestada pelos seus inimigos!
- **Fluxo da apresentação:** Câmera começa no ambiente interno, o qual ela explora livremente até decidir atravessar o quadro. Nisso, o ambiente ineterno deixa de ser renderizado e ela explora o novo ambiente (limitado pela colisão com o SkyBox). Caso ela encoste na estrela, a apresentação reinicia e ela volta para o ambiente interno. 

| Nome | Localização | Transformação a ser aplicada | É fonte de iluminação | Objeto já criado? |
|----|----|----|----|----|
| Quadro | Interno | Nenhuma | a definir... | sim |
| Tocha | interno | Nenhuma | a definir... | sim |
| Toad | Interno | Translação | a definir... | sim |
| Mario | Externo | Translação | a definir... | sim |
| Estrela | Externo | Rotação | a definir... | sim |
| Boo | Externo | Escala | a definir... | sim |
| Arvores | Externo | Nenhuma | a definir... | sim |
| Cano do mario | Externo | Nenhuma | a definir... | sim |
| Chão externo | Externo | Nenhuma | a definir | sim |
| Quarto do castelo | Interno | Nenhuma | a definir... | sim |


## Arquitetura do código

Durante o desenvolvimento, optamos por priorizar abstrações que facilitassem a instanciação de diferentes objetos gráficos e alcançassem um nível de modularização que facilitasse a legibilidade do código. Dessa forma, utilizamos orientação a objetos para encapsular cada comportamento do código em classes bem definidas, sendo elas:

<!-- Falta anotar uma breve descrição de cada modulo... -->

## Como rodar

Certifique-se de que o computador possui python3 instalado (de preferência na versão 3.14)

1. Entre em `src/` com `cd src/`
2. crie um ambiente virtual Python com `python3 -m venv .venv`
3. Ative o ambiente como `source .venv/bin/activate`
4. Instale as dependências com `pip install glfw PyOpenGL PyGLM Pillow numpy`
5. saia de `src` com `cd ../`
6. Rode todo o programa com: `python3 -m src.main`
