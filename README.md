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
- **Ambiente externo:** A praça da convergência (vulgo, praça das bandeiras) do ICMC, infestada pelos inimigos do Mario!
- **Fluxo da apresentação:** Câmera começa no ambiente interno, o qual ela explora livremente até decidir atravessar o quadro. Nisso, o ambiente ineterno deixa de ser renderizado e ela explora o novo ambiente (limitado pela colisão com o SkyBox). Caso ela encoste na estrela, a apresentação reinicia e ela volta para o ambiente interno. 

| Nome | Localização | Transformação a ser aplicada | É fonte de iluminação |
|----|----|----|----|
| Quadro | Interno | Nenhuma | a definir... |
| Tocha | interno | Nenhuma | a definir... |
| Toad | Interno | Translação | a definir... |
| Mario | Externo | Translação | a definir... |
| Estrela | Externo | Rotação | a definir... | 
| Bob-omb | Externo | Escala | a definir... |
| Arvores | Externo | Nenhuma | a definir... |
| Bandeiras do ICMC | Externo | Nenhuma | a definir... |


## Arquitetura do código

## Como rodar
