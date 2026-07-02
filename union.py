# =========================================================
# EL SECRETO DE LA MANSION MILLER - UNIFICADO Y CORREGIDO
# =========================================================

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# =========================================================
# CONFIGURACION GENERAL
# =========================================================
window.title = "El Secreto de la Mansion Miller"
window.fps_counter.enabled = False
window.exit_button.visible = False

DirectionalLight()
AmbientLight(color=color.hex('#505050'))

# Contenedor global para los objetos del nivel actual
nivel_parent = Entity()
texto_nivel = Text(text='', scale=2, y=0.45, color=color.white, origin=(0,0))

# ==========================================
# CLASE INVENTARIO (Interfaz y Lógica UI)
# ==========================================
class InventarioUI:
    def __init__(self):
        self.slot1 = None
        
        # CORREGIDO: Se restauró a color.rgba para evitar el AttributeError
        self.barra = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 150), scale=(0.25, 0.08), position=(0, -0.42))
        self.cuadro = Entity(parent=camera.ui, model='quad', color=color.hex('#323232'), scale=(0.04, 0.04), position=(-0.08, -0.42))
        self.texto = Text(parent=camera.ui, text="1: [ Vacio ]", position=(-0.04, -0.42), scale=1.5, color=color.light_gray)
        
        self.objeto_mano = Entity(parent=camera, model='cube', color=color.yellow, scale=(0.1, 0.1, 0.4), position=(0.35, -0.25, 0.6), enabled=False)

    def guardar_objeto(self, nombre):
        self.slot1 = nombre
        self.texto.text = f"1: {nombre}"
        self.texto.color = color.yellow
        self.cuadro.color = color.yellow

    def vaciar_slot(self):
        self.slot1 = None
        self.objeto_mano.enabled = False
        self.texto.text = "1: [ Vacio ]"
        self.texto.color = color.light_gray
        self.cuadro.color = color.hex('#323232')

    def alternar_equipado(self):
        if self.slot1:
            self.objeto_mano.enabled = not self.objeto_mano.enabled

# ==========================================
# CLASE OBJETO LANZABLE (Físicas independientes)
# ==========================================
class ObjetoLanzable(Entity):
    def __init__(self, posicion, direccion, nombre, jugador_ref):
        super().__init__(
            model='cube', 
            color=color.yellow, 
            scale=(0.5, 0.5, 0.5), 
            position=posicion, 
            name=nombre
        )
        self.agarrable = True
        self.direccion = direccion
        self.fuerza_lanzamiento = 25
        self.velocidad_y = 8
        self.jugador_ref = jugador_ref

    def update(self):
        if self.fuerza_lanzamiento > 0 or self.y > -0.25:
            self.velocidad_y -= time.dt * 15
            desplazamiento = (self.direccion * self.fuerza_lanzamiento + Vec3(0, self.velocidad_y, 0)) * time.dt
            
            hit_info = raycast(self.world_position, desplazamiento.normalized(), distance=0.6, ignore=(self, self.jugador_ref))
            
            if hit_info.hit:
                self.fuerza_lanzamiento = 0
                self.velocidad_y = -2 
            else:
                self.position += desplazamiento

            if self.y <= -0.25:
                self.y = -0.25
                self.fuerza_lanzamiento = 0
                self.velocidad_y = 0
                self.collider = 'box' 

# ==========================================
# CLASE JUGADOR (Controles y Lógica)
# ==========================================
class Jugador(FirstPersonController):
    def __init__(self, inventario_ui):
        super().__init__(position=(0, 2, 0))
        self.collider = 'box'
        self.enabled = False 
        
        self.ui = inventario_ui
        
        self.vel_normal = 5
        self.vel_correr = 8
        self.vel_sigilo = 2.5
        self.altura_normal = self.camera_pivot.y
        self.altura_agachado = 1.0
        self.speed = self.vel_normal

        self.jump_height = 2.0        
        self.jump_up_duration = 0.5    
        self.gravity = 1              

    def input(self, key):
        if key == 'escape': application.quit()
        if not self.enabled: return

        if key == 'space':
            self.jump()

        if key == 'e':
            hit_info = boxcast(
                camera.world_position, 
                direction=camera.forward, 
                distance=4.5, 
                thickness=(0.5, 0.5), 
                ignore=(self, ) 
            )
            if hit_info.hit:
                obj = hit_info.entity
                
                # Lógica para recoger objetos (ya la tenías)
                if hasattr(obj, 'agarrable') and obj.agarrable:
                    self.ui.guardar_objeto(obj.name)
                    destroy(obj)
                
                # NUEVA LÓGICA: Abrir la puerta con la llave
                if hasattr(obj, 'es_puerta') and obj.es_puerta:
                    if self.ui.slot1 == "Llave Dorada":
                        self.ui.vaciar_slot()  # Opcional: gasta la llave al usarla
                        nivel_2()              # Te teletransporta al nivel 2

        if key == '1':
            self.ui.alternar_equipado()

        if key == 'left mouse down' and self.ui.objeto_mano.enabled:
            ObjetoLanzable(
                posicion=camera.world_position + camera.forward, 
                direccion=camera.forward, 
                nombre=self.ui.slot1,
                jugador_ref=self
            )
            self.ui.vaciar_slot()

        if key == 'shift': self.speed = self.vel_correr
        if key == 'shift up': self.speed = self.vel_normal
        if key == 'c':
            self.speed = self.vel_sigilo
            self.camera_pivot.y = self.altura_agachado
        if key == 'c up':
            self.speed = self.vel_normal
            self.camera_pivot.y = self.altura_normal

# ==========================================
# CLASE INTRODUCCIÓN (Cinemática inicial)
# ==========================================
class Introduccion:
    def __init__(self, jugador_ref):
        self.jugador = jugador_ref
        self.pantalla = Entity(parent=camera.ui, model='quad', color=color.black, scale=(2, 2), z=2)
        
        mensaje = "Oficial, necesitamos que investigue\nla mansión Miller\npor casos de personas desaparecidas."
        self.texto = Text(text=mensaje, position=(0, 0), origin=(0, 0), scale=2, color=color.white, alpha=0, z=1)

    def iniciar(self):
        invoke(self.aparecer_texto, delay=1.5)

    def aparecer_texto(self):
        self.texto.fade_in(duration=3.0)
        invoke(self.desaparecer_texto, delay=5.0)

    def desaparecer_texto(self):
        self.texto.fade_out(duration=2.0)
        invoke(self.finalizar, delay=2.5)

    def finalizar(self):
        self.pantalla.fade_out(duration=2.5)
        self.jugador.enable()

# =========================================================
# GESTOR DE NIVELES
# =========================================================

def limpiar_nivel():
    global nivel_parent
    destroy(nivel_parent)
    nivel_parent = Entity()
    protagonista.position = (0, 2, 0)

def nivel_1():
    limpiar_nivel()
    Sky(parent=nivel_parent, color=color.hex('#050505'))
    texto_nivel.text = 'NIVEL 1 - RECIBIDOR'

    Entity(parent=nivel_parent, model='cube', scale=(30,1,30), position=(0,-1,0), color=color.hex('#323232'), collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(30,1,30), position=(0,7,0), color=color.hex('#141414'), collider='box')

    color_pared = color.hex('#191919')
    Entity(parent=nivel_parent, model='cube', scale=(30,8,1), position=(0,3,15), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(30,8,1), position=(0,3,-15), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,8,30), position=(15,3,0), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,8,30), position=(-15,3,0), color=color_pared, collider='box')

    Entity(parent=nivel_parent, model='cube', scale=(4,6,1), position=(0,2,-14.5), color=color.hex('#5a1e1e'), collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(5,1,3), position=(0,0,5), color=color.brown, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(2,2,0.2), position=(-10,3,10), color=color.hex('#781e1e'))

    llave = Entity(parent=nivel_parent, model='cube', scale=0.8, position=(8,-0.1,8), color=color.yellow, collider='box')
    llave.agarrable = True
    llave.name = "Llave Dorada"

    for i in range(4):
        Entity(parent=nivel_parent, model='cube', scale=(2,3,0.2), position=(-14,2,-8 + i*5), color=color.hex('#3c3c3c'))


def nivel_2():
    limpiar_nivel()
    Sky(parent=nivel_parent, color=color.hex('#050505'))
    texto_nivel.text = 'NIVEL 2 - ZONA FAMILIAR'

    Entity(parent=nivel_parent, model='cube', scale=(35,1,35), position=(0,-1,0), color=color.hex('#282828'), collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(35,1,35), position=(0,8,0), color=color.hex('#0f0f0f'), collider='box')

    color_pared = color.hex('#141414')
    Entity(parent=nivel_parent, model='cube', scale=(35,9,1), position=(0,3,17), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(35,9,1), position=(0,3,-17), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,9,35), position=(17,3,0), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,9,35), position=(-17,3,0), color=color_pared, collider='box')

    Entity(parent=nivel_parent, model='cube', scale=(8,1,4), position=(0,0,0), color=color.hex('#462814'), collider='box')
    
    for i in range(5):
        jug = Entity(parent=nivel_parent, model='sphere', scale=1, position=(-8 + i*3,0,-5), color=color.random_color(), collider='box')
        jug.agarrable = True
        jug.name = f"Juguete {i+1}"

    Entity(parent=nivel_parent, model='cube', scale=(3,3,0.2), position=(10,3,10), color=color.cyan)
    Entity(parent=nivel_parent, model='cube', scale=(5,2,3), position=(10,0,5), color=color.gray, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(2,5,2), position=(-10,2,-10), color=color.black, collider='box')


def nivel_3():
    limpiar_nivel()
    Sky(parent=nivel_parent, color=color.hex('#030303'))
    texto_nivel.text = 'NIVEL 3 - BIBLIOTECA Y ATICO'

    Entity(parent=nivel_parent, model='cube', scale=(40,1,40), position=(0,-1,0), color=color.hex('#232323'), collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(40,1,40), position=(0,10,0), color=color.hex('#0a0a0a'), collider='box')

    color_pared = color.hex('#121212')
    Entity(parent=nivel_parent, model='cube', scale=(40,10,1), position=(0,4,20), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(40,10,1), position=(0,4,-20), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,10,40), position=(20,4,0), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,10,40), position=(-20,4,0), color=color_pared, collider='box')

    for i in range(5):
        Entity(parent=nivel_parent, model='cube', scale=(2,6,1), position=(-15 + i*6,2,12), color=color.hex('#321e0a'), collider='box')

    for i in range(8):
        Entity(parent=nivel_parent, model='cube', scale=(1,0.3,1), position=(-10 + i*3,4,-5), color=color.random_color())

    Entity(parent=nivel_parent, model='cube', scale=(3,2,2), position=(10,1,10), color=color.gray, collider='box')

    for i in range(4):
        Entity(parent=nivel_parent, model='cube', scale=(1,4,1), position=(-10 + i*5,2,-12), color=color.black, collider='box')


def nivel_4():
    limpiar_nivel()
    Sky(parent=nivel_parent, color=color.hex('#020202'))
    texto_nivel.text = 'NIVEL 4 - LABORATORIO'

    Entity(parent=nivel_parent, model='cube', scale=(40,1,40), position=(0,-1,0), color=color.hex('#1e1e1e'), collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(40,1,40), position=(0,10,0), color=color.hex('#0a0a0a'), collider='box')

    color_pared = color.hex('#0f0f0f')
    Entity(parent=nivel_parent, model='cube', scale=(40,10,1), position=(0,4,20), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(40,10,1), position=(0,4,-20), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,10,40), position=(20,4,0), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,10,40), position=(-20,4,0), color=color_pared, collider='box')

    for i in range(5):
        Entity(parent=nivel_parent, model='cube', scale=(3,4,3), position=(-15 + i*7,1,10), color=color.gray, collider='box')

    for i in range(6):
        Entity(parent=nivel_parent, model='cube', scale=(0.3,0.3,5), position=(-15 + i*5,0,-5), color=color.random_color())

    for i in range(3):
        Entity(parent=nivel_parent, model='cube', scale=(3,6,3), position=(-10 + i*10,2,-12), color=color.cyan, collider='box')

    Entity(parent=nivel_parent, model='cube', scale=(8,1,3), position=(0,0,0), color=color.hex('#3c3c3c'), collider='box')

    colores = [color.red, color.yellow, color.orange]
    nombres = ["Quimico Rojo", "Quimico Amarillo", "Quimico Naranja"]
    for i in range(3):
        qui = Entity(parent=nivel_parent, model='sphere', scale=1, position=(-2 + i*2,1,0), color=colores[i], collider='box')
        qui.agarrable = True
        qui.name = nombres[i]


def nivel_5():
    limpiar_nivel()
    Sky(parent=nivel_parent, color=color.hex('#010101'))
    texto_nivel.text = 'NIVEL 5 - ESCAPE FINAL'

    Entity(parent=nivel_parent, model='cube', scale=(50,1,50), position=(0,-1,0), color=color.hex('#191919'), collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(50,1,50), position=(0,12,0), color=color.hex('#080808'), collider='box')

    color_pared = color.hex('#0c0c0c')
    Entity(parent=nivel_parent, model='cube', scale=(50,12,1), position=(0,5,25), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(50,12,1), position=(0,5,-25), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,12,50), position=(25,5,0), color=color_pared, collider='box')
    Entity(parent=nivel_parent, model='cube', scale=(1,12,50), position=(-25,5,0), color=color_pared, collider='box')

    Entity(parent=nivel_parent, model='cube', scale=(10,10,1), position=(0,4,-24), color=color.hex('#461414'), collider='box')

    for i in range(3):
        Entity(parent=nivel_parent, model='cube', scale=(1,2,1), position=(-10 + i*10,1,10), color=color.red, collider='box')

    Entity(parent=nivel_parent, model='cube', scale=(5,10,5), position=(0,4,15), color=color.black, collider='box')

    for i in range(4):
        Entity(parent=nivel_parent, model='cube', scale=(1,3,1), position=(-6 + i*4,1,-10), color=color.azure, collider='box')

# =========================================================
# CONTROLES GLOBALES (Cambio de niveles)
# =========================================================
def input(key):
    if key == '1': nivel_1()
    if key == '2': nivel_2()
    if key == '3': nivel_3()
    if key == '4': nivel_4()
    if key == '5': nivel_5()

# =========================================================
# INICIO
# =========================================================

interfaz = InventarioUI()
protagonista = Jugador(interfaz)

intro = Introduccion(protagonista)
intro.iniciar()

nivel_1()

app.run()