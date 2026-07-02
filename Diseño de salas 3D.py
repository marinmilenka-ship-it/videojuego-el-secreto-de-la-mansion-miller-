from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

window.title = "El Secreto de la Mansion Miller"
window.color = color.black

# ====================================
# ILUMINACION
# ====================================

DirectionalLight(y=10, z=5)

AmbientLight(
    color=color.rgba(120,120,120,0.5)
)

# ====================================
# PISO
# ====================================

Entity(
    model='plane',
    scale=40,
    color=color.rgb(70,45,25),
    collider='box'
)

# ====================================
# PAREDES
# ====================================

color_pared = color.rgb(45,30,25)

Entity(
    model='cube',
    scale=(20,8,0.5),
    position=(0,4,10),
    color=color_pared
)

Entity(
    model='cube',
    scale=(20,8,0.5),
    position=(0,4,-10),
    color=color_pared
)

Entity(
    model='cube',
    scale=(0.5,8,20),
    position=(10,4,0),
    color=color_pared
)

Entity(
    model='cube',
    scale=(0.5,8,20),
    position=(-10,4,0),
    color=color_pared
)

# ====================================
# ALFOMBRA
# ====================================

Entity(
    model='cube',
    scale=(5,0.05,12),
    position=(0,0.02,0),
    color=color.rgb(90,15,15)
)

# ====================================
# MESA
# ====================================

Entity(
    model='cube',
    scale=(3,1,2),
    position=(0,0.5,-2),
    color=color.brown,
    collider='box'
)

# ====================================
# SILLON
# ====================================

Entity(
    model='cube',
    scale=(2,2,2),
    position=(6,1,-2),
    color=color.rgb(80,40,20),
    collider='box'
)

# ====================================
# PLANTAS
# ====================================

Entity(
    model='cube',
    scale=(1,2,1),
    position=(-8,1,-5),
    color=color.green
)

Entity(
    model='cube',
    scale=(1,2,1),
    position=(8,1,-5),
    color=color.green
)

# ====================================
# RELOJES IZQUIERDA
# ====================================

for i in range(4):

    Entity(
        model='cube',
        scale=(1.5,1.5,0.1),
        position=(-9,3,-5+i*4),
        color=color.rgb(140,110,60)
    )

# ====================================
# RELOJES DERECHA
# ====================================

for i in range(4):

    Entity(
        model='cube',
        scale=(1.5,1.5,0.1),
        position=(9,3,-5+i*4),
        color=color.rgb(140,110,60)
    )

# ====================================
# CUADROS
# ====================================

for i in range(3):

    Entity(
        model='cube',
        scale=(1.5,2,0.1),
        position=(-5,3,-4+i*4),
        color=color.rgb(70,70,70)
    )

for i in range(3):

    Entity(
        model='cube',
        scale=(1.5,2,0.1),
        position=(5,3,-4+i*4),
        color=color.rgb(70,70,70)
    )

# ====================================
# ESCALERA
# ====================================

for i in range(10):

    Entity(
        model='cube',
        scale=(5,0.3,1),
        position=(0,0.15+i*0.3,8-i),
        color=color.gray,
        collider='box'
    )

# ====================================
# TEXTO
# ====================================

Text(
    text="SALA 1 - RECIBIDOR",
    origin=(0,0),
    scale=2,
    y=0.45
)

# ====================================
# JUGADOR
# ====================================

jugador = FirstPersonController(
    position=(0,2,-7)
)

app.run()