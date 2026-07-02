from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

window.title = "El Secreto de la Mansión Miller"
window.borderless = False
window.fullscreen = False
window.color = color.rgb(15,15,15)

Sky(color=color.rgb(25,25,35))
AmbientLight(color=color.rgba(120,120,120,0.5))
DirectionalLight(y=20, z=10, shadows=True)

#====================================
# VARIABLES DE JUEGO (LÓGICA)
#====================================
tiene_llave = False
reloj_activado = False

#====================================
# COLORES Y TEXTOS
#====================================
COLOR_PISO = color.rgb(70,45,25)
COLOR_PARED = color.rgb(115,105,95)
COLOR_TECHO = color.rgb(180,175,165)
COLOR_MOLDURA = color.rgb(80,55,35)

mensaje_ui = Text(text='', scale=2, y=0.45, origin=(0,0), color=color.white)

#====================================
# ESTRUCTURA (PISO, TECHO Y PAREDES)
#====================================
Entity(model='cube', scale=(40,1,40), position=(0,-0.5,0), color=COLOR_PISO, collider='box')
Entity(model='cube', scale=(40,1,40), position=(0,8.5,0), color=COLOR_TECHO)

Entity(model='cube', scale=(40,9,1), position=(0,4,20), color=COLOR_PARED, collider='box')
Entity(model='cube', scale=(40,9,1), position=(0,4,-20), color=COLOR_PARED, collider='box')
Entity(model='cube', scale=(1,9,40), position=(20,4,0), color=COLOR_PARED, collider='box')
Entity(model='cube', scale=(1,9,40), position=(-20,4,0), color=COLOR_PARED, collider='box')

# Molduras
Entity(model='cube', scale=(40,0.3,0.3), position=(0,0.15,19.8), color=COLOR_MOLDURA)
Entity(model='cube', scale=(40,0.3,0.3), position=(0,0.15,-19.8), color=COLOR_MOLDURA)
Entity(model='cube', scale=(0.3,0.3,40), position=(19.8,0.15,0), color=COLOR_MOLDURA)
Entity(model='cube', scale=(0.3,0.3,40), position=(-19.8,0.15,0), color=COLOR_MOLDURA)

# Columnas
for x in (-16,16):
    for z in (-16,16):
        Entity(model='cube', scale=(1.2,8,1.2), position=(x,4,z), color=color.rgb(210,205,195), collider='box')

#====================================
# ESCALERAS
#====================================
for i in range(10):
    Entity(model='cube', scale=(10,0.4,1.5), position=(0,0.2+i*0.4,12-i*1.2), color=color.rgb(95,65,40), collider='box')

Entity(model='cube', scale=(10,0.5,5), position=(0,4.2,1), color=color.rgb(95,65,40), collider='box')

for i in range(10):
    Entity(model='cube', scale=(10,0.4,1.5), position=(0,4.6+i*0.4,-1-i*1.2), color=color.rgb(95,65,40), collider='box')

for z in range(10):
    Entity(model='cube', scale=(0.2,1.2,0.2), position=(-5,1+z*0.4,12-z*1.2), color=color.rgb(70,45,25))
    Entity(model='cube', scale=(0.2,1.2,0.2), position=(5,1+z*0.4,12-z*1.2), color=color.rgb(70,45,25))

#====================================
# PUERTAS E INTERACTUABLES
#====================================
# La puerta de salida principal (AHORA INTERACTIVA)
puerta_salida = Entity(model='cube', scale=(4,6,0.5), position=(0,3,-19.5), color=color.rgb(65,35,20), collider='box')

# Marcos de la puerta principal
Entity(model='cube', scale=(5,0.5,0.5), position=(0,6.2,-19.4), color=color.rgb(40,20,10))
Entity(model='cube', scale=(0.5,6,0.5), position=(-2.2,3,-19.4), color=color.rgb(40,20,10))
Entity(model='cube', scale=(0.5,6,0.5), position=(2.2,3,-19.4), color=color.rgb(40,20,10))

# Otras puertas
Entity(model='cube', scale=(3,5,0.5), position=(-19.4,2.5,-8), rotation=(0,90,0), color=color.rgb(70,40,20), collider='box')
Entity(model='cube', scale=(3,5,0.5), position=(19.4,2.5,-8), rotation=(0,90,0), color=color.rgb(70,40,20), collider='box')

# Reloj gigante del fondo (AHORA INTERACTIVO)
reloj_interactivo = Entity(model='cube', scale=(4,4,0.2), position=(0,4,19.3), color=color.rgb(140,110,60), collider='box')

#====================================
# DECORACIÓN Y MUEBLES
#====================================
# Ventanas
for x in (-12,12):
    Entity(model='cube', scale=(3,4,0.2), position=(x,4,19.4), color=color.rgb(160,210,255))
    Entity(model='cube', scale=(0.2,4,3), position=(-19.4,4,x), rotation=(0,90,0), color=color.rgb(160,210,255))
    Entity(model='cube', scale=(0.2,4,3), position=(19.4,4,x), rotation=(0,90,0), color=color.rgb(160,210,255))

# Alfombra y Araña
Entity(model='cube', scale=(6,0.05,18), position=(0,-0.45,-2), color=color.rgb(120,20,20))
Entity(model='sphere', scale=1.5, position=(0,7,0), color=color.rgb(220,190,120))
for x in (-1.5, 1.5):
    for z in (-1.5, 1.5):
        Entity(model='sphere', scale=0.4, position=(x,6.5,z), color=color.rgb(255,240,180))

# Relojes laterales y Cuadros
for z in (-12,-6,0,6):
    Entity(model='cube', scale=(1.5,1.5,0.2), position=(-19.3,3,z), rotation=(0,90,0), color=color.rgb(140,110,60))
    Entity(model='cube', scale=(1.5,1.5,0.2), position=(19.3,3,z), rotation=(0,90,0), color=color.rgb(140,110,60))

for z in (-10,-2,6):
    Entity(model='cube', scale=(2,3,0.15), position=(-15,3,z), rotation=(0,90,0), color=color.rgb(70,70,70))
    Entity(model='cube', scale=(2,3,0.15), position=(15,3,z), rotation=(0,90,0), color=color.rgb(70,70,70))

# Plantas
for pos in [(-16,1,-15), (16,1,-15), (-16,1,15), (16,1,15)]:
    Entity(model='cube', scale=(1,2,1), position=pos, color=color.rgb(30,120,30), collider='box')

# Mesas y Sillones
Entity(model='cube', scale=(3,1,1.5), position=(-10,0.5,8), color=color.brown, collider='box')
Entity(model='cube', scale=(3,1,1.5), position=(10,0.5,8), color=color.brown, collider='box')
Entity(model='cube', scale=(2.5,2,2), position=(-10,1,4), color=color.rgb(90,40,20), collider='box')
Entity(model='cube', scale=(2.5,2,2), position=(10,1,4), color=color.rgb(90,40,20), collider='box')

# Lámparas de pie
Entity(model='cube', scale=(0.3,3,0.3), position=(-12,1.5,-5), color=color.rgb(200,180,100))
Entity(model='cube', scale=(0.3,3,0.3), position=(12,1.5,-5), color=color.rgb(200,180,100))

#====================================
# LA LLAVE (OCULTA EN UNA MESA)
#====================================
llave = Entity(model='cube', scale=0.4, position=(-10, 1.2, 8), color=color.gold)

#====================================
# JUGADOR Y CÁMARA
#====================================
jugador = FirstPersonController(position=(0,2,-10))

#====================================
# LÓGICA DEL JUEGO (UPDATE)
#====================================
def update():
    global tiene_llave, reloj_activado

    # Por defecto, ocultar el texto si el jugador no está cerca de nada
    mensaje_ui.text = ''

    # Calcular distancias
    distancia_llave = distance(jugador.position, llave.position)
    distancia_reloj = distance(jugador.position, reloj_interactivo.position)
    distancia_puerta = distance(jugador.position, puerta_salida.position)

    # Lógica de la llave
    if not tiene_llave and distancia_llave < 3:
        mensaje_ui.text = "Presiona E para agarrar la llave dorada"
        if held_keys['e']:
            llave.visible = False
            tiene_llave = True

    # Lógica del reloj
    elif distancia_reloj < 4:
        if not reloj_activado:
            mensaje_ui.text = "Presiona R para investigar el gran reloj"
            if held_keys['r']:
                # Cambiamos el color sutilmente para dar feedback al jugador
                reloj_interactivo.color = color.rgb(100, 150, 60) 
                reloj_activado = True
        else:
            mensaje_ui.text = "El reloj emite un extraño tic-tac..."

    # Lógica de la puerta principal
    elif distancia_puerta < 4:
        if tiene_llave and reloj_activado:
            mensaje_ui.text = "Presiona E para abrir la puerta principal"
            if held_keys['e']:
                puerta_salida.visible = False
                # Aquí podrías cargar el siguiente nivel en el futuro
                mensaje_ui.text = "¡Lograste salir del recibidor!"
        else:
            mensaje_ui.text = "La puerta está bloqueada. Faltan piezas del rompecabezas."

app.run()