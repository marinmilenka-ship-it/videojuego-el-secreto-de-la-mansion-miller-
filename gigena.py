from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

window.fps_counter.enabled = False
window.exit_button.visible = False

# ==========================================
# CLASE MUNDO (Entorno y límites)
# ==========================================
class Mundo:
    def __init__(self):
        self.suelo = Entity(model='plane', scale=(500, 1, 500), color=color.gray, texture='white_cube', collider='box')
        
        self.paredes = [
            Entity(model='cube', position=(0, 10, 250), scale=(500, 20, 1), collider='box', visible=False, name='muro'),
            Entity(model='cube', position=(0, 10, -250), scale=(500, 20, 1), collider='box', visible=False, name='muro'),
            Entity(model='cube', position=(250, 10, 0), scale=(1, 20, 500), collider='box', visible=False, name='muro'),
            Entity(model='cube', position=(-250, 10, 0), scale=(1, 20, 500), collider='box', visible=False, name='muro')
        ]

# ==========================================
# CLASE INVENTARIO (Interfaz y Lógica UI)
# ==========================================
class InventarioUI:
    def __init__(self):
        self.slot1 = None
        
        self.barra = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 150), scale=(0.25, 0.08), position=(0, -0.42))
        self.cuadro = Entity(parent=camera.ui, model='quad', color=color.rgba(50, 50, 50, 255), scale=(0.04, 0.04), position=(-0.08, -0.42))
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
        self.cuadro.color = color.rgba(50, 50, 50, 255)

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
        if self.fuerza_lanzamiento > 0 or self.y > 0.25:
            self.velocidad_y -= time.dt * 15
            desplazamiento = (self.direccion * self.fuerza_lanzamiento + Vec3(0, self.velocidad_y, 0)) * time.dt
            
            hit_info = raycast(self.world_position, desplazamiento.normalized(), distance=0.6, ignore=(self, self.jugador_ref))
            
            if hit_info.hit:
                self.fuerza_lanzamiento = 0
                self.velocidad_y = -2 
            else:
                self.position += desplazamiento

            if self.y <= 0.25:
                self.y = 0.25
                self.fuerza_lanzamiento = 0
                self.velocidad_y = 0
                self.collider = 'box' 

# ==========================================
# CLASE JUGADOR (Controles y Lógica)
# ==========================================
class Jugador(FirstPersonController):
    def __init__(self, inventario_ui, mundo_ref):
        super().__init__(position=(0, 2, 0))
        self.collider = 'box'
        self.enabled = False 
        
        self.ui = inventario_ui
        self.mundo = mundo_ref
        
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

        # AÑADIDO: Ahora la barra espaciadora activa el salto real del motor
        if key == 'space':
            self.jump()

        if key == 'e':
            hit_info = boxcast(
                camera.world_position, 
                direction=camera.forward, 
                distance=4.5, 
                thickness=(0.5, 0.5), 
                ignore=(self, *self.mundo.paredes) 
            )
            if hit_info.hit:
                obj = hit_info.entity
                if hasattr(obj, 'agarrable'):
                    self.ui.guardar_objeto(obj.name)
                    destroy(obj)

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

# ==========================================
# INICIALIZACIÓN PRINCIPAL
# ==========================================

escenario = Mundo()
interfaz = InventarioUI()
protagonista = Jugador(interfaz, escenario)

intro = Introduccion(protagonista)
intro.iniciar()

app.run()