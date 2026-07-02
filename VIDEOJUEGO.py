from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import load_texture

#VARIABLES
cronometro_texto = Text(text='01:00',position=(0, 0.45),origin=(0, 0),scale=2,color=color.white,background=True)
cronometro_texto.disable()
fondo_game_over = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 220), scale=(2, 1.5), z=-0.2, enabled=False)
texto_game_over = Text(parent=camera.ui, text="", scale=2, origin=(0, 0), position=(0, 0.2), color=color.red, z=-0.3, enabled=False)
app = Ursina()
camera.clip_plane_near = 0.09
window.fps_counter.enabled = False
window.exit_button.visible = False
tiempo_restante = 1 * 60  
intro_terminada = False
game_over_activo = False   
vidas = 3
checkpoint_pos = Vec3(0, 2, 0)

#CLASES Y FUNCIONES
class Mundo:
    def __init__(self):
        self.suelo = Entity(model='plane', scale=(500, 1, 500), color=color.gray, texture='white_cube', collider='box')
        self.paredes = [
            Entity(model='cube', position=(0, 10, 250), scale=(500, 20, 1), collider='box', visible=False, name='muro'),
            Entity(model='cube', position=(0, 10, -250), scale=(500, 20, 1), collider='box', visible=False, name='muro'),
            Entity(model='cube', position=(250, 10, 0), scale=(1, 20, 500), collider='box', visible=False, name='muro'),
            Entity(model='cube', position=(-250, 10, 0), scale=(1, 20, 500), collider='box', visible=False, name='muro')
        ]

class InventarioUI:
    def __init__(self):
        self.slot1 = None
        self.barra = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 150), scale=(0.25, 0.08), position=(0, -0.42),enabled=False)
        self.cuadro = Entity(parent=camera.ui, model='quad', color=color.rgba(50, 50, 50, 255), scale=(0.04, 0.04), position=(-0.08, -0.42),enabled=False)
        self.texto = Text(parent=camera.ui, text="1: [ Vacio ]", position=(-0.04, -0.42), scale=1.5, color=color.light_gray,enabled=False)
        self.objeto_mano = Entity(parent=camera, model='cube', color=color.yellow, scale=(0.1, 0.1, 0.4), position=(0.35, -0.25, 0.6), enabled=False)

    def activar(self):
        self.barra.enabled = True
        self.cuadro.enabled = True
        self.texto.enabled = True

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

class ObjetoLanzable(Entity):
    def __init__(self, posicion, direccion, nombre, jugador_ref):
        super().__init__(model='cube', color=color.yellow, scale=(0.5, 0.5, 0.5), position=posicion,name=nombre)
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
        self.jump_height = 2               
        self.jump_up_duration = 0.4    
        self.gravity = 1               

    def input(self, key):
        if key == 'escape': application.quit()
        if not self.enabled: return
        super().input(key)
        if key == 'e':
            hit_info = boxcast(camera.world_position, direction=camera.forward, distance=4.5, thickness=(0.5, 0.5), ignore=(self, *self.mundo.paredes) )
            if hit_info.hit:
                obj = hit_info.entity
                if hasattr(obj, 'agarrable'):
                    self.ui.guardar_objeto(obj.name)
                    destroy(obj)
        if key == '1':
            self.ui.alternar_equipado()
        if key == 'left mouse down' and self.ui.objeto_mano.enabled:
            ObjetoLanzable(posicion=camera.world_position + camera.forward, direccion=camera.forward, nombre=self.ui.slot1,jugador_ref=self)
            self.ui.vaciar_slot()
        if key == 'shift': self.speed = self.vel_correr
        if key == 'shift up': self.speed = self.vel_normal
        if key == 'c':
            self.speed = self.vel_sigilo
            self.camera_pivot.y = self.altura_agachado
        if key == 'c up':
            self.speed = self.vel_normal
            self.camera_pivot.y = self.altura_normal

class Introduccion:
    def __init__(self, jugador_ref):
        self.jugador = jugador_ref
        self.pantalla = Entity(parent=camera.ui, model='quad', color=color.black, scale=(2, 2), z=2, enabled=False)
        mensaje = "Oficial, necesitamos que investigue\nla mansión Miller\npor casos de personas desaparecidas."
        self.texto = Text(text=mensaje, position=(0, 0), origin=(0, 0), scale=2, color=color.white, alpha=0, z=1)
        self.audio_voz = Audio('voz_intro.mp3', autoplay=False, loop=False)

    def iniciar(self):
        self.pantalla.enabled = True
        self.audio_voz.play()
        invoke(self.aparecer_texto, delay=1.0)

    def aparecer_texto(self):
        self.texto.fade_in(duration=4.0)
        invoke(self.desaparecer_texto, delay=5.0)

    def desaparecer_texto(self):
        self.texto.fade_out(duration=2.0)
        invoke(self.finalizar, delay=2.5)

    def finalizar(self):
        global intro_terminada     
        intro_terminada = True
        self.pantalla.fade_out(duration=3.5)
        self.jugador.enable()
        self.jugador.ui.activar()

class Menu:
    def __init__(self, intro_ref):
        self.intro=intro_ref
        self.fondo_menu= Entity(parent=camera.ui, model='quad',texture="fondo_original.jpg",color=color.white,scale=(2,1.5))
        self.titulo=Text(parent=camera.ui, text="La Mansión Miller",scale=3,origin=(0,0), position=(0,0.3), color=color.red,z=-0.1)
        self.boton_play=Button(parent=camera.ui, text="PLAY", scale=(0.3,0.1), position=(0,-0.1),color=color.black,z=-0.1)
        self.boton_play.on_click= self.click_play
    
    def click_play(self):
        destroy(self.titulo)
        destroy(self.boton_play)
        destroy(self.fondo_menu)
        self.intro.iniciar()

def update():
    global tiempo_restante, intro_terminada,game_over_activo, vidas
    if game_over_activo:
        return
    if intro_terminada and tiempo_restante > 0:
        cronometro_texto.enable() 
        tiempo_restante -= time.dt 
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        cronometro_texto.text = f"{minutos:02d}:{segundos:02d}"
        if tiempo_restante <= 0:
            cronometro_texto.text = "00:00"
            cronometro_texto.color = color.red
            game_over_activo = True
            protagonista.disable()  
            mouse.locked = False    
            mouse.visible = True
            fondo_game_over.enabled = True
            texto_game_over.enabled = True
            if vidas > 1:
                texto_game_over.text = f"GAME OVER\n¿Quieres intentar de vuelta?\n(Te quedarán {vidas - 1} vidas)"
                boton_si.enabled = True
                boton_no.enabled = True
            else:
                texto_game_over.text = "GAME OVER\nJuego Finalizado"

def click_si():
    global vidas, tiempo_restante, game_over_activo
    vidas -= 1               
    tiempo_restante = 1 * 60
    fondo_game_over.enabled = False
    texto_game_over.enabled = False
    boton_si.enabled = False
    boton_no.enabled = False
    protagonista.position = checkpoint_pos
    protagonista.enable()
    mouse.locked = True
    mouse.visible = False
    game_over_activo = False

def click_no():
    boton_si.enabled = False
    boton_no.enabled = False
    texto_game_over.text = "Juego Finalizado"

boton_si = Button(parent=camera.ui, text="SÍ", scale=(0.2, 0.08), position=(-0.15, -0.1), color=color.black, z=-0.3, enabled=False)
boton_no = Button(parent=camera.ui, text="NO", scale=(0.2, 0.08), position=(0.15, -0.1), color=color.black, z=-0.3, enabled=False)
boton_si.on_click = click_si
boton_no.on_click = click_no

# INICIALIZACIÓN PRINCIPAL
escenario = Mundo()
interfaz = InventarioUI()
protagonista = Jugador(interfaz, escenario)
mano = Entity(model="protagonista.obj", texture='textura_policia.png',parent=camera,position=(0.5, -0.3, 0.7),rotation=(0, 0, 0),scale=0.1,color=color.white)
mano.disable_shadows=True
intro = Introduccion(protagonista)
menu=Menu(intro)
app.run() 