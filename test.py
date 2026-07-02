# =========================================
# NIVEL 1 - ENTRADA DE LA MANSION
# Recibidor + Relojes + Retratos
# =========================================

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

tiene_llave = False
reloj_activado = False

# Agregamos el suelo. 'plane' es un plano, y le damos una escala grande (50x50)
suelo = Entity(
    model='plane', 
    scale=(50, 1, 50), 
    color=color.dark_gray, 
    texture='white_cube', 
    collider='box' # Muy importante para que el jugador no caiga al vacío
)
# paredes
Entity(model='cube', scale=(20,5,1), position=(0,2,10), color=color.brown, collider='box')
Entity(model='cube', scale=(20,5,1), position=(0,2,-10), color=color.brown, collider='box')
Entity(model='cube', scale=(1,5,20), position=(10,2,0), color=color.brown, collider='box')
Entity(model='cube', scale=(1,5,20), position=(-10,2,0), color=color.brown, collider='box')

# puerta
puerta = Entity(
    model='cube',
    scale=(2,4,1),
    position=(0,2,-9),
    color=color.azure,
    collider='box'
)

# llave
llave = Entity(
    model='cube',
    color=color.yellow,
    scale=0.5,
    position=(5,1,5)
)

# reloj
reloj = Entity(
    model='cube',
    color=color.red,
    scale=1,
    position=(-5,1,5)
)

jugador = FirstPersonController()
jugador.position = (0,1,0)

Sky()

texto = Text(text='Busca la llave', y=0.45, scale=2)

def update():

    global tiene_llave
    global reloj_activado

    distancia_llave = distance(jugador.position, llave.position)

    if distancia_llave < 2:
        texto.text = "Presiona E para agarrar llave"

        if held_keys['e']:
            llave.visible = False
            tiene_llave = True

    distancia_reloj = distance(jugador.position, reloj.position)

    if distancia_reloj < 2:
        texto.text = "Presiona R para activar reloj"

        if held_keys['r']:
            reloj.color = color.green
            reloj_activado = True

    distancia_puerta = distance(jugador.position, puerta.position)

    if distancia_puerta < 3:

        if tiene_llave and reloj_activado:
            puerta.visible = False
            texto.text = "Nivel completado"

        else:
            texto.text = "Falta resolver puzzle"

app.run()