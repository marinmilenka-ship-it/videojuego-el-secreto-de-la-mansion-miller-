from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# ==================================================
# CONFIGURACION
# ==================================================

window.title = "El Secreto de la Mansion Miller"
window.color = color.rgb(10,10,10)

DirectionalLight(y=20, z=10)
AmbientLight(color=color.rgba(80,80,80,0.4))

Sky(color=color.rgb(5,5,5))

# ==================================================
# SALA 1
# ==================================================

def nivel_1():

    color_pared = color.rgb(40,25,20)
    color_piso = color.rgb(60,40,25)
    color_techo = color.rgb(15,10,10)

    # PISO
    Entity(
        model='cube',
        scale=(30,1,30),
        position=(0,-1,0),
        color=color.rgb(60,40,25)
    )

     # TECHO
    Entity(
        model='cube',
        scale=(30,1,30),
        position=(0,7,0),
        color=color.rgb(15,10,10)
    )
    
    # Pared del fondo
    Entity(
        model='cube',
        scale=(30,8,1),
        position=(0,3,15),
        color=color_pared,
        collider='box'
    )

    # Pared de entrada
    Entity(
        model='cube',
        scale=(30,8,1),
        position=(0,3,-15),
        color=color_pared,
        collider='box'
    )

    # Pared derecha
    Entity(
        model='cube',
        scale=(1,8,30),
        position=(15,3,0),
        color=color_pared,
        collider='box'
    )

    # Pared izquierda
    Entity(
        model='cube',
        scale=(1,8,30),
        position=(-15,3,0),
        color=color_pared,
        collider='box'
    )

    # ALFOMBRA
    Entity(
        model='cube',
        scale=(8,0.1,14),
        position=(0,-0.45,0),
        color=color.rgb(90,15,15)
    )

    # MESA
    Entity(
        model='cube',
        scale=(4,1,2),
        position=(-6,0,4),
        color=color.brown,
        collider='box'
    )

    # SILLON
    Entity(
        model='cube',
        scale=(3,2,2),
        position=(8,1,4),
        color=color.rgb(70,40,20),
        collider='box'
    )

    # PLANTAS
    Entity(
        model='cube',
        scale=(1,2,1),
        position=(-12,1,-6),
        color=color.rgb(20,80,20),
        collider='box'
    )

    Entity(
        model='cube',
        scale=(1,2,1),
        position=(12,1,-6),
        color=color.rgb(20,80,20),
        collider='box'
    )

    # RELOJES IZQUIERDA Y DERECHA
    for i in range(4):

        Entity(
            model='cube',
            scale=(1.5,1.5,0.2),
            position=(-14,3,-8 + i*5),
            color=color.rgb(120,80,40)
        )

        Entity(
            model='cube',
            scale=(1.5,1.5,0.2),
            position=(14,3,-8 + i*5),
            color=color.rgb(120,80,40)
        )

    # RELOJ CENTRAL GIGANTE
    Entity(
        model='cube',
        scale=(4,4,0.3),
        position=(0,4,14),
        color=color.rgb(140,100,50)
    )

    # ESCALERA
    for i in range(10):

        Entity(
            model='cube',
            scale=(6,0.4,1),
            position=(0,i*0.4,12-i),
            color=color.rgb(90,90,90),
            collider='box'
        )

    # LAMPARA IZQUIERDA
    Entity(
        model='cube',
        scale=(0.5,3,0.5),
        position=(-10,1.5,2),
        color=color.rgb(180,150,80)
    )

    # LAMPARA DERECHA
    Entity(
        model='cube',
        scale=(0.5,3,0.5),
        position=(10,1.5,2),
        color=color.rgb(180,150,80)
    )

    # ARAÑA DE TECHO
    Entity(
        model='sphere',
        scale=1.5,
        position=(0,5.5,0),
        color=color.rgb(200,180,100)
    )

    Text(
        text='SALA 1 - RECIBIDOR',
        scale=2,
        y=0.45,
        color=color.white
    )

# ==================================================
# JUGADOR
# ==================================================

jugador = FirstPersonController(
    position=(0,2,0)
)

# ==================================================
# INICIO
# ==================================================

nivel_1()
print("LLEGUE HASTA ACA")        
app.run()