# Sonar

## Descrição da Atividade

A atividade consistiu na montagem de um circuito que é um sonar.

Então, construímos um circuito que com um Servo Motor ele rotaciona entre 30° e 150° graus um sensor ultrassônico que retorna a distância até onde ricocheteou a onda, dessa forma é informado na tela do computador conectado ao arduino se algum objeto foi detectado em um raio de 40cm .

## Alunos

* Bruno Kioshi Otani - 16858174

* Luis Aires Coimbra - 15472565


## Tabela de Gastos

| Quantidade | Componente | Descrição | Valor Unitário |
|----------|----------|----------|----------|
| 1 | Arduino | UNO | R$ 108,00 |
| 1 | Protoboard | BB-01 400P | R$ 21,70 |
| 1 | Kit Jumper | Macho-Macho + Macho-Fêmea | R$ 14,00 |
| 1 | Sensor Ultrassônico | SR04-Open | R$ 7,00 |
| 1 | Servo Motor Tower Pro SG90 | 180 graus de rotação | R$ 19,99 |
| 1 | Garrafa PET de Sprite usada | 600mL | R$ 00,00 | 

Agradecimentos à José Fausto Vital Barbosa, Pablo Henrique Almeida Vieira, Pedro Paulo Carvalho Coutinho e Roberto Brostel Barroso pela doação dos componentes.

## Tabela de pinagem

| Pino no arduino | Componente | Pino do componente |
|----------|----------|----------|
| 11 | Sensor Ultrassônico | TRIG\_PIN |
| 12 | Sensor Ultrassônico | ECHO\_PIN |
| 5V | Sensor Ultrassônico | Vcc |
| GND | Sensor Ultrassônico | Gnd |
| 10 | Servo Motor | Linha de controle |
| ICSP 5V | Servo Motor | Vcc |
| GND | Servo Motor | Gnd |


Valor Total: R$ 170,69

## Projeto Físico
![](imagem.jpg)


## Vídeo Explicando o Circuito e Circuito funcionando
[Video do circuito funcionando e explicação](https://www.youtube.com/watch?v=-jvtnRwk8xg)


## Guia de como fazer o projeto funcionar
####  Envie o código `sonar.ino` ao arduino. 
#### Instale as dependências `pygame` e `pyserial`
```
pip install pyserial
pip install pygame
```
#### Execute o arquivo `sonar_display.py` 
```
python3 sonar_display.py
```
Observação: o display foi programado para linux ubuntu
