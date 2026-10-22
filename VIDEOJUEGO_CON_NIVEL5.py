import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
camera.clip_plane_near = 0.09
window.fps_counter.enabled = False
window.exit_button.visible = False

class Mundo:
    
    class RelojPared(Entity):
        def __init__(self, position, rotation=(0, 0, 0), hora_objetivo=6):
            super().__init__(position=position, rotation=rotation)
            self.hora_objetivo = hora_objetivo
            self.modelo_visual = Entity(parent=self, model='RELOj.obj', color=color.dark_gray, scale=1, rotation=(0, 90, 0), position=(0, 0, 0))
            self.collider = BoxCollider(self, center=(0, 0, 0), size=(2.0, 2.0, 1.0))
            self.hora_actual = 12
            self.pantalla = Text(parent=self, text="12:00", scale=3.5, position=(0, 0, -0.15), color=color.red, origin=(0, 0), z=-0.15)

        def interactuar(self):
            self.hora_actual += 1
            if self.hora_actual > 12:
                self.hora_actual = 1 
            self.pantalla.text = f"{self.hora_actual:02d}:00"
            self.pantalla.color = color.green if self.hora_actual == self.hora_objetivo else color.red

    class PuertaSalida(Entity):
        def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), **kwargs):
            super().__init__(model='PUERTA.obj', texture='araña.png', position=position, rotation=rotation, scale=(1), origin_y=-0.5, collider='box', double_sided=True, **kwargs)

    class Enemigo(Entity):
        def __init__(self, posicion, modelo, jugador_ref, **kwargs):
            textura = kwargs.pop('texture', None)
            super().__init__(position=posicion, **kwargs)
            self.jugador = jugador_ref
            self.velocidad = 3.5
            self.dano = 20
            self.cooldown_ataque = 0
            self.modelo_visual = Entity(parent=self, model=modelo, texture=textura, y=1.2, rotation=(180, 180, 0))

        def update(self):
            if juego.game_over_activo or not juego.intro_terminada or juego.nivel_completado or juego.juego_pausado:
                return
            if self.cooldown_ataque > 0:
                self.cooldown_ataque -= time.dt
            if not self.jugador.agachado:
                dist_2d = Vec2(self.x - self.jugador.x, self.z - self.jugador.z).length()
                self.look_at(Vec3(self.jugador.x, self.y, self.jugador.z))
                if dist_2d > 0.8:
                    self.position += self.forward * self.velocidad * time.dt
                rango_impacto = 2.5 if getattr(self, 'scale_x', 1) > 1.5 else 1.2
                if dist_2d < rango_impacto and self.cooldown_ataque <= 0:
                    if juego.nivel_actual == 5:
                        self.jugador.salud = 0
                    else:
                        self.jugador.recibir_dano(self.dano)
                        self.cooldown_ataque = 1.5

    def __init__(self):
        self.sala = Entity(model='sala1.glb', position=(0, 1.5, 0), rotation=(0, 180, 0), scale=(0.1, 0.1, 0.1), collider='mesh', double_sided=True)
        self.suelo = Entity(model='plane', scale=(500, 1, 500), position=(0, -0.05, 0), visible=False, collider='box')
        self.limites_sala = [
            Entity(model='cube', position=(0, 3, 10.2), scale=(20, 10, 1), visible=False, collider='box'),
            Entity(model='cube', position=(0, 3, -10), scale=(20, 10, 1), visible=False, collider='box'),
            Entity(model='cube', position=(-10, 3, 0), scale=(1, 10, 25), visible=False, collider='box'),
            Entity(model='cube', position=(10, 3, 0), scale=(1, 10, 25), visible=False, collider='box')
        ]
        
        self.puerta_salida = self.PuertaSalida(position=Vec3(-45, 0, 30), rotation=(0, 0, 0))
        self.relojes = [
            self.RelojPared(position=(-3, 3.5, 6), rotation=(0, 0, 0), hora_objetivo=6),
            self.RelojPared(position=(0, 3.5, 6), rotation=(0, 0, 0), hora_objetivo=6),
            self.RelojPared(position=(3, 3.5, 6), rotation=(0, 0, 0), hora_objetivo=6)
        ]
        self.enemigo = None
        self.tarjeta = None

    def generar_enemigo(self, pos_inicial, jugador_ref):
        self.enemigo = self.Enemigo(posicion=pos_inicial, modelo='enemigo.obj', texture='enemigo.png', jugador_ref=jugador_ref)

    def todos_relojes_en_hora(self):
        return all(r.hora_actual == r.hora_objetivo for r in self.relojes)

    def cargar_nivel_2(self):
        if getattr(self, 'puerta_salida', None): destroy(self.puerta_salida)
        for r in getattr(self, 'relojes', []): destroy(r)
        if getattr(self, 'enemigo', None): destroy(self.enemigo)
        if getattr(self, 'sala', None): destroy(self.sala); self.sala = None
        if getattr(self, 'suelo', None): destroy(self.suelo); self.suelo = None
        if hasattr(self, 'limites_sala'): 
            for limite in self.limites_sala: destroy(limite)
            
        self.suelo_nivel2 = Entity(model='suelo.gltf', position=(0, 0, 15), scale=(20, 1, 60), collider='box')
        self.techo_nivel2 = Entity(model='suelo.gltf', position=(0, 15, 15), rotation=(180, 0, 0), scale=(20, 1, 60), collider='box')
        self.bibliotecas = []
        for z in range(-5, 40, 8):
            bib_izq = Entity(model='biblioteca.gltf', position=(-4, 0, z), rotation=(0, 90, 0), scale=2, collider='box')
            bib_der = Entity(model='biblioteca.gltf', position=(4, 0, z), rotation=(0, -90, 0), scale=2, collider='box')
            self.bibliotecas.append(bib_izq)
            self.bibliotecas.append(bib_der)
        self.paredes = [
            Entity(model='pared.gltf', position=(0, 7.5, 40), scale=(20, 15, 1), collider='box'),
            Entity(model='pared.gltf', position=(0, 7.5, -10), scale=(20, 15, 1), collider='box'),
            Entity(model='pared.gltf', position=(-8, 7.5, 15), rotation=(0, 90, 0), scale=(60, 15, 1), collider='box'),
            Entity(model='pared.gltf', position=(8, 7.5, 15), rotation=(0, 90, 0), scale=(60, 15, 1), collider='box')
        ]
        self.libros = []
        posiciones_parkour = [(0, 1.0, 0), (0, 2.5, 7), (0, 4.0, 14), (0, 5.5, 21), (0, 7.0, 28)]
        for pos in posiciones_parkour:
            libro = Entity(model='libro.gltf', position=pos, scale=(4, 0.5, 4), collider='box')
            self.libros.append(libro)
        self.tarjeta = Entity(model='tarjeta.gltf', position=(0, 8.5, 28), scale=2, collider='box')
        self.tarjeta.agarrable = True
        self.tarjeta.name = 'Tarjeta'

    def cargar_nivel_3(self):
        if getattr(self, 'sala', None): destroy(self.sala); self.sala = None
        if getattr(self, 'suelo', None): destroy(self.suelo); self.suelo = None
        if getattr(self, 'suelo_nivel2', None): destroy(self.suelo_nivel2)
        if getattr(self, 'techo_nivel2', None): destroy(self.techo_nivel2)
        for b in getattr(self, 'bibliotecas', []): destroy(b)
        for p in getattr(self, 'paredes', []): destroy(p)
        for l in getattr(self, 'libros', []): destroy(l)
        if getattr(self, 'tarjeta', None): destroy(self.tarjeta)
        self.suelo_nivel3 = Entity(model='suelo.gltf', position=(0, 0, 40), scale=(80, 1, 80), collider='box')
        self.techo_nivel3 = Entity(model='suelo.gltf', position=(0, 15, 40), rotation=(180, 0, 0), scale=(80, 1, 80), collider='box')
        self.paredes_n3 = [
            Entity(model='pared.gltf', position=(0, 7.5, 80), scale=(80, 15, 1), collider='box'),
            Entity(model='pared.gltf', position=(0, 7.5, 0), scale=(80, 15, 1), collider='box'),
            Entity(model='pared.gltf', position=(-40, 7.5, 40), rotation=(0, 90, 0), scale=(80, 15, 1), collider='box'),
            Entity(model='pared.gltf', position=(40, 7.5, 40), rotation=(0, 90, 0), scale=(80, 15, 1), collider='box')
        ]
        self.documentos = []
        for x in range(-30, 31, 10):
            for z in range(15, 66, 10):
                mesa_doc = Entity(model='documentos.gltf', position=(x, 1.0, z), scale=1, collider='box')
                self.documentos.append(mesa_doc)
        mesa_con_llave = random.choice(self.documentos)
        self.llave = Entity(model='llave.gltf', color=color.yellow, position=(mesa_con_llave.x, mesa_con_llave.y + 1.5, mesa_con_llave.z), scale=1.5, collider='box')
        self.llave.agarrable = True
        self.llave.name = 'Llave'

    def cargar_nivel_4(self):
        if getattr(self, 'suelo_nivel3', None): destroy(self.suelo_nivel3)
        if getattr(self, 'techo_nivel3', None): destroy(self.techo_nivel3)
        for p in getattr(self, 'paredes_n3', []): destroy(p)
        for d in getattr(self, 'documentos', []): destroy(d)
        if getattr(self, 'llave', None): destroy(self.llave)
        self.suelo_nivel4 = Entity(model='suelo.gltf', position=(0, 0, 0), scale=(100, 1, 100), collider='box')
        self.techo_nivel4 = Entity(model='suelo.gltf', position=(0, 20, 0), rotation=(180, 0, 0), scale=(100, 1, 100), collider='box')
        self.paredes_n4 = [
            Entity(model='pared.gltf', position=(0, 10, 50), scale=(100, 20, 1), collider='box'),
            Entity(model='pared.gltf', position=(0, 10, -50), scale=(100, 20, 1), collider='box'),
            Entity(model='pared.gltf', position=(-50, 10, 0), rotation=(0, 90, 0), scale=(100, 20, 1), collider='box'),
            Entity(model='pared.gltf', position=(50, 10, 0), rotation=(0, 90, 0), scale=(100, 20, 1), collider='box')
        ]
        self.celda = Entity(model='celda.gltf', position=(0, 6, 15), scale=1, collider='box') 
        self.humano1 = Entity(model='npc2_juego.blend', color=color.blue, position=(-2, 1, 15), scale=(0.6, 1.8, 0.6), collider='box',texture="npc2_juego.png")
        self.humano2 = Entity(model='npc2_juego.blend', color=color.blue, position=(0, 1, 16), scale=(0.6, 1.8, 0.6), collider='box',texture="npc2_juego.png")
        self.humano3 = Entity(model='npc2_juego.blend', color=color.blue, position=(2, 1, 15), scale=(0.6, 1.8, 0.6), collider='box',texture="npc2_juego.png")
        self.civiles_liberados = False
        self.llave_lanzada_ref = None
        self.puerta_salida_n4 = self.PuertaSalida(position=Vec3(-4.8, 0.5, -20.0))
        
    def cargar_nivel_5(self):
        if getattr(self, 'suelo_nivel4', None): destroy(self.suelo_nivel4)
        if getattr(self, 'techo_nivel4', None): destroy(self.techo_nivel4)
        for p in getattr(self, 'paredes_n4', []): destroy(p)
        if getattr(self, 'puerta_salida_n4', None): destroy(self.puerta_salida_n4)
        if getattr(self, 'humano1', None): self.humano1.position = (-2, 0, 0)
        if getattr(self, 'humano2', None): self.humano2.position = (0, 0, -2)
        if getattr(self, 'humano3', None): self.humano3.position = (2, 0, 0)
        self.tarjeta_pasada = False
        self.jefe_generado = False
        self.tarjeta_lanzada_ref = None
        self.suelo_nivel5 = Entity(model='suelo.gltf', position=(0, 0, 0), scale=(100, 1, 100), collider='box')
        self.techo_nivel5 = Entity(model='suelo.gltf', position=(0, 20, 0), rotation=(180, 0, 0), scale=(100, 1, 100), collider='box')
        self.paredes_n5 = [
            Entity(model='pared.gltf', position=(0, 10, 50), scale=(100, 20, 1), collider='box'),
            Entity(model='pared.gltf', position=(0, 10, -50), scale=(100, 20, 1), collider='box'),
            Entity(model='pared.gltf', position=(-50, 10, 0), rotation=(0, 90, 0), scale=(100, 20, 1), collider='box'),
            Entity(model='pared.gltf', position=(50, 10, 0), rotation=(0, 90, 0), scale=(100, 20, 1), collider='box')
        ]
        self.porton_garage = Entity(model='garage.gltf', position=(0, 6, 47), scale=1, collider='box')
        self.mesa = Entity(model='mesa.gltf', position=(0, 2, -35), scale=1, collider='box')
        self.pasador = Entity(model='pasador.gltf', position=(0, 5, -35), rotation=(0, 90, 0), scale=1, collider='box')
        self.pasador.name = 'Pasador'

class Jugador(FirstPersonController):
    class ObjetoLanzable(Entity):
        def __init__(self, posicion, direccion, nombre, jugador_ref):
            super().__init__(model='cube', color=color.yellow, scale=(0.5, 0.5, 0.5), position=posicion, name=nombre)
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

    class InventarioUI:
        def __init__(self):
            self.slot1 = None
            self.barra = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 150), scale=(0.25, 0.08), position=(0, -0.42), enabled=False)
            self.cuadro = Entity(parent=camera.ui, model='quad', color=color.rgba(50, 50, 50, 255), scale=(0.04, 0.04), position=(-0.08, -0.42), enabled=False)
            self.texto = Text(parent=camera.ui, text="1: [ Vacio ]", position=(-0.04, -0.42), scale=1.5, color=color.light_gray, enabled=False)
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

    def __init__(self, pos_inicial):
        super().__init__(position=pos_inicial)
        self.collider = BoxCollider(self, center=(0, 1, 0), size=(0.6, 2, 0.6))
        self.enabled = False
        self.salud = 100
        self.agachado = False
        self.mundo = None
        self.tiempo_inmunidad = 0 
        self.ui = self.InventarioUI()
        self.mano = Entity(model="protagonista.obj", texture='textura_policia.png', parent=camera, position=(0.5, -0.3, 0.7), rotation=(0, 0, 0), scale=0.1, color=color.white)
        self.mano.disable_shadows = True
        self.vel_normal = 5
        self.vel_correr = 8
        self.vel_sigilo = 2.5
        self.altura_normal = self.camera_pivot.y
        self.altura_agachado = 1.0
        self.speed = self.vel_normal
        self.jump_height = 2.5
        self.jump_up_duration = 0.4
        self.gravity = 1
        self.audio_pasos = Audio('pasos.mp3', autoplay=False, loop=True, volume=1)

    def recibir_dano(self, cantidad):
        if self.tiempo_inmunidad > 0:
            return 
        self.salud = max(0, self.salud - cantidad)
        self.tiempo_inmunidad = 1.5 

    def update(self):
        super().update()
        if self.tiempo_inmunidad > 0:
            self.tiempo_inmunidad -= time.dt
        if juego.nivel_completado or juego.game_over_activo or juego.juego_pausado:
            if self.audio_pasos.playing:
                self.audio_pasos.stop()
            return
        moviendose = held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']
        if moviendose and self.grounded and self.enabled:
            if not self.audio_pasos.playing:
                self.audio_pasos.play()
        else:
            if self.audio_pasos.playing:
                self.audio_pasos.stop()

    def input(self, key):
        if key == 'escape': application.quit()
        if not self.enabled or juego.nivel_completado or juego.juego_pausado: return
        super().input(key)
        if key == 'e':
            if juego.nivel_actual == 1 and getattr(self.mundo, 'sala', None):
                objetos_a_ignorar = [self, self.mundo.sala, self.mundo.suelo] + self.mundo.limites_sala
                objetos_a_ignorar = tuple(objetos_a_ignorar)
            else:
                objetos_a_ignorar = (self,)
            hit_info = boxcast(camera.world_position, direction=camera.forward, distance=6.0, thickness=(0.3, 0.3), ignore=objetos_a_ignorar)
            if hit_info.hit and hasattr(hit_info.entity, 'agarrable'):
                self.ui.guardar_objeto(hit_info.entity.name)
                destroy(hit_info.entity)
        if key == '1':
            self.ui.alternar_equipado()
        if key == 'left mouse down':
            if self.ui.objeto_mano.enabled:
                objeto_lanzado = self.ObjetoLanzable(posicion=camera.world_position + camera.forward, direccion=camera.forward, nombre=self.ui.slot1, jugador_ref=self)
                if juego.nivel_actual == 4 and self.ui.slot1 == 'Llave':
                    juego.mundo.llave_lanzada_ref = objeto_lanzado
                if juego.nivel_actual == 5 and self.ui.slot1 == 'Tarjeta':
                    juego.mundo.tarjeta_lanzada_ref = objeto_lanzado
                self.ui.vaciar_slot()
            elif juego.nivel_actual == 1:
                if getattr(self.mundo, 'sala', None):
                    objetos_a_ignorar = [self, self.mundo.sala, self.mundo.suelo] + self.mundo.limites_sala
                    objetos_a_ignorar = tuple(objetos_a_ignorar)
                else:
                    objetos_a_ignorar = (self,)
                hit_info = boxcast(camera.world_position, direction=camera.forward, distance=6.0, thickness=(0.3, 0.3), ignore=objetos_a_ignorar)
                if hit_info.hit:
                    for reloj in self.mundo.relojes:
                       if hit_info.entity == reloj:
                            reloj.interactuar()
                            break
        if key == 'shift': self.speed = self.vel_correr
        if key == 'shift up': self.speed = self.vel_normal
        if key == 'c':
            self.speed = self.vel_sigilo
            self.camera_pivot.y = self.altura_agachado
            self.agachado = True
        if key == 'c up':
            self.speed = self.vel_normal
            self.camera_pivot.y = self.altura_normal
            self.agachado = False

class AdministradorJuego:
    class InterfazJuego:
        def __init__(self, manager):
            self.manager = manager
            self.cronometro_texto = Text(text='01:00', position=(0, 0.45), origin=(0, 0), scale=2, color=color.white, background=True, enabled=False)
            self.texto_vida = Text(text='Vida: 100', position=(-0.85, 0.45), origin=(-0.5, 0), scale=2, color=color.green, background=True, enabled=False)
            self.texto_coordenadas = Text(text='X: 0.0 | Y: 0.0 | Z: 0.0', position=(-0.85, 0.40), origin=(-0.5, 0), scale=1.5, color=color.yellow, background=True, enabled=False)
            self.instruccion_pista = Text(text="[P] VER PISTA", position=(0.75, 0.45), origin=(0.5, 0), scale=1.5, color=color.cyan, background=True, enabled=False)
            self.panel_pista = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 240), scale=(1.6, 1.2), z=-5, enabled=False)
            self.titulo_pista = Text(parent=self.panel_pista, text="PISTA DEL NIVEL", scale=2.0, origin=(0, 0), position=(0, 0.35), color=color.yellow, z=-6)
            self.texto_detalle_pista = Text(parent=self.panel_pista, text="", scale=1.1, origin=(0, 0), position=(0, 0.1), color=color.white, z=-6)
            self.boton_volver_pista = Button(parent=self.panel_pista, text="VOLVER AL JUEGO", scale=(0.4, 0.08), position=(0, -0.4), color=color.red, z=-6, on_click=self.ocultar_pista)
            self.fondo_game_over = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 220), scale=(2, 1.5), z=-0.2, enabled=False)
            self.texto_game_over = Text(parent=camera.ui, text="", scale=2, origin=(0, 0), position=(0, 0.2), color=color.red, z=-0.3, enabled=False)
            self.panel_victoria = Entity(parent=camera.ui, model='quad', texture='fondo_nivel1.png', color=color.white, scale=(2, 1.5), z=-10, enabled=False)
            self.texto_victoria = Text(parent=camera.ui, text="Has completado el nivel 1", scale=3, origin=(0, 0), position=(0, 0.1), color=color.green, background=True, z=-20, enabled=False)
            self.boton_siguiente = Button(parent=camera.ui, text="SIGUIENTE NIVEL", scale=(0.3, 0.08), position=(0, -0.15), color=color.black, z=-20, enabled=False, on_click=self.manager.avanzar_nivel)
            self.boton_si = Button(parent=camera.ui, text="SÍ", scale=(0.2, 0.08), position=(-0.15, -0.1), color=color.black, z=-0.3, enabled=False, on_click=self.manager.reiniciar_nivel)
            self.boton_no = Button(parent=camera.ui, text="NO", scale=(0.2, 0.08), position=(0.15, -0.1), color=color.black, z=-0.3, enabled=False, on_click=application.quit)
            self.fondo_menu = Entity(parent=camera.ui, model='quad', texture="fondo_original.jpg", color=color.white, scale=(2, 1.5))
            self.titulo = Text(parent=camera.ui, text="La Mansión Miller", scale=3, origin=(0, 0), position=(0, 0.3), color=color.red, z=-0.1)
            self.boton_play = Button(parent=camera.ui, text="PLAY", scale=(0.3, 0.1), position=(0, -0.1), color=color.black, z=-0.1, on_click=self.click_play)
            self.boton_controles = Button(parent=camera.ui, text="CONTROLES", scale=(0.3, 0.1), position=(0, -0.25), color=color.black, z=-0.1, on_click=self.mostrar_controles)
            self.menu_controles = Entity(parent=camera.ui, enabled=False, z=-1)
            Entity(parent=self.menu_controles, model='quad', color=color.rgba(0, 0, 0, 240), scale=(2, 1.5))
            texto_teclas = "W, A, S, D - Moverse\nMouse - Mirar\nShift - Correr\nC - Sigilo\nE - Interactuar / Recoger\n1 - Equipar\nClick Izq. - Accionar\nM - Pausa\nP - Ver Pista del Nivel\nF3 - Ver Coordenadas"
            Text(parent=self.menu_controles, text=texto_teclas, scale=1.3, origin=(0, 0), position=(0, 0.1), color=color.white, z=-2)
            Button(parent=self.menu_controles, text="VOLVER", scale=(0.2, 0.08), position=(0, -0.3), color=color.red, z=-2, on_click=self.ocultar_controles)
            self.menu_pausa = Entity(parent=camera.ui, enabled=False, z=-5)
            Entity(parent=self.menu_pausa, model='quad', color=color.rgba(0, 0, 0, 230), scale=(2, 1.5))
            Text(parent=self.menu_pausa, text="JUEGO PAUSADO", scale=3, origin=(0, 0), position=(0, 0.25), color=color.yellow, z=-6)
            self.slider_sens = Slider(parent=self.menu_pausa, min=10, max=100, default=40, dynamic=True, position=(-0.25, -0.05), scale=1.2, z=-6)
            self.slider_sens.on_value_changed = self.actualizar_sensibilidad

        def mostrar_controles(self): self.menu_controles.enabled = True
        def ocultar_controles(self): self.menu_controles.enabled = False

        def mostrar_pista(self):
            if self.manager.nivel_actual == 1:
                self.texto_detalle_pista.text = "Acertijo: Calcula la mitad de 10 y luego súmale 1.\nEse resultado es la hora exacta de escape.\n\nInstrucciones:\n1. Acércate a los 3 relojes de la pared.\n2. Presiona Clic Izquierdo sobre ellos hasta fijar esa hora.\n3. Abre la puerta para salir."
            elif self.manager.nivel_actual == 2:
                self.texto_detalle_pista.text = "¡El suelo no es seguro!\n\nInstrucciones:\n1. Realiza Parkour saltando de libro en libro.\n2. Llega hasta arriba y usa Clic Izquierdo\npara recoger la Tarjeta de acceso."
            elif self.manager.nivel_actual == 3:
                self.texto_detalle_pista.text = "Necesitas encontrar la salida escondida.\n\nInstrucciones:\n1. Revisa detenidamente sobre todos los escritorios.\n2. Al encontrar la Llave Maestra, salta sobre ella para agarrarla."
            elif self.manager.nivel_actual == 4:
                self.texto_detalle_pista.text = "Debes rescatar a los civiles atrapados.\n\nInstrucciones:\n1. Selecciona la Llave en tu inventario.\n2. Apunta directamente a la celda y usa Clic Izquierdo para lanzarla.\n3. Escapa por la puerta trasera."
            elif self.manager.nivel_actual == 5:
                self.texto_detalle_pista.text = "El Gran Sacrificio.\n\nInstrucciones:\n1. Equipa tu Tarjeta y lánzala al pasador de tarjeta.\n2. Deja que los civiles se vayan a la salida \n3. Deja que el monstruo te elimine, haciendo el sacrificio final para ganar."

            self.panel_pista.enabled = True
            self.manager.jugador.disable()
            mouse.locked = False
            mouse.visible = True

        def ocultar_pista(self):
            self.panel_pista.enabled = False
            if not self.manager.juego_pausado:
                self.manager.jugador.enable()
                mouse.locked = True
                mouse.visible = False

        def click_play(self):
            destroy(self.titulo)
            destroy(self.boton_play)
            destroy(self.boton_controles)
            destroy(self.menu_controles)
            destroy(self.fondo_menu)
            self.manager.iniciar_introduccion()

        def actualizar_sensibilidad(self):
            if self.manager.jugador:
                self.manager.jugador.mouse_sensitivity = Vec2(self.slider_sens.value, self.slider_sens.value)

        def alternar_pausa(self):
            self.manager.juego_pausado = not self.manager.juego_pausado
            if self.manager.juego_pausado:
                self.menu_pausa.enabled = True
                self.manager.jugador.disable()
                mouse.locked = False
                mouse.visible = True
                self.manager.musica_fondo.volume = 0
            else:
                self.menu_pausa.enabled = False
                self.manager.jugador.enable()
                mouse.locked = True
                mouse.visible = False
                self.manager.musica_fondo.volume = 0.4

    def __init__(self):
        self.cargando_nivel = False
        self.nivel_actual = 1
        self.juego_pausado = False
        self.tiempo_restante = 45 * 60
        self.intro_terminada = False
        self.game_over_activo = False
        self.nivel_completado = False
        self.vidas = 3
        self.checkpoint_pos = Vec3(0, 0, -8)
        self.musica_fondo = Audio('musica_juego.mp3', autoplay=False, loop=True, volume=0.4)
        self.audio_voz = Audio('voz_intro.mp3', autoplay=False, loop=False)
        self.mundo = Mundo()
        self.jugador = Jugador(self.checkpoint_pos)
        self.jugador.mundo = self.mundo 
        self.mundo.generar_enemigo(Vec3(0, 0, 5), self.jugador)
        self.ui = self.InterfazJuego(self)
        self.pantalla_intro = Entity(parent=camera.ui, model='quad', color=color.black, scale=(2, 2), z=-1, enabled=False)
        self.texto_intro = Text(text="Oficial, necesitamos que investigue\nla mansión Miller\npor casos de personas desaparecidas.", position=(0, 0), origin=(0, 0), scale=2, color=color.white, alpha=0, z=-2)
        self.video_intro = Entity(parent=camera.ui, model='quad', texture='CINEMATICA.mp4', color=color.white, scale=(2, 1.5), z=0, enabled=False)
        try:
            self.video_intro.texture._texture.setLoop(False)
        except:
            pass
        self.audio_video = Audio('CIUDAD.mp3', autoplay=False, loop=False)
        self.duracion_video = 6.0 
        invoke(self.audio_video.stop, delay=self.duracion_video)

    def iniciar_introduccion(self):
        self.pantalla_intro.enabled = True
        self.audio_voz.play()
        invoke(self.aparecer_texto_intro, delay=1.0)

    def aparecer_texto_intro(self):
        self.texto_intro.fade_in(duration=4.0)
        invoke(self.desaparecer_texto_intro, delay=5.0)

    def desaparecer_texto_intro(self):
        self.texto_intro.fade_out(duration=2.0)
        invoke(self.reproducir_video_intro, delay=2.5)

    def reproducir_video_intro(self):
        self.video_intro.enabled = True
        self.audio_video.play()
        self.pantalla_intro.fade_out(duration=1.0) 
        invoke(self.finalizar_intro, delay=self.duracion_video) 

    def finalizar_intro(self):
        self.pantalla_intro.fade_in(duration=1.0)
        invoke(self.iniciar_juego_real, delay=1.0)

    def iniciar_juego_real(self):
        self.intro_terminada = True
        self.jugador.enable()
        self.jugador.ui.activar()
        self.ui.cronometro_texto.enable()
        self.ui.texto_vida.enable()
        self.ui.texto_coordenadas.enable()
        self.ui.instruccion_pista.enable()
        self.musica_fondo.play()
        destroy(self.video_intro)
        self.pantalla_intro.fade_out(duration=2.5)

    def avanzar_nivel(self):
        if self.cargando_nivel:
            return
        self.cargando_nivel = True
        if self.nivel_actual == 1:
            self.iniciar_nivel_2()
        elif self.nivel_actual == 2:
            self.iniciar_nivel_3()
        elif self.nivel_actual == 3:
            self.iniciar_nivel_4()
        elif self.nivel_actual == 4: 
            self.iniciar_nivel_5()    
        invoke(self.liberar_carga, delay=1.5)

    def liberar_carga(self):
        self.cargando_nivel = False

    def iniciar_nivel_2(self):
        self.nivel_actual = 2
        self.nivel_completado = False
        self.ui.panel_victoria.enabled = False
        self.ui.texto_victoria.enabled = False
        self.ui.boton_siguiente.enabled = False
        self.checkpoint_pos = Vec3(0, 1, -5)
        offset_spawn = Vec3(0, 0.5, 0)
        self.jugador.position = self.checkpoint_pos + offset_spawn
        self.jugador.rotation = (0, 0, 0)
        self.jugador.camera_pivot.rotation_x = 0
        self.jugador.salud = 100
        self.jugador.tiempo_inmunidad = 2.0 
        self.mundo.cargar_nivel_2()
        self.jugador.enable()
        mouse.locked = True
        mouse.visible = False
        self.musica_fondo.play()

    def iniciar_nivel_3(self):
        self.nivel_actual = 3
        self.nivel_completado = False
        self.ui.panel_victoria.enabled = False
        self.ui.texto_victoria.enabled = False
        self.ui.boton_siguiente.enabled = False
        self.checkpoint_pos = Vec3(0, 3, 15)
        offset_spawn = Vec3(0, 0.5, 0)
        self.jugador.position = self.checkpoint_pos + offset_spawn
        self.jugador.rotation = (0, 0, 0)
        self.jugador.camera_pivot.rotation_x = 0
        self.jugador.salud = 100
        self.jugador.tiempo_inmunidad = 2.0 
        self.mundo.cargar_nivel_3()
        self.jugador.enable()
        mouse.locked = True
        mouse.visible = False
        self.musica_fondo.play()

    def iniciar_nivel_4(self):
        self.nivel_actual = 4
        self.nivel_completado = False
        self.ui.panel_victoria.enabled = False
        self.ui.texto_victoria.enabled = False
        self.ui.boton_siguiente.enabled = False
        self.checkpoint_pos = Vec3(0, 1, 0)
        offset_spawn = Vec3(0, 0.5, 0)
        self.jugador.position = self.checkpoint_pos + offset_spawn
        self.jugador.rotation = (0, 0, 0)
        self.jugador.camera_pivot.rotation_x = 0
        self.jugador.salud = 100
        self.jugador.tiempo_inmunidad = 2.0
        self.mundo.civiles_liberados = False
        self.mundo.cargar_nivel_4()
        self.jugador.enable()
        mouse.locked = True
        mouse.visible = False
        self.musica_fondo.play()
        self.jugador.ui.guardar_objeto('Llave')

    def iniciar_nivel_5(self):
        self.nivel_actual = 5
        self.nivel_completado = False
        self.ui.panel_victoria.enabled = False
        self.ui.texto_victoria.enabled = False
        self.ui.boton_siguiente.enabled = False
        self.checkpoint_pos = Vec3(0, 1, 0)
        self.jugador.position = self.checkpoint_pos + Vec3(0, 0.5, 0)
        self.jugador.rotation = (0, 0, 0)
        self.jugador.camera_pivot.rotation_x = 0
        self.jugador.salud = 100
        self.mundo.tarjeta_pasada = False
        self.mundo.jefe_generado = False
        self.mundo.cargar_nivel_5() 
        self.mundo.civiles_liberados = False  
        self.mundo.tarjeta_pasada = False
        self.mundo.jefe_generado = False
        self.jugador.enable()
        mouse.locked = True
        mouse.visible = False
        self.musica_fondo.play()
        self.jugador.ui.guardar_objeto('Tarjeta')

    def actualizar_logica(self):
        if self.game_over_activo or self.nivel_completado or self.juego_pausado:
            return  
        if self.tiempo_restante > 0:
            self.tiempo_restante -= time.dt
            minutos = int(self.tiempo_restante // 60)
            segundos = int(self.tiempo_restante % 60)
            self.ui.cronometro_texto.text = f"{minutos:02d}:{segundos:02d}"
            if self.tiempo_restante <= 0:
                self.desencadenar_game_over()
                return
        if self.jugador.salud <= 0 and self.nivel_actual != 5:
            self.desencadenar_game_over()
            return
        if self.jugador and self.jugador.enabled:
            x, y, z = self.jugador.position
            rot = self.jugador.rotation_y % 360
            self.ui.texto_coordenadas.text = f"X: {x:.1f} | Y: {y:.1f} | Z: {z:.1f} | Rot: {rot:.0f}°"
            if self.jugador.y < -4:
                self.jugador.position = self.checkpoint_pos
                self.jugador.recibir_dano(10)
                self.jugador.tiempo_inmunidad = 1.5
        self.ui.texto_vida.text = f'Vidas: {self.vidas} | Salud: {self.jugador.salud}'
        self.ui.texto_vida.color = color.red if self.jugador.salud <= 40 else color.green
        if self.nivel_actual == 1:
            if self.mundo.todos_relojes_en_hora() and self.mundo.puerta_salida.intersects(self.jugador).hit:
                self.nivel_completado = True
                self.jugador.disable()
                self.musica_fondo.stop()
                mouse.locked = False
                mouse.visible = True
                self.ui.panel_victoria.enabled = True
                self.ui.texto_victoria.enabled = True
                self.ui.texto_victoria.text = "Has completado el Nivel 1"
                self.ui.boton_siguiente.enabled = True 
        elif self.nivel_actual == 2:
            ha_tocado_tarjeta = False
            if hasattr(self.mundo, 'tarjeta') and self.mundo.tarjeta:
                try: 
                    ha_tocado_tarjeta = self.mundo.tarjeta.intersects(self.jugador).hit
                except: pass 
            ha_agarrado_tarjeta = self.jugador.ui.slot1 == 'Tarjeta'
            if ha_tocado_tarjeta or ha_agarrado_tarjeta:
                self.nivel_completado = True
                self.jugador.disable()
                self.musica_fondo.stop()
                mouse.locked = False
                mouse.visible = True
                self.ui.panel_victoria.enabled = True
                self.ui.texto_victoria.enabled = True
                self.ui.texto_victoria.text = "¡Has conseguido la tarjeta!\nNivel 2 Completado"
                self.ui.boton_siguiente.enabled = True
        elif self.nivel_actual == 3:
            ha_tocado_llave = False
            if hasattr(self.mundo, 'llave') and self.mundo.llave:
                try: 
                    ha_tocado_llave = self.mundo.llave.intersects(self.jugador).hit
                except: pass
            ha_agarrado_llave = self.jugador.ui.slot1 == 'Llave'
            if ha_tocado_llave or ha_agarrado_llave:
                self.nivel_completado = True
                self.jugador.disable()
                self.musica_fondo.stop()
                mouse.locked = False
                mouse.visible = True
                self.ui.panel_victoria.enabled = True
                self.ui.texto_victoria.enabled = True
                self.ui.texto_victoria.text = "¡Has encontrado la Llave Maestra!\nNivel 3 Completado"
                self.ui.boton_siguiente.enabled = True 
        elif self.nivel_actual == 4:
            if not self.mundo.civiles_liberados and self.mundo.celda:
                llave_encontrada = None
                for entidad in list(scene.entities):
                    try:
                        if entidad and hasattr(entidad, 'model') and entidad.model:
                            nombre_modelo = str(entidad.model.name).lower()
                            if 'llave' in nombre_modelo and entidad.parent != camera.ui:
                                llave_encontrada = entidad
                                break
                    except Exception:
                        continue
                if not llave_encontrada and self.mundo.llave_lanzada_ref:
                    llave_encontrada = self.mundo.llave_lanzada_ref
                if llave_encontrada:
                    try:
                        distancia_2d = Vec2(llave_encontrada.x - self.mundo.celda.x, llave_encontrada.z - self.mundo.celda.z).length()
                        if distancia_2d < 25.0:
                            print("¡Llave detectada cerca de la celda! Liberando civiles...")
                            destroy(llave_encontrada)
                            self.mundo.llave_lanzada_ref = None
                            destroy(self.mundo.celda) 
                            self.mundo.celda = None
                            self.mundo.civiles_liberados = True
                    except Exception:
                        pass
            if self.mundo.civiles_liberados:
                vel_civiles = 4.5 * time.dt
                civiles = [self.mundo.humano1, self.mundo.humano2, self.mundo.humano3]
                offsets = [
                    self.jugador.back * 3.5 + self.jugador.left * 1.5,
                    self.jugador.back * 6.0,
                    self.jugador.back * 8.5 + self.jugador.right * 1.5
                ]
                for i, civil in enumerate(civiles):
                    if civil and hasattr(civil, 'position'):
                        punto_objetivo = self.jugador.position + offsets[i]
                        punto_objetivo.y = civil.y 
                        dist_al_puesto = distance(civil.position, punto_objetivo)
                        if dist_al_puesto > 1.0:
                            civil.look_at(Vec3(punto_objetivo.x, civil.y, punto_objetivo.z))
                            civil.position += civil.forward * vel_civiles
                        else:
                            civil.rotation_y = self.jugador.rotation_y          
            if getattr(self.mundo, 'puerta_salida_n4', None):
                try:
                    if self.mundo.puerta_salida_n4.intersects(self.jugador).hit:
                        if self.mundo.civiles_liberados:
                            self.nivel_completado = True
                            self.jugador.disable()
                            self.musica_fondo.stop()
                            mouse.locked = False
                            mouse.visible = True
                            self.ui.panel_victoria.enabled = True
                            self.ui.texto_victoria.enabled = True
                            self.ui.texto_victoria.text = "¡Has rescatado a los civiles!\nNivel 4 Completado"
                            self.ui.boton_siguiente.enabled = True
                except:
                    pass
        elif self.nivel_actual == 5:
            if self.jugador.salud <= 0:
                self.nivel_completado = True
                self.jugador.disable()
                self.musica_fondo.stop()
                mouse.locked = False
                mouse.visible = True
                self.ui.panel_victoria.enabled = True
                self.ui.texto_victoria.enabled = True
                self.ui.texto_victoria.text = "FIN DEL JUEGO\nTu sacrificio permitió que los civiles escaparan."
                self.ui.boton_siguiente.enabled = False
                return
            if not getattr(self.mundo, 'tarjeta_pasada', False):
                tarjeta_lanzada = None
                for entidad in list(scene.entities):
                    try:
                        if entidad and entidad.parent != camera.ui:
                            nombre_entidad = str(getattr(entidad, 'name', '')).lower()
                            nombre_modelo = str(getattr(entidad.model, 'name', '')).lower() if hasattr(entidad, 'model') and entidad.model else ''
                            if 'tarjeta' in nombre_entidad or 'tarjeta' in nombre_modelo:
                                tarjeta_lanzada = entidad
                                break
                    except Exception:
                        continue
                if not tarjeta_lanzada and getattr(self.mundo, 'tarjeta_lanzada_ref', None):
                    tarjeta_lanzada = self.mundo.tarjeta_lanzada_ref
                if tarjeta_lanzada and getattr(self.mundo, 'pasador', None):
                    try:
                        dist_2d = Vec2(tarjeta_lanzada.x - self.mundo.pasador.x, tarjeta_lanzada.z - self.mundo.pasador.z).length()
                        if dist_2d < 12.0:  
                            print("¡ÉXITO! Tarjeta validada. Liberando civiles y abriendo portón...")
                            self.mundo.tarjeta_pasada = True
                            destroy(tarjeta_lanzada)
                            self.mundo.tarjeta_lanzada_ref = None
                            if getattr(self.mundo, 'porton_garage', None):
                                destroy(self.mundo.porton_garage)
                                self.mundo.porton_garage = None
                    except Exception:
                        pass
            civiles = [getattr(self.mundo, 'humano1', None), getattr(self.mundo, 'humano2', None), getattr(self.mundo, 'humano3', None)]
            civiles = [c for c in civiles if c is not None and hasattr(c, 'position')]
            if not getattr(self.mundo, 'tarjeta_pasada', False):
                vel_civiles = 4.5 * time.dt
                offsets = [
                    self.jugador.back * 3.5 + self.jugador.left * 1.5,
                    self.jugador.back * 6.0,
                    self.jugador.back * 8.5 + self.jugador.right * 1.5
                ]
                for i, civil in enumerate(civiles):
                    punto_objetivo = self.jugador.position + offsets[i]
                    punto_objetivo.y = civil.y 
                    dist_al_puesto = distance(civil.position, punto_objetivo)
                    if dist_al_puesto > 1.0:
                        civil.look_at(Vec3(punto_objetivo.x, civil.y, punto_objetivo.z))
                        civil.position += civil.forward * vel_civiles
                    else:
                        civil.rotation_y = self.jugador.rotation_y
            else:
                todos_escaparon = True
                vel_civiles = 8.0 * time.dt
                for civil in civiles:
                    if civil.enabled and civil.visible:
                        punto_escape = Vec3(0, civil.y, 45) 
                        dist = distance(civil.position, punto_escape)
                        if dist > 2.5:
                            civil.look_at(Vec3(punto_escape.x, civil.y, punto_escape.z))
                            civil.position += civil.forward * vel_civiles
                            todos_escaparon = False
                        else:
                            civil.visible = False
                            civil.enabled = False
                            civil.position = Vec3(0, 100, 0)
                if todos_escaparon and not getattr(self.mundo, 'jefe_generado', False):
                    print("¡TODOS ESCAPARON! Aparece el Jefe Final...")
                    self.mundo.jefe_generado = True
                    self.mundo.enemigo = self.mundo.Enemigo(posicion=Vec3(0, 2, 30), modelo="ene_final.gltf", jugador_ref=self.jugador)
                    self.mundo.enemigo.scale = 2.0    
                    self.mundo.enemigo.dano = 100     
                    self.mundo.enemigo.velocidad = 5.5

    def desencadenar_game_over(self):
        if self.tiempo_restante <= 0:
            self.ui.cronometro_texto.text = "00:00"
            self.ui.cronometro_texto.color = color.red
        self.game_over_activo = True
        self.jugador.disable()
        mouse.locked = False
        mouse.visible = True
        self.musica_fondo.stop()
        self.ui.fondo_game_over.enabled = True
        self.ui.texto_game_over.enabled = True
        if self.vidas > 1:
            self.ui.texto_game_over.text = f"GAME OVER\n¿Quieres intentar de vuelta?\n(Te quedarán {self.vidas - 1} vidas)"
            self.ui.boton_si.enabled = True
            self.ui.boton_no.enabled = True
        else:
            self.ui.texto_game_over.text = "GAME OVER\nTe has quedado sin vidas."
            self.ui.boton_si.enabled = False
            self.ui.boton_no.enabled = False

    def reiniciar_nivel(self):
        self.vidas -= 1
        self.jugador.salud = 100
        offset_spawn = Vec3(0, 0.5, 0)
        self.jugador.position = self.checkpoint_pos + offset_spawn
        self.jugador.rotation = (0, 0, 0)
        self.jugador.camera_pivot.rotation_x = 0
        self.jugador.tiempo_inmunidad = 2.0 
        if self.tiempo_restante <= 0:
            self.tiempo_restante = 45 * 60
        if self.nivel_actual == 1:
            if getattr(self.mundo, 'enemigo', None):
                destroy(self.mundo.enemigo)
            self.mundo.generar_enemigo(Vec3(0, 0, 5), self.jugador)
            for r in self.mundo.relojes:
                r.hora_actual = 12
                r.pantalla.text = "12:00"
                r.pantalla.color = color.red
        self.ui.fondo_game_over.enabled = False
        self.ui.texto_game_over.enabled = False
        self.ui.boton_si.enabled = False
        self.ui.boton_no.enabled = False
        self.jugador.enable()
        mouse.locked = True
        mouse.visible = False
        self.game_over_activo = False
        self.juego_pausado = False
        self.musica_fondo.play()

juego = AdministradorJuego()

def input(key):
    if key == 'm' and juego.intro_terminada and not juego.game_over_activo and not juego.nivel_completado:
        if not juego.ui.panel_pista.enabled:
            juego.ui.alternar_pausa()
    if key == 'p' and juego.intro_terminada and not juego.game_over_activo and not juego.nivel_completado:
        if juego.ui.panel_pista.enabled:
            juego.ui.ocultar_pista()
        elif not juego.juego_pausado:
            juego.ui.mostrar_pista()
    if key == 'f3' and juego.intro_terminada:
        juego.ui.texto_coordenadas.enabled = not juego.ui.texto_coordenadas.enabled

def update():
    juego.actualizar_logica()

app.run()