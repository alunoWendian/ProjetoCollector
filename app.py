import pygame
import random
import math
import sys

# --- CONFIGURAÇÕES GERAIS ---
LARGURA, ALTURA = 900, 650
FPS = 60

# Paleta de Cores
COR_FUNDO = (22, 22, 26)
COR_CHAO = (38, 36, 40)
COR_GRADE = (95, 52, 54)          # Vermelho menos saturado e discreto
COR_BORDA_MAPA = (130, 68, 70)
COR_SOMBRA = (18, 18, 22)
COR_JOGADOR = (255, 204, 0)       # Amarelo estilo Pac-Man
COR_JOGADOR_BORDA = (200, 150, 0)
COR_CRISTAL = (0, 229, 255)       # Ciano brilhante
COR_CRISTAL_BRILHO = (200, 255, 255)
COR_WALL_KICK = (80, 240, 255)    # Ciano elétrico (Wall Kick)
COR_SLIDE = (255, 135, 50)        # Laranja vibrante (Slide)
COR_TEXTO = (240, 240, 240)

# Cores das Paredes Internas (Maze Mode)
COR_PAREDE_TOPO = (115, 62, 66)
COR_PAREDE_FRENTE = (78, 40, 44)
COR_PAREDE_BORDA = (155, 82, 86)

# Cores das Cartas de Modificadores (Desafios)
COR_CARTA_FUNDO = (34, 32, 42)
COR_CARTA_HOVER = (52, 42, 56)
COR_CARTA_BORDA = (110, 75, 85)
COR_CARTA_BORDA_HOVER = (255, 185, 70)

# Cores das Cartas de Perigo (Únicas)
COR_PERIGO_FUNDO = (46, 24, 28)
COR_PERIGO_HOVER = (70, 30, 36)
COR_PERIGO_BORDA = (190, 55, 65)
COR_PERIGO_BORDA_HOVER = (255, 65, 75)

# Fator de inclinação da câmera
INCLINACAO_Y = 0.65


class ConfigPartida:
    """Guarda os parâmetros dinâmicos da run afetados pelos modificadores e perigos."""
    def __init__(self):
        self.mapa_largura = 1800
        self.mapa_profundidade = 1800
        self.qtd_cristais = 25

        # Controle dos modificadores escolhidos
        self.stacks_mais = 0
        self.stacks_espacoso = 0
        self.stacks_lerdo = 0
        self.max_stacks_lerdo = 3
        self.stacks_maze = 0

        # Controle dos Perigos únicos ativos
        self.perigo_aernis_ativo = False


class Camera:
    def __init__(self, config):
        self.x = 0.0
        self.y = config.mapa_profundidade / 2

    def centralizar(self, config):
        self.x = 0.0
        self.y = config.mapa_profundidade / 2

    def atualizar(self, alvo_x, alvo_y):
        suavizacao = 0.12
        self.x += (alvo_x - self.x) * suavizacao
        self.y += (alvo_y - self.y) * suavizacao


def mundo_para_tela(x, y, z, camera):
    """Converte coordenadas 3D do mundo (X, Y, Z) para coordenadas 2D da tela relativas à câmera."""
    tela_x = (LARGURA // 2) + (x - camera.x)
    tela_y = (ALTURA // 2) + ((y - camera.y) * INCLINACAO_Y) - z
    return int(tela_x), int(tela_y)


class Parede:
    """Representa uma parede interna fina gerada pelo modificador Maze Mode."""
    def __init__(self, x, y, largura, profundidade, altura_z=46):
        self.x = x
        self.y = y
        self.largura = largura
        self.profundidade = profundidade
        self.altura_z = altura_z

    @property
    def min_x(self):
        return self.x - self.largura / 2

    @property
    def max_x(self):
        return self.x + self.largura / 2

    @property
    def min_y(self):
        return self.y - self.profundidade / 2

    @property
    def max_y(self):
        return self.y + self.profundidade / 2

    @property
    def sort_y(self):
        return self.max_y

    def desenhar_sombra(self, superficie, camera):
        p1 = mundo_para_tela(self.min_x - 4, self.min_y - 4, 0, camera)
        p2 = mundo_para_tela(self.max_x + 4, self.min_y - 4, 0, camera)
        p3 = mundo_para_tela(self.max_x + 4, self.max_y + 4, 0, camera)
        p4 = mundo_para_tela(self.min_x - 4, self.max_y + 4, 0, camera)
        pygame.draw.polygon(superficie, COR_SOMBRA, [p1, p2, p3, p4])

    def desenhar(self, superficie, camera):
        f1 = mundo_para_tela(self.min_x, self.max_y, self.altura_z, camera)
        f2 = mundo_para_tela(self.max_x, self.max_y, self.altura_z, camera)
        f3 = mundo_para_tela(self.max_x, self.max_y, 0, camera)
        f4 = mundo_para_tela(self.min_x, self.max_y, 0, camera)
        pygame.draw.polygon(superficie, COR_PAREDE_FRENTE, [f1, f2, f3, f4])
        pygame.draw.polygon(superficie, COR_PAREDE_BORDA, [f1, f2, f3, f4], 1)

        t1 = mundo_para_tela(self.min_x, self.min_y, self.altura_z, camera)
        t2 = mundo_para_tela(self.max_x, self.min_y, self.altura_z, camera)
        t3 = mundo_para_tela(self.max_x, self.max_y, self.altura_z, camera)
        t4 = mundo_para_tela(self.min_x, self.max_y, self.altura_z, camera)
        pygame.draw.polygon(superficie, COR_PAREDE_TOPO, [t1, t2, t3, t4])
        pygame.draw.polygon(superficie, COR_PAREDE_BORDA, [t1, t2, t3, t4], 2)


class Aernis03:
    """Inimigo 'Zé do Picadinho': Máquina achatada laranja com núcleo preto, olhos de raiva e serra inferior."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0.0
        self.raio = 25          # Um pouco maior que o jogador (raio 18)
        self.altura_hitbox = 28 # Mais baixa por ser achatada (permite pular por cima)

        # Movimento estilo Logo de DVD
        velocidade = 5.4
        angulo = random.choice([
            math.pi * 0.25, math.pi * 0.75,
            math.pi * 1.25, math.pi * 1.75
        ]) + random.uniform(-0.15, 0.15)
        self.vx = math.cos(angulo) * velocidade
        self.vy = math.sin(angulo) * velocidade

        self.angulo_serra = 0.0
        self.fumaca = []
        self.timer_fumaca = 0.0

    @property
    def sort_y(self):
        return self.y

    def atualizar(self, config, paredes, dt):
        self.angulo_serra += dt * 18.0

        # Emissão de fumaça do chassi defeituoso
        self.timer_fumaca += dt
        if self.timer_fumaca >= 0.06:
            self.timer_fumaca = 0.0
            self.fumaca.append({
                "x": self.x + random.uniform(-10, 10),
                "y": self.y + random.uniform(-6, 6),
                "z": 24.0,
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-0.4, 0.4),
                "vz": random.uniform(1.1, 1.8),
                "vida": 0.75,
                "max_vida": 0.75,
                "raio": random.randint(5, 9)
            })

        for p in self.fumaca[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["z"] += p["vz"]
            p["vida"] -= dt
            if p["vida"] <= 0:
                self.fumaca.remove(p)

        # Movimento no Eixo X + quicada
        self.x += self.vx
        limite_x = (config.mapa_largura / 2) - self.raio
        if self.x <= -limite_x:
            self.x = -limite_x
            self.vx = abs(self.vx)
        elif self.x >= limite_x:
            self.x = limite_x
            self.vx = -abs(self.vx)

        for parede in paredes:
            mais_prox_x = max(parede.min_x, min(self.x, parede.max_x))
            mais_prox_y = max(parede.min_y, min(self.y, parede.max_y))
            dx = self.x - mais_prox_x
            dy = self.y - mais_prox_y
            dist_sq = dx * dx + dy * dy
            if dist_sq < self.raio * self.raio:
                dist = math.sqrt(dist_sq)
                if dist > 0.0001:
                    sobreposicao = self.raio - dist
                    self.x += (dx / dist) * sobreposicao
                self.vx = -self.vx
                break

        # Movimento no Eixo Y + quicada
        self.y += self.vy
        if self.y <= self.raio:
            self.y = self.raio
            self.vy = abs(self.vy)
        elif self.y >= config.mapa_profundidade - self.raio:
            self.y = config.mapa_profundidade - self.raio
            self.vy = -abs(self.vy)

        for parede in paredes:
            mais_prox_x = max(parede.min_x, min(self.x, parede.max_x))
            mais_prox_y = max(parede.min_y, min(self.y, parede.max_y))
            dx = self.x - mais_prox_x
            dy = self.y - mais_prox_y
            dist_sq = dx * dx + dy * dy
            if dist_sq < self.raio * self.raio:
                dist = math.sqrt(dist_sq)
                if dist > 0.0001:
                    sobreposicao = self.raio - dist
                    self.y += (dy / dist) * sobreposicao
                self.vy = -self.vy
                break

    def colidiu_com_jogador(self, jogador):
        if jogador.z > self.altura_hitbox:
            return False
        dist_xy = math.hypot(jogador.x - self.x, jogador.y - self.y)
        return dist_xy < (jogador.raio + self.raio - 4)

    def desenhar_sombra(self, superficie, camera):
        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        largura_sombra = int(self.raio * 2.5)
        altura_sombra = int(self.raio * 2.1 * INCLINACAO_Y)
        rect_sombra = pygame.Rect(
            sx - largura_sombra // 2,
            sy - altura_sombra // 2,
            largura_sombra,
            altura_sombra
        )
        pygame.draw.ellipse(superficie, COR_SOMBRA, rect_sombra)

    def desenhar(self, superficie, camera):
        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)

        # 1. Serra giratória bem rente ao chão (embaixo da máquina achatada)
        centro_serra = (tx, ty - 3)
        raio_serra_ext = self.raio + 7
        raio_serra_int = self.raio - 1
        num_dentes = 12
        pontos_serra = []
        for i in range(num_dentes * 2):
            ang = self.angulo_serra + (i * math.pi / num_dentes)
            r = raio_serra_ext if i % 2 == 0 else raio_serra_int
            px = centro_serra[0] + math.cos(ang) * r
            py = centro_serra[1] + math.sin(ang) * r * (INCLINACAO_Y * 0.85)
            pontos_serra.append((px, py))

        pygame.draw.polygon(superficie, (180, 190, 200), pontos_serra)
        pygame.draw.polygon(superficie, (70, 75, 85), pontos_serra, 2)

        # 2. Chassi Achatado Laranja (largo e baixo, cobrindo a base da serra)
        largura_chassi = 56
        altura_chassi = 22
        rect_chassi = pygame.Rect(
            tx - largura_chassi // 2,
            ty - altura_chassi - 3,
            largura_chassi,
            altura_chassi
        )
        pygame.draw.rect(superficie, (242, 112, 20), rect_chassi, border_radius=8)
        pygame.draw.rect(superficie, (185, 75, 10), rect_chassi, 2, border_radius=8)

        # Tampa/teto achatado laranja mais claro para dar volume 2.5D
        rect_teto = pygame.Rect(tx - 22, ty - altura_chassi - 5, 44, 9)
        pygame.draw.ellipse(superficie, (255, 138, 42), rect_teto)

        # 3. Detalhes Pretos no Meio da Máquina
        rect_meio_preto = pygame.Rect(tx - 15, ty - altura_chassi - 2, 30, altura_chassi - 2)
        pygame.draw.rect(superficie, (24, 24, 28), rect_meio_preto, border_radius=4)

        # Grades / fendas no bloco preto central
        pygame.draw.line(superficie, (50, 50, 56), (tx - 10, ty - 8), (tx + 10, ty - 8), 2)

        # 4. Olhos Vermelhos de Raiva (sem brilho branco) dentro do painel preto
        olhar_x = int((self.vx / 5.5) * 3)
        olhar_y = int((self.vy / 5.5) * 1.5)
        ox = tx + olhar_x
        oy = ty - 16 + olhar_y

        olho_esq = [
            (ox - 11, oy - 3),
            (ox - 3, oy),
            (ox - 4, oy + 4),
            (ox - 11, oy + 2)
        ]
        olho_dir = [
            (ox + 11, oy - 3),
            (ox + 3, oy),
            (ox + 4, oy + 4),
            (ox + 11, oy + 2)
        ]
        pygame.draw.polygon(superficie, (245, 22, 32), olho_esq)
        pygame.draw.polygon(superficie, (245, 22, 32), olho_dir)

        # 5. Fumaça escura subindo do topo (defeito)
        for p in self.fumaca:
            fx, fy = mundo_para_tela(p["x"], p["y"], p["z"], camera)
            proporcao = p["vida"] / p["max_vida"]
            raio_f = max(2, int(p["raio"] * (1.3 - 0.5 * proporcao)))
            tom = int(55 + 40 * (1.0 - proporcao))
            pygame.draw.circle(superficie, (tom, tom, tom + 5), (fx, fy), raio_f)


class Jogador:
    def __init__(self, config):
        self.raio = 18

        self.vel_min = 4.0
        self.ganho_embalo_base = 6.5
        self.fator_embalo_mod = 1.0

        self.aceleracao = 0.09
        self.desaceleracao = 0.35

        self.forca_pulo = 10.5
        self.gravidade = 0.55
        self.espaco_pressionado_antes = False
        self.duracao_boost_wk = 0.95
        self.bonus_vel_wk = 7.5

        self.shift_pressionado_antes = False

        self.resetar_para_centro(config)

    def resetar_para_centro(self, config):
        self.x = 0.0
        self.y = config.mapa_profundidade / 2
        self.z = 0.0

        self.velocidade_atual = 0.0
        self.dir_x = 0.0
        self.dir_y = 0.0
        self.rastro = []

        self.vel_z = 0.0
        self.no_chao = True
        self.pode_wall_kick = True
        self.perto_parede_no_ar = False
        self.timer_boost_wk = 0.0

        self.timer_slide = 0.0
        self.cooldown_slide = 0.0
        self.bonus_vel_slide_atual = 0.0
        self.slide_foi_no_ar = False

    @property
    def vel_max(self):
        return self.vel_min + (self.ganho_embalo_base * self.fator_embalo_mod)

    @property
    def boost_wk_ativo(self):
        return self.timer_boost_wk > 0.0

    @property
    def slide_ativo(self):
        return self.timer_slide > 0.0

    def resolver_colisao_paredes(self, paredes):
        bateu = False
        for parede in paredes:
            mais_prox_x = max(parede.min_x, min(self.x, parede.max_x))
            mais_prox_y = max(parede.min_y, min(self.y, parede.max_y))

            dist_x = self.x - mais_prox_x
            dist_y = self.y - mais_prox_y
            dist_sq = dist_x ** 2 + dist_y ** 2

            if dist_sq < self.raio ** 2:
                bateu = True
                dist = math.sqrt(dist_sq)
                if dist > 0.0001:
                    sobreposicao = self.raio - dist
                    self.x += (dist_x / dist) * sobreposicao
                    self.y += (dist_y / dist) * sobreposicao
                else:
                    self.y = parede.max_y + self.raio
        return bateu

    def detectar_normal_parede(self, config, paredes):
        margem_wk = 14.0
        limite_x = (config.mapa_largura / 2) - self.raio
        nx, ny = 0.0, 0.0

        if self.x <= -limite_x + margem_wk:
            nx += 1.0
        elif self.x >= limite_x - margem_wk:
            nx -= 1.0

        if self.y <= self.raio + margem_wk:
            ny += 1.0
        elif self.y >= config.mapa_profundidade - self.raio - margem_wk:
            ny -= 1.0

        raio_deteccao = self.raio + margem_wk
        for parede in paredes:
            mais_prox_x = max(parede.min_x, min(self.x, parede.max_x))
            mais_prox_y = max(parede.min_y, min(self.y, parede.max_y))
            dx = self.x - mais_prox_x
            dy = self.y - mais_prox_y
            dist = math.hypot(dx, dy)
            if dist <= raio_deteccao:
                if dist > 0.0001:
                    nx += dx / dist
                    ny += dy / dist
                else:
                    ny += 1.0

        if nx != 0.0 or ny != 0.0:
            comp = math.hypot(nx, ny)
            return nx / comp, ny / comp
        return None

    def atualizar(self, teclas, config, paredes, dt):
        dx, dy = 0.0, 0.0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx -= 1.0
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx += 1.0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy -= 1.0
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy += 1.0

        if self.timer_boost_wk > 0.0:
            self.timer_boost_wk = max(0.0, self.timer_boost_wk - dt)
        if self.timer_slide > 0.0:
            self.timer_slide = max(0.0, self.timer_slide - dt)
        if self.cooldown_slide > 0.0:
            self.cooldown_slide = max(0.0, self.cooldown_slide - dt)

        shift_agora = (
            teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT] or
            teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]
        )
        apertou_slide = shift_agora and not self.shift_pressionado_antes
        self.shift_pressionado_antes = shift_agora

        if apertou_slide and self.cooldown_slide <= 0.0:
            if dx != 0.0 or dy != 0.0:
                comp = math.hypot(dx, dy)
                self.dir_x = dx / comp
                self.dir_y = dy / comp
            elif self.dir_x == 0.0 and self.dir_y == 0.0:
                self.dir_y = 1.0

            if self.no_chao:
                self.slide_foi_no_ar = False
                self.timer_slide = 0.45
                self.bonus_vel_slide_atual = 4.2
                self.cooldown_slide = 0.70
            else:
                self.slide_foi_no_ar = True
                self.timer_slide = 0.65
                self.bonus_vel_slide_atual = 6.2
                self.vel_z = max(self.vel_z, 3.2)
                self.cooldown_slide = 0.85

            self.velocidade_atual = max(self.velocidade_atual, self.vel_max + self.bonus_vel_slide_atual)

        bonus_wk = self.bonus_vel_wk * (self.timer_boost_wk / self.duracao_boost_wk) if self.boost_wk_ativo else 0.0
        duracao_ref_slide = 0.65 if self.slide_foi_no_ar else 0.45
        bonus_sl = self.bonus_vel_slide_atual * (self.timer_slide / duracao_ref_slide) if self.slide_ativo else 0.0
        vel_max_atual = self.vel_max + max(bonus_wk, bonus_sl)

        if dx != 0 or dy != 0:
            comprimento = math.hypot(dx, dy)
            dx /= comprimento
            dy /= comprimento

            if self.velocidade_atual < self.vel_min:
                self.velocidade_atual = self.vel_min
            else:
                alinhamento = (self.dir_x * dx) + (self.dir_y * dy)

                if alinhamento > 0.95:
                    self.velocidade_atual = min(vel_max_atual, self.velocidade_atual + self.aceleracao)
                elif alinhamento >= 0.65:
                    excesso = self.velocidade_atual - self.vel_min
                    self.velocidade_atual = self.vel_min + (excesso * 0.88)
                elif alinhamento >= -0.1:
                    excesso = self.velocidade_atual - self.vel_min
                    self.velocidade_atual = self.vel_min + (excesso * 0.60)
                else:
                    if not (self.boost_wk_ativo or self.slide_ativo):
                        self.velocidade_atual = self.vel_min

            self.dir_x = dx
            self.dir_y = dy
        else:
            if not (self.boost_wk_ativo or self.slide_ativo):
                self.velocidade_atual = max(0.0, self.velocidade_atual - self.desaceleracao)

        if self.velocidade_atual > vel_max_atual:
            taxa_queda = 0.65 if (not self.boost_wk_ativo and not self.slide_foi_no_ar) else 0.35
            self.velocidade_atual = max(vel_max_atual, self.velocidade_atual - taxa_queda)

        self.x += self.dir_x * self.velocidade_atual
        self.y += self.dir_y * self.velocidade_atual

        limite_x = (config.mapa_largura / 2) - self.raio
        bateu_parede = False

        if self.x < -limite_x:
            self.x = -limite_x
            bateu_parede = True
        elif self.x > limite_x:
            self.x = limite_x
            bateu_parede = True

        if self.y < self.raio:
            self.y = self.raio
            bateu_parede = True
        elif self.y > config.mapa_profundidade - self.raio:
            self.y = config.mapa_profundidade - self.raio
            bateu_parede = True

        if self.resolver_colisao_paredes(paredes):
            bateu_parede = True

        if bateu_parede and self.no_chao and not (self.boost_wk_ativo or self.slide_ativo):
            self.velocidade_atual = min(self.velocidade_atual, self.vel_min)

        espaco_agora = teclas[pygame.K_SPACE]
        apertou_espaco = espaco_agora and not self.espaco_pressionado_antes
        self.espaco_pressionado_antes = espaco_agora

        normal_parede = self.detectar_normal_parede(config, paredes)
        self.perto_parede_no_ar = (not self.no_chao) and self.pode_wall_kick and (normal_parede is not None)

        if apertou_espaco:
            if self.no_chao:
                self.vel_z = self.forca_pulo
                self.no_chao = False
                self.pode_wall_kick = True
            elif self.perto_parede_no_ar:
                nx, ny = normal_parede
                self.vel_z = self.forca_pulo * 1.05
                self.pode_wall_kick = False

                rebote_x = nx * 1.4 + dx * 0.8
                rebote_y = ny * 1.4 + dy * 0.8
                comp_rebote = math.hypot(rebote_x, rebote_y)
                if comp_rebote > 0:
                    self.dir_x = rebote_x / comp_rebote
                    self.dir_y = rebote_y / comp_rebote

                self.timer_boost_wk = self.duracao_boost_wk
                self.velocidade_atual = self.vel_max + self.bonus_vel_wk

        self.z += self.vel_z
        if not self.no_chao:
            self.vel_z -= self.gravidade

        if self.z <= 0:
            self.z = 0
            self.vel_z = 0
            self.no_chao = True
            self.pode_wall_kick = True

        faixa_embalo = self.vel_max - self.vel_min
        fator_embalo = max(0.0, (self.velocidade_atual - self.vel_min) / faixa_embalo) if faixa_embalo > 0 else 0.0

        tipo_rastro = "NORMAL"
        if self.boost_wk_ativo:
            tipo_rastro = "WK"
        elif self.slide_ativo:
            tipo_rastro = "SLIDE"

        if fator_embalo > 0.35 or tipo_rastro != "NORMAL":
            self.rastro.append((self.x, self.y, self.z, min(1.0, fator_embalo), tipo_rastro))
        if len(self.rastro) > 10:
            self.rastro.pop(0)
        elif fator_embalo <= 0.35 and tipo_rastro == "NORMAL" and self.rastro:
            self.rastro.pop(0)

    def desenhar_sombra(self, superficie, camera):
        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        escala = max(0.4, 1.0 - (self.z / 180.0))
        fator_slide = 1.25 if (self.slide_ativo and self.no_chao) else 1.0
        largura_sombra = int(self.raio * 2 * escala * fator_slide)
        altura_sombra = int(self.raio * 2 * INCLINACAO_Y * escala)

        rect_sombra = pygame.Rect(
            sx - largura_sombra // 2,
            sy - altura_sombra // 2,
            largura_sombra,
            altura_sombra
        )
        pygame.draw.ellipse(superficie, COR_SOMBRA, rect_sombra)

    def desenhar(self, superficie, camera):
        for i, (rx, ry, rz, embalo, tipo) in enumerate(self.rastro):
            tx, ty = mundo_para_tela(rx, ry, rz, camera)
            centro_y = ty - self.raio + 4
            proporcao = (i + 1) / len(self.rastro)
            raio_rastro = int(self.raio * 0.8 * proporcao)
            if raio_rastro > 2:
                if tipo == "WK":
                    cor_rastro = (60, int(180 + 75 * proporcao), 255)
                elif tipo == "SLIDE":
                    cor_rastro = (255, int(100 + 80 * proporcao), 40)
                else:
                    cor_rastro = (220, int(140 + 60 * embalo), 30)
                pygame.draw.circle(superficie, cor_rastro, (tx, centro_y), raio_rastro)

        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        centro_y = ty - self.raio + 4

        if self.perto_parede_no_ar:
            pygame.draw.circle(superficie, COR_WALL_KICK, (tx, centro_y), self.raio + 6, 2)

        if self.slide_ativo:
            largura_corpo = int(self.raio * 2.3)
            altura_corpo = int(self.raio * 1.45)
            rect_corpo = pygame.Rect(
                tx - largura_corpo // 2,
                centro_y - altura_corpo // 2 + 4,
                largura_corpo,
                altura_corpo
            )
            pygame.draw.ellipse(superficie, COR_JOGADOR, rect_corpo)
            pygame.draw.ellipse(superficie, COR_SLIDE, rect_corpo, 3)
        else:
            pygame.draw.circle(superficie, COR_JOGADOR, (tx, centro_y), self.raio)
            cor_borda = COR_WALL_KICK if self.boost_wk_ativo else COR_JOGADOR_BORDA
            pygame.draw.circle(superficie, cor_borda, (tx, centro_y), self.raio, 3 if self.boost_wk_ativo else 2)


class Cristal:
    def __init__(self, x, y, z=8):
        self.x = x
        self.y = y
        self.z_base = z
        self.z = z
        self.raio = 10
        self.fase_flutuacao = random.uniform(0, math.pi * 2)

    @property
    def sort_y(self):
        return self.y

    def atualizar(self, tempo):
        self.z = self.z_base + math.sin(tempo * 4 + self.fase_flutuacao) * 4

    def desenhar_sombra(self, superficie, camera):
        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        rect_sombra = pygame.Rect(sx - 8, sy - 5, 16, 10)
        pygame.draw.ellipse(superficie, COR_SOMBRA, rect_sombra)

    def desenhar(self, superficie, camera):
        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        centro_y = ty - self.raio

        pygame.draw.circle(superficie, COR_CRISTAL, (tx, centro_y), self.raio)
        pygame.draw.circle(superficie, COR_CRISTAL_BRILHO, (tx - 3, centro_y - 3), 3)


def desenhar_icone_carta(superficie, id_mod, centro, cor_destaque):
    """Desenha um emblema vetorial exclusivo para cada tipo de modificador ou perigo."""
    cx, cy = centro
    pygame.draw.circle(superficie, (22, 22, 28), (cx, cy), 38)
    pygame.draw.circle(superficie, (42, 42, 52), (cx, cy), 38, 1)

    if id_mod == "MAIS":
        pygame.draw.circle(superficie, cor_destaque, (cx, cy), 22)
        pygame.draw.circle(superficie, (255, 255, 255), (cx - 6, cy - 6), 5)

    elif id_mod == "ESPACOSO":
        tam = 16
        rect_arena = pygame.Rect(cx - tam, cy - tam, tam * 2, tam * 2)
        pygame.draw.rect(superficie, (55, 50, 62), rect_arena)
        pygame.draw.rect(superficie, cor_destaque, rect_arena, 2)

        direcoes = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        for dx, dy in direcoes:
            inicio = (cx + dx * 10, cy + dy * 10)
            ponta = (cx + dx * 25, cy + dy * 25)
            pygame.draw.line(superficie, cor_destaque, inicio, ponta, 2)
            asa1 = (ponta[0] - dx * 6, ponta[1])
            asa2 = (ponta[0], ponta[1] - dy * 6)
            pygame.draw.line(superficie, cor_destaque, ponta, asa1, 2)
            pygame.draw.line(superficie, cor_destaque, ponta, asa2, 2)

    elif id_mod == "MAZE":
        tam = 22
        rect_maze = pygame.Rect(cx - tam, cy - tam, tam * 2, tam * 2)
        pygame.draw.rect(superficie, (36, 28, 46), rect_maze, border_radius=4)
        pygame.draw.rect(superficie, cor_destaque, rect_maze, 2, border_radius=4)

        cor_parede_icone = (215, 150, 255)
        pygame.draw.line(superficie, cor_parede_icone, (cx - 22, cy - 7), (cx + 4, cy - 7), 3)
        pygame.draw.line(superficie, cor_parede_icone, (cx - 4, cy + 7), (cx + 22, cy + 7), 3)
        pygame.draw.line(superficie, cor_parede_icone, (cx + 8, cy - 22), (cx + 8, cy - 2), 3)
        pygame.draw.line(superficie, cor_parede_icone, (cx - 8, cy + 2), (cx - 8, cy + 22), 3)

    elif id_mod == "LERDO":
        cor_corpo = (230, 175, 130)
        cor_concha = cor_destaque
        cor_espiral = (120, 30, 45)

        rect_corpo = pygame.Rect(cx - 24, cy + 8, 46, 11)
        pygame.draw.ellipse(superficie, cor_corpo, rect_corpo)

        cabeca = (cx + 18, cy + 7)
        pygame.draw.circle(superficie, cor_corpo, cabeca, 7)
        pygame.draw.line(superficie, cor_corpo, (cx + 19, cy + 1), (cx + 24, cy - 8), 2)
        pygame.draw.line(superficie, cor_corpo, (cx + 15, cy + 1), (cx + 17, cy - 8), 2)
        pygame.draw.circle(superficie, (255, 255, 255), (cx + 24, cy - 8), 2)
        pygame.draw.circle(superficie, (255, 255, 255), (cx + 17, cy - 8), 2)

        centro_concha = (cx - 4, cy - 1)
        pygame.draw.circle(superficie, cor_concha, centro_concha, 16)
        pygame.draw.circle(superficie, cor_espiral, centro_concha, 16, 2)
        pygame.draw.circle(superficie, cor_espiral, centro_concha, 10, 2)
        pygame.draw.circle(superficie, cor_espiral, centro_concha, 4, 2)

    elif id_mod == "AERNIS03":
        # Serra metálica de 4 pontas (shuriken / lâmina circular)
        pontos_serra = []
        num_pontas = 4
        for i in range(num_pontas * 2):
            ang = -math.pi / 4 + (i * math.pi / num_pontas)
            r = 26 if i % 2 == 0 else 11
            pontos_serra.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))

        pygame.draw.polygon(superficie, (195, 205, 215), pontos_serra)
        pygame.draw.polygon(superficie, (95, 105, 118), pontos_serra, 2)

        # Disco e furo central do eixo da serra
        pygame.draw.circle(superficie, (140, 150, 165), (cx, cy), 8)
        pygame.draw.circle(superficie, (22, 22, 28), (cx, cy), 4)


class CartaModificador:
    def __init__(self, id_mod, tipo, indice, total_cartas, titulo, subtitulo, detalhe, cor_destaque):
        self.id_mod = id_mod
        self.tipo = tipo
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.detalhe = detalhe
        self.cor_destaque = cor_destaque

        largura_carta = 235
        altura_carta = 325
        espacamento = 24
        largura_total = (largura_carta * total_cartas) + (espacamento * (total_cartas - 1))
        inicio_x = (LARGURA - largura_total) // 2

        x = inicio_x + indice * (largura_carta + espacamento)
        y = (ALTURA - altura_carta) // 2 + 25
        self.rect = pygame.Rect(x, y, largura_carta, altura_carta)

    def desenhar(self, superficie, pos_mouse, fonte_titulo, fonte_sub, fonte_detalhe):
        hover = self.rect.collidepoint(pos_mouse)
        rect_desenho = self.rect.move(0, -10) if hover else self.rect

        eh_perigo = (self.tipo == "PERIGO")
        if eh_perigo:
            cor_fundo = COR_PERIGO_HOVER if hover else COR_PERIGO_FUNDO
            cor_borda = COR_PERIGO_BORDA_HOVER if hover else COR_PERIGO_BORDA
        else:
            cor_fundo = COR_CARTA_HOVER if hover else COR_CARTA_FUNDO
            cor_borda = COR_CARTA_BORDA_HOVER if hover else COR_CARTA_BORDA

        pygame.draw.rect(superficie, cor_fundo, rect_desenho, border_radius=12)
        pygame.draw.rect(superficie, cor_borda, rect_desenho, 3 if hover else 2, border_radius=12)

        texto_tag = "PERIGO ÚNICO" if eh_perigo else "MODIFICADOR"
        cor_tag = (255, 85, 95) if eh_perigo else (150, 160, 180)
        surf_tag = fonte_detalhe.render(texto_tag, True, cor_tag)
        rect_tag = surf_tag.get_rect(center=(rect_desenho.centerx, rect_desenho.y + 22))
        superficie.blit(surf_tag, rect_tag)

        centro_icone = (rect_desenho.centerx, rect_desenho.y + 84)
        desenhar_icone_carta(superficie, self.id_mod, centro_icone, self.cor_destaque)

        surf_titulo = fonte_titulo.render(self.titulo, True, COR_TEXTO)
        rect_titulo = surf_titulo.get_rect(center=(rect_desenho.centerx, rect_desenho.y + 150))
        superficie.blit(surf_titulo, rect_titulo)

        for i, linha in enumerate(self.subtitulo.split("\n")):
            surf_sub = fonte_sub.render(linha, True, (225, 225, 235))
            rect_sub = surf_sub.get_rect(center=(rect_desenho.centerx, rect_desenho.y + 190 + i * 20))
            superficie.blit(surf_sub, rect_sub)

        for i, linha in enumerate(self.detalhe.split("\n")):
            surf_det = fonte_detalhe.render(linha, True, self.cor_destaque)
            rect_det = surf_det.get_rect(center=(rect_desenho.centerx, rect_desenho.y + 258 + i * 18))
            superficie.blit(surf_det, rect_det)


def gerar_paredes_rodada(config):
    total_paredes = config.stacks_maze * 4
    if total_paredes <= 0:
        return []

    paredes = []
    espessura = 26
    margem_borda = 180

    centro_x = 0.0
    centro_y = config.mapa_profundidade / 2
    raio_zona_central = 240.0

    escala_sala = config.mapa_largura / 1800.0
    comp_min = int(240 * escala_sala)
    comp_max = int(440 * escala_sala)

    for _ in range(total_paredes):
        for _tentativa in range(100):
            horizontal = random.choice([True, False])
            comprimento = random.randint(comp_min, comp_max)

            if horizontal:
                w, d = comprimento, espessura
            else:
                w, d = espessura, comprimento

            cx = random.uniform(-config.mapa_largura / 2 + margem_borda + w / 2,
                                config.mapa_largura / 2 - margem_borda - w / 2)
            cy = random.uniform(margem_borda + d / 2,
                                config.mapa_profundidade - margem_borda - d / 2)

            candidata = Parede(cx, cy, w, d)

            prox_cx = max(candidata.min_x, min(centro_x, candidata.max_x))
            prox_cy = max(candidata.min_y, min(centro_y, candidata.max_y))
            if math.hypot(centro_x - prox_cx, centro_y - prox_cy) < raio_zona_central:
                continue

            colidiu_parede = False
            folga_entre_paredes = 70
            for outra in paredes:
                if (candidata.min_x - folga_entre_paredes < outra.max_x and
                        candidata.max_x + folga_entre_paredes > outra.min_x and
                        candidata.min_y - folga_entre_paredes < outra.max_y and
                        candidata.max_y + folga_entre_paredes > outra.min_y):
                    colidiu_parede = True
                    break
            if colidiu_parede:
                continue

            paredes.append(candidata)
            break

    return paredes


def gerar_cristais(config, paredes):
    cristais = []
    margem = 60
    centro_x = 0.0
    centro_y = config.mapa_profundidade / 2

    for _ in range(config.qtd_cristais):
        for _tentativa in range(80):
            cx = random.uniform(-config.mapa_largura / 2 + margem, config.mapa_largura / 2 - margem)
            cy = random.uniform(margem, config.mapa_profundidade - margem)

            if math.hypot(cx - centro_x, cy - centro_y) < 80:
                continue

            dentro_parede = False
            for parede in paredes:
                prox_x = max(parede.min_x, min(cx, parede.max_x))
                prox_y = max(parede.min_y, min(cy, parede.max_y))
                if math.hypot(cx - prox_x, cy - prox_y) < 26:
                    dentro_parede = True
                    break

            if not dentro_parede:
                cristais.append(Cristal(cx, cy))
                break

    return cristais


def gerar_inimigos_rodada(config, paredes):
    inimigos = []
    if not config.perigo_aernis_ativo:
        return inimigos

    margem = 100
    centro_x = 0.0
    centro_y = config.mapa_profundidade / 2

    for _tentativa in range(100):
        ix = random.uniform(-config.mapa_largura / 2 + margem, config.mapa_largura / 2 - margem)
        iy = random.uniform(margem, config.mapa_profundidade - margem)

        if math.hypot(ix - centro_x, iy - centro_y) < 420:
            continue

        dentro_parede = False
        for parede in paredes:
            prox_x = max(parede.min_x, min(ix, parede.max_x))
            prox_y = max(parede.min_y, min(iy, parede.max_y))
            if math.hypot(ix - prox_x, iy - prox_y) < 45:
                dentro_parede = True
                break

        if not dentro_parede:
            inimigos.append(Aernis03(ix, iy))
            break

    return inimigos


def gerar_opcoes_cartas(config):
    disponiveis = [
        (
            "MAIS",
            "MODIFICADOR",
            "Mais?",
            "Adiciona mais cristais\npara coletar",
            f"+5 cristais ({config.qtd_cristais} -> {config.qtd_cristais + 5})",
            (0, 229, 255)
        ),
        (
            "ESPACOSO",
            "MODIFICADOR",
            "Espaçoso",
            "Aumenta o tamanho\nda Área",
            f"+300x300 ({config.mapa_largura} -> {config.mapa_largura + 300})",
            (255, 175, 65)
        ),
        (
            "MAZE",
            "MODIFICADOR",
            "Maze Mode",
            "Adiciona algumas paredes\ninternas no jogo",
            f"+4 paredes finas ({config.stacks_maze * 4} -> {(config.stacks_maze + 1) * 4})",
            (190, 110, 255)
        ),
    ]

    if config.stacks_lerdo < config.max_stacks_lerdo:
        embalo_atual_pct = int(round((1.0 - config.stacks_lerdo * 0.20) * 100))
        embalo_prox_pct = int(round((1.0 - (config.stacks_lerdo + 1) * 0.20) * 100))
        disponiveis.append(
            (
                "LERDO",
                "MODIFICADOR",
                "Sou Lerdo",
                "O Embalo será menor",
                f"Embalo: {embalo_atual_pct}% -> {embalo_prox_pct}%\n({config.stacks_lerdo}/{config.max_stacks_lerdo} escolhidos)",
                (255, 95, 110)
            )
        )

    if not config.perigo_aernis_ativo:
        disponiveis.append(
            (
                "AERNIS03",
                "PERIGO",
                "Zé do Picadinho",
                "Adiciona Aernis-03\nna arena",
                "Serra defeituosa que quica\npelas paredes (Pule por cima!)",
                (255, 110, 35)
            )
        )

    qtd_sortear = min(3, len(disponiveis))
    escolhidas = random.sample(disponiveis, qtd_sortear)

    return [
        CartaModificador(id_mod, tipo, i, qtd_sortear, titulo, sub, det, cor)
        for i, (id_mod, tipo, titulo, sub, det, cor) in enumerate(escolhidas)
    ]


def aplicar_modificador(id_mod, config, jogador):
    if id_mod == "MAIS":
        config.qtd_cristais += 5
        config.stacks_mais += 1

    elif id_mod == "ESPACOSO":
        config.mapa_largura += 300
        config.mapa_profundidade += 300
        config.stacks_espacoso += 1

    elif id_mod == "LERDO":
        if config.stacks_lerdo < config.max_stacks_lerdo:
            config.stacks_lerdo += 1
            jogador.fator_embalo_mod = max(0.40, 1.0 - (config.stacks_lerdo * 0.20))

    elif id_mod == "MAZE":
        config.stacks_maze += 1

    elif id_mod == "AERNIS03":
        config.perigo_aernis_ativo = True


def desenhar_terreno(superficie, camera, config):
    canto_sup_esq = mundo_para_tela(-config.mapa_largura / 2, 0, 0, camera)
    canto_sup_dir = mundo_para_tela(config.mapa_largura / 2, 0, 0, camera)
    canto_inf_dir = mundo_para_tela(config.mapa_largura / 2, config.mapa_profundidade, 0, camera)
    canto_inf_esq = mundo_para_tela(-config.mapa_largura / 2, config.mapa_profundidade, 0, camera)

    pontos_chao = [canto_sup_esq, canto_sup_dir, canto_inf_dir, canto_inf_esq]
    pygame.draw.polygon(superficie, COR_CHAO, pontos_chao)

    passo = 75
    for gx in range(-config.mapa_largura // 2, config.mapa_largura // 2 + 1, passo):
        p1 = mundo_para_tela(gx, 0, 0, camera)
        p2 = mundo_para_tela(gx, config.mapa_profundidade, 0, camera)
        pygame.draw.line(superficie, COR_GRADE, p1, p2, 1)

    for gy in range(0, config.mapa_profundidade + 1, passo):
        p1 = mundo_para_tela(-config.mapa_largura / 2, gy, 0, camera)
        p2 = mundo_para_tela(config.mapa_largura / 2, gy, 0, camera)
        pygame.draw.line(superficie, COR_GRADE, p1, p2, 1)

    cx, cy = mundo_para_tela(0, config.mapa_profundidade / 2, 0, camera)
    pygame.draw.circle(superficie, COR_GRADE, (cx, cy), 32, 1)

    pygame.draw.polygon(superficie, COR_BORDA_MAPA, pontos_chao, 3)


def desenhar_radar(superficie, jogador, cristais, paredes, inimigos, config):
    tamanho_radar = 140
    margem = 20
    rx = LARGURA - tamanho_radar - margem
    ry = margem

    fundo_radar = pygame.Surface((tamanho_radar, tamanho_radar), pygame.SRCALPHA)
    fundo_radar.fill((18, 18, 24, 210))
    superficie.blit(fundo_radar, (rx, ry))

    pygame.draw.rect(superficie, COR_BORDA_MAPA, (rx, ry, tamanho_radar, tamanho_radar), 2)

    def para_radar(wx, wy):
        norm_x = (wx + config.mapa_largura / 2) / config.mapa_largura
        norm_y = wy / config.mapa_profundidade
        px = rx + int(norm_x * tamanho_radar)
        py = ry + int(norm_y * tamanho_radar)
        return px, py

    for parede in paredes:
        p1x, p1y = para_radar(parede.min_x, parede.min_y)
        p2x, p2y = para_radar(parede.max_x, parede.max_y)
        w_rad = max(2, p2x - p1x)
        h_rad = max(2, p2y - p1y)
        pygame.draw.rect(superficie, COR_PAREDE_BORDA, (p1x, p1y, w_rad, h_rad))

    for cristal in cristais:
        cx, cy = para_radar(cristal.x, cristal.y)
        pygame.draw.circle(superficie, COR_CRISTAL, (cx, cy), 3)

    for inimigo in inimigos:
        ix, iy = para_radar(inimigo.x, inimigo.y)
        pygame.draw.circle(superficie, (255, 70, 40), (ix, iy), 5)

    jx, jy = para_radar(jogador.x, jogador.y)
    pygame.draw.circle(superficie, COR_JOGADOR, (jx, jy), 4)


def desenhar_barra_embalo(superficie, jogador, fonte):
    x, y = 20, 52
    largura_max_visual = 180
    largura_barra = int(largura_max_visual * jogador.fator_embalo_mod)
    altura_barra = 12

    faixa_embalo = jogador.vel_max - jogador.vel_min
    velocidade_normal = min(jogador.velocidade_atual, jogador.vel_max)
    embalo = max(0.0, (velocidade_normal - jogador.vel_min) / faixa_embalo) if faixa_embalo > 0 else 0.0

    pygame.draw.rect(superficie, (28, 28, 34), (x, y, largura_max_visual, altura_barra))
    pygame.draw.rect(superficie, (45, 45, 55), (x, y, largura_barra, altura_barra))
    pygame.draw.rect(superficie, (90, 90, 105), (x, y, largura_barra, altura_barra), 1)

    if embalo > 0 and largura_barra > 2:
        cor_barra = (255, int(204 - 110 * embalo), 0)
        pygame.draw.rect(superficie, cor_barra, (x + 1, y + 1, int((largura_barra - 2) * embalo), altura_barra - 2))

    if jogador.velocidade_atual > jogador.vel_max:
        excesso = jogador.velocidade_atual - jogador.vel_max
        largura_extra = int((excesso / jogador.bonus_vel_wk) * 95)
        cor_extra = COR_WALL_KICK if jogador.boost_wk_ativo else COR_SLIDE
        pygame.draw.rect(superficie, cor_extra, (x + largura_barra, y, largura_extra, altura_barra))

    pct_embalo = int(round(jogador.fator_embalo_mod * 100))
    if jogador.boost_wk_ativo:
        texto_status = "WALL KICK!"
        cor_label = COR_WALL_KICK
    elif jogador.slide_ativo:
        texto_status = "AIR SLIDE!" if jogador.slide_foi_no_ar else "SLIDE!"
        cor_label = COR_SLIDE
    else:
        texto_status = f"Embalo ({pct_embalo}%)"
        cor_label = (180, 180, 190)

    label = fonte.render(texto_status, True, cor_label)
    superficie.blit(label, (x + max(largura_max_visual, largura_barra + 95) + 10, y - 3))


def iniciar_nova_rodada(config, jogador, camera):
    jogador.resetar_para_centro(config)
    camera.centralizar(config)
    paredes = gerar_paredes_rodada(config)
    cristais = gerar_cristais(config, paredes)
    inimigos = gerar_inimigos_rodada(config, paredes)
    return paredes, cristais, inimigos


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("ProjetoCollector")
    relogio = pygame.time.Clock()

    fonte = pygame.font.SysFont("consolas", 20, bold=True)
    fonte_grande = pygame.font.SysFont("consolas", 26, bold=True)
    fonte_pequena = pygame.font.SysFont("consolas", 15, bold=True)
    fonte_mini = pygame.font.SysFont("consolas", 13, bold=True)

    config = ConfigPartida()
    jogador = Jogador(config)
    camera = Camera(config)
    paredes, cristais, inimigos = iniciar_nova_rodada(config, jogador, camera)
    pontos = 0
    tempo_jogo = 0.0

    estado = "JOGANDO"
    cartas_atuais = []

    rodando = True
    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_c and estado == "JOGANDO":
                    estado = "ESCOLHA_CARTA"
                    cartas_atuais = gerar_opcoes_cartas(config)
                elif evento.key == pygame.K_r and estado == "GAME_OVER":
                    config = ConfigPartida()
                    jogador = Jogador(config)
                    camera = Camera(config)
                    paredes, cristais, inimigos = iniciar_nova_rodada(config, jogador, camera)
                    pontos = 0
                    estado = "JOGANDO"

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if estado == "ESCOLHA_CARTA":
                    for carta in cartas_atuais:
                        if carta.rect.collidepoint(evento.pos):
                            aplicar_modificador(carta.id_mod, config, jogador)
                            paredes, cristais, inimigos = iniciar_nova_rodada(config, jogador, camera)
                            estado = "JOGANDO"
                            break

        if estado == "JOGANDO":
            tempo_jogo += dt
            teclas = pygame.key.get_pressed()
            jogador.atualizar(teclas, config, paredes, dt)
            camera.atualizar(jogador.x, jogador.y)

            for inimigo in inimigos:
                inimigo.atualizar(config, paredes, dt)
                if inimigo.colidiu_com_jogador(jogador):
                    estado = "GAME_OVER"

            for cristal in cristais[:]:
                cristal.atualizar(tempo_jogo)
                dist_3d = math.sqrt(
                    (jogador.x - cristal.x) ** 2 +
                    (jogador.y - cristal.y) ** 2 +
                    (jogador.z - cristal.z) ** 2
                )
                if dist_3d < (jogador.raio + cristal.raio):
                    cristais.remove(cristal)
                    pontos += 1

            if len(cristais) == 0 and estado == "JOGANDO":
                estado = "ESCOLHA_CARTA"
                cartas_atuais = gerar_opcoes_cartas(config)

        # --- RENDERIZAÇÃO ---
        tela.fill(COR_FUNDO)
        desenhar_terreno(tela, camera, config)

        for parede in paredes:
            parede.desenhar_sombra(tela, camera)
        for cristal in cristais:
            cristal.desenhar_sombra(tela, camera)
        for inimigo in inimigos:
            inimigo.desenhar_sombra(tela, camera)
        jogador.desenhar_sombra(tela, camera)

        entidades = cristais + paredes + inimigos + [jogador]
        entidades.sort(key=lambda obj: obj.sort_y if hasattr(obj, "sort_y") else obj.y)

        for entidade in entidades:
            entidade.desenhar(tela, camera)

        # HUD
        texto_pontos = fonte.render(f"Pontuação: {pontos} | Restantes: {len(cristais)}/{config.qtd_cristais}", True, COR_TEXTO)
        tela.blit(texto_pontos, (20, 20))

        perigos_txt = "Aernis-03" if config.perigo_aernis_ativo else "Nenhum"
        resumo_mods = (
            f"Mods -> Mais?: {config.stacks_mais} | Espaçoso: {config.stacks_espacoso} | "
            f"Lerdo: {config.stacks_lerdo}/{config.max_stacks_lerdo} | Maze: {config.stacks_maze}  ||  Perigos: {perigos_txt}"
        )
        texto_mods = fonte_pequena.render(resumo_mods, True, (210, 140, 150))
        texto_controles = fonte_mini.render("WASD/Setas: Mover | Espaço: Pular/Wall Kick | Shift: Slide | [C]: Cartas", True, (140, 140, 150))
        tela.blit(texto_mods, (20, ALTURA - 52))
        tela.blit(texto_controles, (20, ALTURA - 28))

        desenhar_barra_embalo(tela, jogador, fonte_pequena)
        desenhar_radar(tela, jogador, cristais, paredes, inimigos, config)

        if estado == "ESCOLHA_CARTA":
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((12, 13, 18, 200))
            tela.blit(overlay, (0, 0))

            titulo_tela = fonte_grande.render("ESCOLHA SEU PRÓXIMO DESAFIO", True, (255, 190, 80))
            rect_titulo = titulo_tela.get_rect(center=(LARGURA // 2, 105))
            tela.blit(titulo_tela, rect_titulo)

            for carta in cartas_atuais:
                carta.desenhar(tela, pos_mouse, fonte, fonte_pequena, fonte_mini)

        elif estado == "GAME_OVER":
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((25, 10, 14, 215))
            tela.blit(overlay, (0, 0))

            t_go = fonte_grande.render("FIM DE JOGO!", True, (255, 65, 75))
            t_pts = fonte.render(f"Pontuação Final: {pontos} cristais", True, COR_TEXTO)
            t_reiniciar = fonte_pequena.render("Pressione [R] para jogar novamente", True, (200, 200, 210))

            tela.blit(t_go, t_go.get_rect(center=(LARGURA // 2, ALTURA // 2 - 45)))
            tela.blit(t_pts, t_pts.get_rect(center=(LARGURA // 2, ALTURA // 2 + 5)))
            tela.blit(t_reiniciar, t_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 55)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()