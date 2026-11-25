import pygame
import random
import math


class Jogador:
    def __init__(self, config):
        self.raio = 18

        self.vel_min = 4.0
        self.ganho_embalo_base = 6.5
        self.fator_embalo_mod = 1.0

        self.aceleracao = 0.09
        self.desaceleracao = 0.35

        # Wall Kick + multiplicador afetado pelo modificador 'Brochou'
        self.forca_pulo = 10.5
        self.gravidade = 0.55
        self.espaco_pressionado_antes = False
        self.duracao_boost_wk = 0.95
        self.bonus_vel_wk_base = 7.5
        self.fator_wk_mod = 1.0

        # Slide / Air Slide + Slide Jump + multiplicador afetado por 'Escorregou na Real'
        self.shift_pressionado_antes = False
        self.fator_slide_mod = 1.0
        self.duracao_boost_slide_jump = 0.85

        # Configurações do Parry (Tecla E ou Botão Direito do Mouse)
        self.janela_parry_max = 0.16
        self.cooldown_parry_max = 3.20
        self.duracao_boost_parry = 1.10
        self.bonus_vel_parry = 9.5
        self.parry_pressionado_antes = False
        self.parry_bloqueado = False

        # Animação de Morte (arremessado para cima e cai girando para fora do fundo da tela)
        self.morto = False
        self.morte_tela_x = 0.0
        self.morte_tela_y = 0.0
        self.morte_vel_x = 0.0
        self.morte_vel_y = 0.0
        self.morte_angulo = 0.0
        self.morte_vel_ang = 0.0

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

        # Controle do Slide Jump (uso único até a energia extra do slide acabar)
        self.timer_boost_slide_jump = 0.0
        self.bonus_vel_slide_jump_atual = 0.0
        self.slide_jump_disponivel = True

        self.timer_parry_ativo = 0.0
        self.cooldown_parry = 0.0
        self.timer_boost_parry = 0.0
        self.timer_invulneravel_parry = 0.0
        self.onda_parry_timer = 0.0

        self.timer_lentidao_bigon = 0.0

        self.morto = False
        self.morte_tela_x = 0.0
        self.morte_tela_y = 0.0
        self.morte_vel_x = 0.0
        self.morte_vel_y = 0.0
        self.morte_angulo = 0.0
        self.morte_vel_ang = 0.0

    def iniciar_animacao_morte(self, camera, fonte_x=None):
        """Inicia o lançamento clássico para fora do fundo da tela girando."""
        from main import mundo_para_tela

        if self.morto:
            return
        self.morto = True
        self.rastro.clear()
        self.timer_slide = 0.0
        self.timer_boost_slide_jump = 0.0
        self.timer_parry_ativo = 0.0
        self.timer_boost_wk = 0.0
        self.timer_boost_parry = 0.0

        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        self.morte_tela_x = float(tx)
        self.morte_tela_y = float(ty - self.raio + 4)

        if fonte_x is not None and abs(self.x - fonte_x) > 1.0:
            lado = 1.0 if self.x >= fonte_x else -1.0
        else:
            lado = random.choice([-1.0, 1.0])

        self.morte_vel_x = lado * random.uniform(2.2, 3.6)
        self.morte_vel_y = -11.5
        self.morte_angulo = 0.0
        self.morte_vel_ang = lado * 13.5

    def atualizar_morte(self, dt):
        """Atualiza o arco parabólico da queda para fora do fundo da tela."""
        from main import ALTURA

        if not self.morto:
            return
        if self.morte_tela_y > ALTURA + 120:
            return

        fator_frame = dt * 60.0
        self.morte_tela_x += self.morte_vel_x * fator_frame
        self.morte_tela_y += self.morte_vel_y * fator_frame
        self.morte_vel_y += 0.56 * fator_frame
        self.morte_angulo += self.morte_vel_ang * dt

    def desenhar_animacao_morte(self, superficie):
        """Desenha o boneco girando em primeiro plano enquanto cai para fora do fundo."""
        from main import ALTURA, COR_JOGADOR, COR_JOGADOR_BORDA

        if not self.morto or self.morte_tela_y > ALTURA + 110:
            return

        cx = int(self.morte_tela_x)
        cy = int(self.morte_tela_y)

        pygame.draw.circle(superficie, COR_JOGADOR, (cx, cy), self.raio)
        pygame.draw.circle(superficie, COR_JOGADOR_BORDA, (cx, cy), self.raio, 3)

        brilho_x = cx + int(math.cos(self.morte_angulo) * 9)
        brilho_y = cy + int(math.sin(self.morte_angulo) * 9)
        pygame.draw.circle(superficie, (255, 242, 150), (brilho_x, brilho_y), 4)

        cos_a = math.cos(self.morte_angulo)
        sin_a = math.sin(self.morte_angulo)
        for lado in (-1, 1):
            local_x = lado * 6.5
            local_y = -2.0
            ox = cx + int(local_x * cos_a - local_y * sin_a)
            oy = cy + int(local_x * sin_a + local_y * cos_a)

            for diag in (-1, 1):
                ang_d = self.morte_angulo + (math.pi / 4) * diag
                dx = math.cos(ang_d) * 3.5
                dy = math.sin(ang_d) * 3.5
                pygame.draw.line(
                    superficie,
                    (40, 28, 12),
                    (int(ox - dx), int(oy - dy)),
                    (int(ox + dx), int(oy + dy)),
                    2
                )

    def aplicar_lentidao_bigon(self, duracao=1.35):
        self.timer_lentidao_bigon = duracao
        self.velocidade_atual = min(self.velocidade_atual, self.vel_min * 0.55)

    @property
    def lento_por_bigon(self):
        return self.timer_lentidao_bigon > 0.0

    @property
    def vel_max(self):
        return self.vel_min + (self.ganho_embalo_base * self.fator_embalo_mod)

    @property
    def bonus_vel_wk(self):
        return self.bonus_vel_wk_base * self.fator_wk_mod

    @property
    def boost_wk_ativo(self):
        return self.timer_boost_wk > 0.0

    @property
    def slide_ativo(self):
        return self.timer_slide > 0.0

    @property
    def boost_slide_jump_ativo(self):
        return self.timer_boost_slide_jump > 0.0

    @property
    def tem_energia_slide_extra(self):
        """Indica se ainda há velocidade extra proveniente do Slide ou Slide Jump."""
        return (
            self.slide_ativo or
            self.boost_slide_jump_ativo or
            (self.velocidade_atual > self.vel_max + 0.15 and not self.boost_wk_ativo and not self.boost_parry_ativo)
        )

    @property
    def parry_ativo(self):
        return (not self.parry_bloqueado) and (self.timer_parry_ativo > 0.0)

    @property
    def boost_parry_ativo(self):
        return self.timer_boost_parry > 0.0

    def executar_parry_sucesso(self, dir_fuga_x=None, dir_fuga_y=None):
        self.timer_parry_ativo = 0.0
        self.cooldown_parry = 1.25
        self.timer_boost_parry = self.duracao_boost_parry
        self.timer_invulneravel_parry = 0.35
        self.onda_parry_timer = 0.35
        self.timer_lentidao_bigon = 0.0

        if dir_fuga_x is not None and dir_fuga_y is not None:
            comp = math.hypot(dir_fuga_x, dir_fuga_y)
            if comp > 0.0001:
                self.dir_x = dir_fuga_x / comp
                self.dir_y = dir_fuga_y / comp

        self.velocidade_atual = max(self.velocidade_atual, self.vel_max + self.bonus_vel_parry)

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

    def atualizar(self, teclas, botoes_mouse, config, paredes, dt):
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
        if self.timer_boost_slide_jump > 0.0:
            self.timer_boost_slide_jump = max(0.0, self.timer_boost_slide_jump - dt)
        if self.cooldown_slide > 0.0:
            self.cooldown_slide = max(0.0, self.cooldown_slide - dt)
        if self.timer_lentidao_bigon > 0.0:
            self.timer_lentidao_bigon = max(0.0, self.timer_lentidao_bigon - dt)

        # Recarrega o Slide Jump assim que toda a energia extra do Slide acabar
        if not self.slide_jump_disponivel and not self.tem_energia_slide_extra:
            self.slide_jump_disponivel = True

        if self.timer_parry_ativo > 0.0:
            self.timer_parry_ativo = max(0.0, self.timer_parry_ativo - dt)
        if self.cooldown_parry > 0.0:
            self.cooldown_parry = max(0.0, self.cooldown_parry - dt)
        if self.timer_boost_parry > 0.0:
            self.timer_boost_parry = max(0.0, self.timer_boost_parry - dt)
        if self.timer_invulneravel_parry > 0.0:
            self.timer_invulneravel_parry = max(0.0, self.timer_invulneravel_parry - dt)
        if self.onda_parry_timer > 0.0:
            self.onda_parry_timer = max(0.0, self.onda_parry_timer - dt)

        if not self.parry_bloqueado:
            parry_agora = teclas[pygame.K_e] or botoes_mouse[2]
            apertou_parry = parry_agora and not self.parry_pressionado_antes
            self.parry_pressionado_antes = parry_agora

            if apertou_parry and self.cooldown_parry <= 0.0 and not self.parry_ativo:
                self.timer_parry_ativo = self.janela_parry_max
                self.cooldown_parry = self.cooldown_parry_max
        else:
            self.timer_parry_ativo = 0.0

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
                self.bonus_vel_slide_atual = 4.2 * self.fator_slide_mod
                self.cooldown_slide = 0.70
            else:
                self.slide_foi_no_ar = True
                self.timer_slide = 0.65
                self.bonus_vel_slide_atual = 6.2 * self.fator_slide_mod
                self.vel_z = max(self.vel_z, 3.2)
                self.cooldown_slide = 0.85

            self.velocidade_atual = max(self.velocidade_atual, self.vel_max + self.bonus_vel_slide_atual)

        # Leitura do Pulo / Wall Kick / Slide Jump
        espaco_agora = teclas[pygame.K_SPACE]
        apertou_espaco = espaco_agora and not self.espaco_pressionado_antes
        self.espaco_pressionado_antes = espaco_agora

        normal_parede = self.detectar_normal_parede(config, paredes)
        self.perto_parede_no_ar = (not self.no_chao) and self.pode_wall_kick and (normal_parede is not None)

        if apertou_espaco:
            if self.no_chao:
                # Slide Jump: pular durante o Slide conserva o embalo extra do Slide (1 uso até zerar)
                if self.slide_ativo and self.slide_jump_disponivel:
                    self.slide_jump_disponivel = False
                    self.timer_slide = 0.0
                    self.timer_boost_slide_jump = self.duracao_boost_slide_jump
                    self.bonus_vel_slide_jump_atual = max(
                        self.bonus_vel_slide_atual,
                        max(0.0, self.velocidade_atual - self.vel_max)
                    )
                    self.velocidade_atual = max(
                        self.velocidade_atual,
                        self.vel_max + self.bonus_vel_slide_jump_atual
                    )

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
                self.velocidade_atual = max(self.velocidade_atual, self.vel_max + self.bonus_vel_wk)

        bonus_wk = self.bonus_vel_wk * (self.timer_boost_wk / self.duracao_boost_wk) if self.boost_wk_ativo else 0.0
        duracao_ref_slide = 0.65 if self.slide_foi_no_ar else 0.45
        bonus_sl = self.bonus_vel_slide_atual * (self.timer_slide / duracao_ref_slide) if self.slide_ativo else 0.0
        # Conserva a velocidade extra do Slide durante o Slide Jump
        bonus_sj = self.bonus_vel_slide_jump_atual if self.boost_slide_jump_ativo else 0.0
        bonus_pr = self.bonus_vel_parry * (self.timer_boost_parry / self.duracao_boost_parry) if self.boost_parry_ativo else 0.0
        vel_max_atual = self.vel_max + max(bonus_wk, bonus_sl, bonus_sj, bonus_pr)

        tem_boost_ativo = (
            self.boost_wk_ativo or
            self.slide_ativo or
            self.boost_slide_jump_ativo or
            self.boost_parry_ativo
        )

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
                    if not tem_boost_ativo:
                        self.velocidade_atual = self.vel_min

            self.dir_x = dx
            self.dir_y = dy
        else:
            if not tem_boost_ativo:
                self.velocidade_atual = max(0.0, self.velocidade_atual - self.desaceleracao)

        if self.velocidade_atual > vel_max_atual:
            taxa_queda = 0.65 if (not tem_boost_ativo and not self.slide_foi_no_ar) else 0.35
            self.velocidade_atual = max(vel_max_atual, self.velocidade_atual - taxa_queda)

        if self.lento_por_bigon and not self.boost_parry_ativo:
            self.velocidade_atual = min(self.velocidade_atual, self.vel_min * 0.55)

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

        if bateu_parede and self.no_chao and not tem_boost_ativo:
            self.velocidade_atual = min(self.velocidade_atual, self.vel_min)

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
        if self.boost_parry_ativo:
            tipo_rastro = "PARRY"
        elif self.boost_wk_ativo:
            tipo_rastro = "WK"
        elif self.boost_slide_jump_ativo:
            tipo_rastro = "SLIDE_JUMP"
        elif self.slide_ativo:
            tipo_rastro = "SLIDE"

        if fator_embalo > 0.35 or tipo_rastro != "NORMAL":
            self.rastro.append((self.x, self.y, self.z, min(1.0, fator_embalo), tipo_rastro))
        if len(self.rastro) > 10:
            self.rastro.pop(0)
        elif fator_embalo <= 0.35 and tipo_rastro == "NORMAL" and self.rastro:
            self.rastro.pop(0)

    def desenhar_sombra(self, superficie, camera):
        from main import mundo_para_tela, INCLINACAO_Y, COR_SOMBRA

        if self.morto:
            return
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
        from main import (
            mundo_para_tela,
            COR_JOGADOR,
            COR_JOGADOR_BORDA,
            COR_WALL_KICK,
            COR_SLIDE,
            COR_PARRY,
        )

        if self.morto:
            return

        for i, (rx, ry, rz, embalo, tipo) in enumerate(self.rastro):
            tx, ty = mundo_para_tela(rx, ry, rz, camera)
            centro_y = ty - self.raio + 4
            proporcao = (i + 1) / len(self.rastro)
            raio_rastro = int(self.raio * 0.8 * proporcao)
            if raio_rastro > 2:
                if tipo == "PARRY":
                    cor_rastro = (255, int(235 + 20 * proporcao), int(180 + 75 * proporcao))
                elif tipo == "WK":
                    cor_rastro = (60, int(180 + 75 * proporcao), 255)
                elif tipo == "SLIDE_JUMP":
                    cor_rastro = (255, int(155 + 75 * proporcao), int(40 + 55 * proporcao))
                elif tipo == "SLIDE":
                    cor_rastro = (255, int(100 + 80 * proporcao), 40)
                else:
                    cor_rastro = (220, int(140 + 60 * embalo), 30)
                pygame.draw.circle(superficie, cor_rastro, (tx, centro_y), raio_rastro)

        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        centro_y = ty - self.raio + 4

        if self.onda_parry_timer > 0.0:
            prog_onda = 1.0 - (self.onda_parry_timer / 0.35)
            raio_onda = int(self.raio + 10 + prog_onda * 55)
            pygame.draw.circle(superficie, COR_PARRY, (tx, centro_y), raio_onda, 3)

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
            cor_borda_slide = COR_PARRY if (self.parry_ativo or self.boost_parry_ativo) else COR_SLIDE
            pygame.draw.ellipse(superficie, cor_borda_slide, rect_corpo, 3)
        else:
            cor_corpo = (255, 248, 210) if self.parry_ativo else COR_JOGADOR
            pygame.draw.circle(superficie, cor_corpo, (tx, centro_y), self.raio)
            if self.parry_ativo or self.boost_parry_ativo:
                cor_borda = COR_PARRY
                espessura = 3
            elif self.lento_por_bigon:
                cor_borda = (95, 175, 130)
                espessura = 3
            elif self.boost_wk_ativo:
                cor_borda = COR_WALL_KICK
                espessura = 3
            elif self.boost_slide_jump_ativo:
                cor_borda = COR_SLIDE
                espessura = 3
            else:
                cor_borda = COR_JOGADOR_BORDA
                espessura = 2
            pygame.draw.circle(superficie, cor_borda, (tx, centro_y), self.raio, espessura)

        if self.parry_ativo:
            prog = self.timer_parry_ativo / self.janela_parry_max
            raio_escudo = int(self.raio + 5 + prog * 10)
            pygame.draw.circle(superficie, COR_PARRY, (tx, centro_y), raio_escudo, 3)