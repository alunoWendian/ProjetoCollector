import pygame
import random
import math


class MestreHUD:
    """Entidade misteriosa no topo do HUD: olhos em losango totalmente vermelhos sem parte branca."""
    def __init__(self):
        self.resetar_ciclo()

    def resetar_ciclo(self):
        self.estado = "FECHADO"
        self.timer = random.uniform(14.0, 17.0)
        self.abertura = 0.0

    def forcar_fechar(self):
        self.estado = "FECHADO"
        self.abertura = 0.0
        self.timer = random.uniform(14.0, 17.0)

    def atualizar(self, dt):
        self.timer -= dt

        if self.estado == "FECHADO":
            self.abertura = max(0.0, self.abertura - dt * 5.0)
            if self.timer <= 0.0:
                self.estado = "AVISO"
                self.timer = 1.2

        elif self.estado == "AVISO":
            self.abertura = min(0.32, self.abertura + dt * 0.45)
            if self.timer <= 0.0:
                self.estado = "ABERTO"
                self.timer = 2.1

        elif self.estado == "ABERTO":
            self.abertura = min(1.0, self.abertura + dt * 9.0)
            if self.timer <= 0.0:
                self.estado = "FECHADO"
                self.timer = random.uniform(14.0, 17.0)

    def detectou_movimento(self, jogador):
        if self.estado != "ABERTO":
            return False
        esta_movendo = (
            jogador.velocidade_atual > 0.35 or
            not jogador.no_chao or
            jogador.z > 0.5 or
            jogador.slide_ativo
        )
        return esta_movendo

    def desenhar(self, superficie, fonte_aviso, pausado=False):
        from main import LARGURA

        cx = LARGURA // 2
        cy = 48
        espaco_olhos = 42

        if self.estado in ("AVISO", "ABERTO"):
            faixa = pygame.Surface((LARGURA, 115), pygame.SRCALPHA)
            alpha = 50 if self.estado == "AVISO" else 105
            faixa.fill((170, 15, 25, alpha))
            superficie.blit(faixa, (0, 0))

        tremor_x = random.randint(-2, 2) if (self.estado == "AVISO" and not pausado) else 0
        tremor_y = random.randint(-1, 1) if (self.estado == "AVISO" and not pausado) else 0

        for lado in (-1, 1):
            ox = cx + lado * espaco_olhos + tremor_x
            oy = cy + tremor_y

            largura_meia = 26
            altura_meia = max(2, int(20 * self.abertura))

            pontos_losango = [
                (ox, oy - altura_meia),
                (ox + largura_meia, oy),
                (ox, oy + altura_meia),
                (ox - largura_meia, oy)
            ]

            if self.estado == "FECHADO" and self.abertura <= 0.05:
                pygame.draw.line(superficie, (145, 25, 35), (ox - largura_meia, oy), (ox + largura_meia, oy), 3)
                pygame.draw.circle(superficie, (190, 30, 40), (ox, oy), 3)
            else:
                cor_fundo_olho = (45, 8, 12) if self.estado == "AVISO" else (95, 12, 20)
                cor_borda_olho = (200, 30, 40) if self.estado == "AVISO" else (255, 35, 45)

                pygame.draw.polygon(superficie, cor_fundo_olho, pontos_losango)
                pygame.draw.polygon(superficie, cor_borda_olho, pontos_losango, 2)

                if self.abertura > 0.22:
                    raio_pupila = 4 if self.estado == "AVISO" else 5
                    cor_pupila = (220, 35, 45) if self.estado == "AVISO" else (255, 40, 50)
                    pygame.draw.circle(superficie, cor_pupila, (ox, oy), raio_pupila)

        if self.estado == "AVISO":
            txt = fonte_aviso.render("O MESTRE VAI ABRIR OS OLHOS...", True, (255, 110, 115))
            superficie.blit(txt, txt.get_rect(center=(cx, cy + 32)))
        elif self.estado == "ABERTO":
            txt = fonte_aviso.render("FIQUE PARADO!", True, (255, 55, 65))
            superficie.blit(txt, txt.get_rect(center=(cx, cy + 32)))


class GerenciadorPropaganda:
    """Perigo Único 'Propaganda': Aviso prévio parryável seguido de Pop-up clássico de Windows."""
    def __init__(self):
        self.resetar()

    def resetar(self):
        self.estado = "AGUARDANDO"
        self.timer = random.uniform(6.0, 10.0)
        self.tempo_aberto = 0.0

        self.rect_janela = pygame.Rect(0, 0, 340, 210)
        self.rect_fechar = pygame.Rect(0, 0, 24, 20)
        self.rect_ok = pygame.Rect(0, 0, 82, 26)
        self.mensagem_rara = False

    def abrir_popup(self):
        from main import LARGURA, ALTURA

        self.estado = "ABERTO"
        self.tempo_aberto = 0.0

        largura = 340
        altura = 210
        x = random.randint(150, LARGURA - largura - 150)
        y = random.randint(135, ALTURA - altura - 95)

        self.rect_janela = pygame.Rect(x, y, largura, altura)
        self.rect_fechar = pygame.Rect(x + largura - 29, y + 6, 23, 20)
        self.rect_ok = pygame.Rect(x + (largura - 82) // 2, y + altura - 40, 82, 26)
        self.mensagem_rara = (random.random() < 0.10)

    def bloquear_com_parry(self):
        self.estado = "AGUARDANDO"
        self.timer = random.uniform(9.5, 13.5)
        self.tempo_aberto = 0.0

    def pode_dar_parry(self):
        return self.estado == "AVISO" or (self.estado == "ABERTO" and self.tempo_aberto <= 0.30)

    def atualizar(self, dt):
        if self.estado == "AGUARDANDO":
            self.timer -= dt
            if self.timer <= 0.0:
                self.estado = "AVISO"
                self.timer = 0.90

        elif self.estado == "AVISO":
            self.timer -= dt
            if self.timer <= 0.0:
                self.abrir_popup()

        elif self.estado == "ABERTO":
            self.tempo_aberto += dt

    def processar_clique(self, pos):
        if self.estado != "ABERTO":
            return False
        if self.rect_fechar.collidepoint(pos) or self.rect_ok.collidepoint(pos):
            self.estado = "AGUARDANDO"
            self.timer = random.uniform(8.0, 12.5)
            return True
        return False

    def desenhar_borda_win98(self, superficie, rect, afundado=False):
        cor_clara = (255, 255, 255)
        cor_media_clara = (223, 223, 223)
        cor_sombra = (128, 128, 128)
        cor_escura = (40, 40, 40)

        c1 = cor_escura if afundado else cor_clara
        c2 = cor_sombra if afundado else cor_media_clara
        c3 = cor_media_clara if afundado else cor_sombra
        c4 = cor_clara if afundado else cor_escura

        pygame.draw.line(superficie, c1, (rect.left, rect.top), (rect.right - 1, rect.top), 2)
        pygame.draw.line(superficie, c1, (rect.left, rect.top), (rect.left, rect.bottom - 1), 2)
        pygame.draw.line(superficie, c2, (rect.left + 2, rect.top + 2), (rect.right - 3, rect.top + 2), 1)
        pygame.draw.line(superficie, c2, (rect.left + 2, rect.top + 2), (rect.left + 2, rect.bottom - 3), 1)

        pygame.draw.line(superficie, c4, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
        pygame.draw.line(superficie, c4, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)
        pygame.draw.line(superficie, c3, (rect.left + 1, rect.bottom - 3), (rect.right - 3, rect.bottom - 3), 1)
        pygame.draw.line(superficie, c3, (rect.right - 3, rect.top + 1), (rect.right - 3, rect.bottom - 3), 1)

    def desenhar(self, superficie, pos_mouse, fonte_titulo, fonte_corpo, fonte_aviso, mestre_ativo=False):
        from main import LARGURA

        if self.estado == "AGUARDANDO":
            return

        if self.estado == "AVISO":
            cx = LARGURA // 2
            cy = 122 if mestre_ativo else 46
            pulso = 1.0 + math.sin(self.timer * 24.0) * 0.06
            w_box = int(280 * pulso)
            h_box = int(38 * pulso)
            rect_aviso = pygame.Rect(cx - w_box // 2, cy - h_box // 2, w_box, h_box)

            pygame.draw.rect(superficie, (192, 192, 192), rect_aviso)
            self.desenhar_borda_win98(superficie, rect_aviso, afundado=False)

            ix = rect_aviso.x + 22
            iy = rect_aviso.centery
            pygame.draw.circle(superficie, (220, 32, 42), (ix, iy), 11)
            pygame.draw.circle(superficie, (120, 15, 22), (ix, iy), 11, 2)
            pygame.draw.line(superficie, (255, 255, 255), (ix - 4, iy - 4), (ix + 4, iy + 4), 2)
            pygame.draw.line(superficie, (255, 255, 255), (ix - 4, iy + 4), (ix + 4, iy - 4), 2)

            txt = fonte_aviso.render("POP-UP CHEGANDO! [PARRY]", True, (20, 20, 28))
            superficie.blit(txt, txt.get_rect(midleft=(ix + 18, iy)))
            return

        r = self.rect_janela

        sombra = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 130))
        superficie.blit(sombra, (r.x + 7, r.y + 7))

        pygame.draw.rect(superficie, (192, 192, 192), r)
        self.desenhar_borda_win98(superficie, r, afundado=False)

        barra_titulo = pygame.Rect(r.x + 4, r.y + 4, r.width - 8, 24)
        pygame.draw.rect(superficie, (0, 0, 128), barra_titulo)

        pygame.draw.circle(superficie, (225, 35, 45), (barra_titulo.x + 12, barra_titulo.centery), 7)
        pygame.draw.line(superficie, (255, 255, 255), (barra_titulo.x + 9, barra_titulo.centery - 3), (barra_titulo.x + 15, barra_titulo.centery + 3), 2)
        pygame.draw.line(superficie, (255, 255, 255), (barra_titulo.x + 9, barra_titulo.centery + 3), (barra_titulo.x + 15, barra_titulo.centery - 3), 2)

        t_barra = fonte_titulo.render("Anúncio", True, (255, 255, 255))
        superficie.blit(t_barra, t_barra.get_rect(midleft=(barra_titulo.x + 25, barra_titulo.centery)))

        hover_x = self.rect_fechar.collidepoint(pos_mouse)
        cor_btn_x = (235, 50, 58) if hover_x else (205, 38, 46)
        pygame.draw.rect(superficie, cor_btn_x, self.rect_fechar)
        self.desenhar_borda_win98(superficie, self.rect_fechar, afundado=False)
        cx_x, cy_x = self.rect_fechar.center
        pygame.draw.line(superficie, (255, 255, 255), (cx_x - 4, cy_x - 4), (cx_x + 4, cy_x + 4), 2)
        pygame.draw.line(superficie, (255, 255, 255), (cx_x - 4, cy_x + 4), (cx_x + 4, cy_x - 4), 2)

        if self.mensagem_rara:
            t_msg = fonte_corpo.render("Proibido ser covarde.", True, (18, 18, 22))
            superficie.blit(t_msg, t_msg.get_rect(center=(r.centerx, r.y + 98)))

        hover_ok = self.rect_ok.collidepoint(pos_mouse)
        cor_ok = (212, 212, 212) if hover_ok else (192, 192, 192)
        pygame.draw.rect(superficie, cor_ok, self.rect_ok)
        self.desenhar_borda_win98(superficie, self.rect_ok, afundado=False)
        t_ok = fonte_titulo.render("OK", True, (15, 15, 18))
        superficie.blit(t_ok, t_ok.get_rect(center=self.rect_ok.center))


class Aernis03:
    """Inimigo 'Zé do Picadinho': Máquina achatada laranja com núcleo preto, olhos de raiva e serra inferior."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0.0
        self.raio = 25
        self.altura_hitbox = 28

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

        self.timer_tonto = 0.0
        self.angulo_tonto = 0.0

    @property
    def sort_y(self):
        return self.y

    @property
    def esta_tonto(self):
        return self.timer_tonto > 0.0

    def atordoar(self, duracao=2.8):
        self.timer_tonto = duracao
        self.vx = -self.vx
        self.vy = -self.vy

    def atualizar(self, jogador, config, paredes, dt):
        for p in self.fumaca[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["z"] += p["vz"]
            p["vida"] -= dt
            if p["vida"] <= 0:
                self.fumaca.remove(p)

        if self.esta_tonto:
            self.timer_tonto = max(0.0, self.timer_tonto - dt)
            self.angulo_tonto += dt * 7.5
            self.angulo_serra += dt * 2.0
            return

        self.angulo_serra += dt * 18.0

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

    def colidiu_com_jogador(self, jogador, margem_extra=0.0):
        if self.esta_tonto:
            return False
        if jogador.z > self.altura_hitbox:
            return False
        dist_xy = math.hypot(jogador.x - self.x, jogador.y - self.y)
        return dist_xy < (jogador.raio + self.raio - 4 + margem_extra)

    def desenhar_sombra(self, superficie, camera):
        from main import mundo_para_tela, INCLINACAO_Y, COR_SOMBRA

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
        from main import mundo_para_tela, INCLINACAO_Y

        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        offset_tonto_x = int(math.sin(self.angulo_tonto * 3.0) * 2) if self.esta_tonto else 0

        centro_serra = (tx + offset_tonto_x, ty - 3)
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

        cor_serra = (140, 148, 160) if self.esta_tonto else (180, 190, 200)
        pygame.draw.polygon(superficie, cor_serra, pontos_serra)
        pygame.draw.polygon(superficie, (70, 75, 85), pontos_serra, 2)

        largura_chassi = 56
        altura_chassi = 22
        rect_chassi = pygame.Rect(
            tx + offset_tonto_x - largura_chassi // 2,
            ty - altura_chassi - 3,
            largura_chassi,
            altura_chassi
        )
        cor_chassi = (210, 105, 35) if self.esta_tonto else (242, 112, 20)
        pygame.draw.rect(superficie, cor_chassi, rect_chassi, border_radius=8)
        pygame.draw.rect(superficie, (185, 75, 10), rect_chassi, 2, border_radius=8)

        rect_teto = pygame.Rect(tx + offset_tonto_x - 22, ty - altura_chassi - 5, 44, 9)
        pygame.draw.ellipse(superficie, (255, 138, 42), rect_teto)

        rect_meio_preto = pygame.Rect(tx + offset_tonto_x - 15, ty - altura_chassi - 2, 30, altura_chassi - 2)
        pygame.draw.rect(superficie, (24, 24, 28), rect_meio_preto, border_radius=4)
        pygame.draw.line(
            superficie,
            (50, 50, 56),
            (tx + offset_tonto_x - 10, ty - 8),
            (tx + offset_tonto_x + 10, ty - 8),
            2
        )

        if self.esta_tonto:
            ox = tx + offset_tonto_x
            oy = ty - 15
            for lado in (-7, 7):
                cx_olho = ox + lado
                tam_x = 3
                pygame.draw.line(superficie, (255, 220, 90), (cx_olho - tam_x, oy - tam_x), (cx_olho + tam_x, oy + tam_x), 2)
                pygame.draw.line(superficie, (255, 220, 90), (cx_olho - tam_x, oy + tam_x), (cx_olho + tam_x, oy - tam_x), 2)

            for i in range(3):
                ang_est = self.angulo_tonto + (i * (2 * math.pi / 3))
                ex = ox + int(math.cos(ang_est) * 16)
                ey = (ty - 32) + int(math.sin(ang_est) * 5)
                pygame.draw.circle(superficie, (255, 235, 110), (ex, ey), 2)
        else:
            olhar_x = int((self.vx / 5.5) * 3)
            olhar_y = int((self.vy / 5.5) * 1.5)
            ox = tx + olhar_x
            oy = ty - 16 + olhar_y

            olho_esq = [(ox - 11, oy - 3), (ox - 3, oy), (ox - 4, oy + 4), (ox - 11, oy + 2)]
            olho_dir = [(ox + 11, oy - 3), (ox + 3, oy), (ox + 4, oy + 4), (ox + 11, oy + 2)]
            pygame.draw.polygon(superficie, (245, 22, 32), olho_esq)
            pygame.draw.polygon(superficie, (245, 22, 32), olho_dir)

        for p in self.fumaca:
            fx, fy = mundo_para_tela(p["x"], p["y"], p["z"], camera)
            proporcao = p["vida"] / p["max_vida"]
            raio_f = max(2, int(p["raio"] * (1.3 - 0.5 * proporcao)))
            tom = int(55 + 40 * (1.0 - proporcao))
            pygame.draw.circle(superficie, (tom, tom, tom + 5), (fx, fy), raio_f)


class Perseqtor:
    """Inimigo 'Atrás de mim?': Sombra humanoide borrada e apagada na base que atravessa paredes."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0.0
        self.raio = 20
        self.velocidade = 1.95
        self.fase_flutuacao = random.uniform(0, math.pi * 2)
        self.timer_tonto = 0.0
        self.motivo_morte = "CAPTURADO PELO PERSEQTOR!"

    @property
    def sort_y(self):
        return self.y

    @property
    def esta_tonto(self):
        return self.timer_tonto > 0.0

    def atordoar(self, duracao=2.8):
        self.timer_tonto = duracao

    def atualizar(self, jogador, config, paredes, dt):
        self.fase_flutuacao += dt * 3.2

        if self.esta_tonto:
            self.timer_tonto = max(0.0, self.timer_tonto - dt)
            dx = self.x - jogador.x
            dy = self.y - jogador.y
            dist = math.hypot(dx, dy)
            if dist > 0.001:
                self.x += (dx / dist) * (self.velocidade * 1.6)
                self.y += (dy / dist) * (self.velocidade * 1.6)
            return

        dx = jogador.x - self.x
        dy = jogador.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.x += (dx / dist) * self.velocidade
            self.y += (dy / dist) * self.velocidade

    def colidiu_com_jogador(self, jogador, margem_extra=0.0):
        if self.esta_tonto:
            return False
        if jogador.z > 48:
            return False
        dist_xy = math.hypot(jogador.x - self.x, jogador.y - self.y)
        return dist_xy < (jogador.raio + self.raio - 4 + margem_extra)

    def desenhar_sombra(self, superficie, camera):
        from main import mundo_para_tela

        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        sombra_surf = pygame.Surface((56, 28), pygame.SRCALPHA)
        alpha = 40 if self.esta_tonto else 85
        pygame.draw.ellipse(sombra_surf, (8, 6, 14, alpha), (4, 4, 48, 20))
        superficie.blit(sombra_surf, (sx - 28, sy - 14))

    def desenhar(self, superficie, camera):
        from main import mundo_para_tela

        flutuacao = math.sin(self.fase_flutuacao) * 4.5
        tx, ty = mundo_para_tela(self.x, self.y, self.z + 6 + flutuacao, camera)

        w, h = 84, 116
        fantasma = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2
        fator_tonto = 0.45 if self.esta_tonto else 1.0

        for camada in range(4):
            expand = (4 - camada) * 4
            alpha_camada = int((16 + camada * 14) * fator_tonto)
            cor_aura = (18, 14, 28, alpha_camada)

            pygame.draw.circle(fantasma, cor_aura, (cx, 28), 13 + expand)
            pygame.draw.ellipse(
                fantasma,
                cor_aura,
                (cx - 19 - expand, 39 - expand // 2, (19 + expand) * 2, 48 + expand)
            )

        pygame.draw.circle(fantasma, (10, 8, 16, int(215 * fator_tonto)), (cx, 28), 12)
        corpo_pts = [(cx - 17, 44), (cx + 17, 44), (cx + 13, 84), (cx - 13, 84)]
        pygame.draw.polygon(fantasma, (10, 8, 16, int(195 * fator_tonto)), corpo_pts)
        pygame.draw.ellipse(fantasma, (10, 8, 16, int(205 * fator_tonto)), (cx - 18, 38, 36, 18))

        if not self.esta_tonto:
            pygame.draw.circle(fantasma, (185, 175, 205, 130), (cx - 4, 27), 2)
            pygame.draw.circle(fantasma, (185, 175, 205, 130), (cx + 4, 27), 2)

        inicio_fade = 54
        fim_fade = 98
        for y in range(inicio_fade, h):
            if y >= fim_fade:
                fator_manter = 0.0
            else:
                progresso = (y - inicio_fade) / (fim_fade - inicio_fade)
                fator_manter = max(0.0, (1.0 - progresso) ** 1.6)

            for x in range(w):
                r, g, b, a = fantasma.get_at((x, y))
                if a > 0:
                    fantasma.set_at((x, y), (r, g, b, int(a * fator_manter)))

        superficie.blit(fantasma, (tx - cx, ty - 88))


class Bigon:
    """Inimigo 'Peso na Consciência': Bigorna de cobre com asas enferrujadas que paira acima do jogador."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 500.0
        self.z_pairar = 54.0
        self.raio = 30

        self.estado = "DORMINDO"
        self.timer = random.uniform(4.5, 6.5)
        self.penas_soltas = 0
        self.timer_pena = 0.0
        self.penas = []

        self.batidas_na_onda = 0
        self.max_batidas_onda = 3
        self.cooldown_batida = 0.0

        self.fase_asa = 0.0
        self.motivo_morte = "BATEU NO BIGON 3 VEZES!"

    @property
    def sort_y(self):
        return self.y + 1.0

    @property
    def ativo_no_ceu(self):
        return self.estado in ("PENAS", "DESCENDO", "PAIRANDO", "SUBINDO", "REBATIDO")

    def soltar_pena(self, jogador):
        self.penas.append({
            "x": jogador.x + random.uniform(-24, 24),
            "y": jogador.y + random.uniform(-18, 18),
            "z": random.uniform(220.0, 290.0),
            "vz": random.uniform(95.0, 125.0),
            "fase": random.uniform(0, math.pi * 2),
            "vida": 2.4,
            "oxidada": random.choice([True, False])
        })

    def rebater_com_parry(self):
        self.estado = "REBATIDO"
        self.timer = 0.0
        self.cooldown_batida = 0.5

    def atualizar(self, jogador, config, paredes, dt):
        self.fase_asa += dt * (18.0 if self.estado in ("SUBINDO", "REBATIDO") else 10.5)
        if self.cooldown_batida > 0.0:
            self.cooldown_batida = max(0.0, self.cooldown_batida - dt)

        for pena in self.penas[:]:
            pena["fase"] += dt * 5.0
            pena["x"] += math.sin(pena["fase"]) * 0.65
            pena["z"] = max(2.0, pena["z"] - pena["vz"] * dt)
            pena["vida"] -= dt
            if pena["vida"] <= 0.0:
                self.penas.remove(pena)

        if self.estado == "DORMINDO":
            self.timer -= dt
            if self.timer <= 0.0:
                self.estado = "PENAS"
                self.penas_soltas = 1
                self.timer_pena = 0.95
                self.x = jogador.x
                self.y = jogador.y
                self.soltar_pena(jogador)

        elif self.estado == "PENAS":
            self.x = jogador.x
            self.y = jogador.y
            self.timer_pena -= dt

            if self.timer_pena <= 0.0:
                self.penas_soltas += 1
                self.soltar_pena(jogador)
                if self.penas_soltas >= 3:
                    self.estado = "DESCENDO"
                    self.x = jogador.x
                    self.y = jogador.y
                    self.z = 340.0
                else:
                    self.timer_pena = 0.95

        elif self.estado == "DESCENDO":
            self.x = jogador.x
            self.y = jogador.y
            self.z -= 560.0 * dt
            if self.z <= self.z_pairar:
                self.z = self.z_pairar
                self.estado = "PAIRANDO"
                self.timer = random.uniform(3.4, 4.4)

        elif self.estado == "PAIRANDO":
            oscilacao_x = math.sin(self.fase_asa * 0.55) * 3.0
            oscilacao_y = math.cos(self.fase_asa * 0.55) * 2.0
            self.x = jogador.x + oscilacao_x
            self.y = jogador.y + oscilacao_y
            self.z = self.z_pairar + math.sin(self.fase_asa * 0.7) * 3.5

            self.timer -= dt
            if self.timer <= 0.0:
                self.estado = "SUBINDO"

        elif self.estado == "SUBINDO":
            self.z += 340.0 * dt
            if self.z >= 460.0:
                self.estado = "DORMINDO"
                self.timer = random.uniform(5.5, 8.0)

        elif self.estado == "REBATIDO":
            self.z += 980.0 * dt
            if self.z >= 520.0:
                self.estado = "DORMINDO"
                self.timer = random.uniform(6.5, 9.0)

    def jogador_bateu_ao_pular(self, jogador, margem_extra=0.0):
        if self.estado not in ("DESCENDO", "PAIRANDO"):
            return False
        if self.cooldown_batida > 0.0:
            return False

        altura_jogador = jogador.z + (jogador.raio * 2)
        if jogador.z <= 2.0 or altura_jogador < (self.z - 6.0 - margem_extra):
            return False

        dist_xy = math.hypot(jogador.x - self.x, jogador.y - self.y)
        return dist_xy < (jogador.raio + self.raio + margem_extra)

    def registrar_batida_pulo(self, jogador):
        self.cooldown_batida = 0.55
        self.batidas_na_onda += 1

        jogador.vel_z = -4.5
        jogador.z = min(jogador.z, max(0.0, self.z - jogador.raio * 2 - 4.0))
        jogador.aplicar_lentidao_bigon(duracao=1.35)
        return self.batidas_na_onda >= self.max_batidas_onda

    def desenhar_sombra(self, superficie, camera):
        from main import mundo_para_tela, INCLINACAO_Y, COR_SOMBRA

        for pena in self.penas:
            sx, sy = mundo_para_tela(pena["x"], pena["y"], 0, camera)
            pygame.draw.ellipse(superficie, COR_SOMBRA, (sx - 5, sy - 3, 10, 6))

        if self.estado not in ("DESCENDO", "PAIRANDO", "SUBINDO", "REBATIDO"):
            return

        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        fator_altura = max(0.35, min(1.0, 1.0 - (self.z / 420.0)))
        largura = int(68 * fator_altura)
        altura = int(44 * INCLINACAO_Y * fator_altura)

        sombra_surf = pygame.Surface((largura + 8, altura + 8), pygame.SRCALPHA)
        alpha = int(155 * fator_altura)
        pygame.draw.ellipse(sombra_surf, (12, 10, 14, alpha), (4, 4, largura, altura))
        if self.estado == "PAIRANDO":
            pygame.draw.ellipse(sombra_surf, (215, 115, 45, alpha), (4, 4, largura, altura), 2)
        superficie.blit(sombra_surf, (sx - (largura + 8) // 2, sy - (altura + 8) // 2))

    def desenhar(self, superficie, camera):
        from main import mundo_para_tela

        for pena in self.penas:
            px, py = mundo_para_tela(pena["x"], pena["y"], pena["z"], camera)
            inclinacao = math.sin(pena["fase"]) * 0.45
            cor_pena = (82, 152, 118) if pena["oxidada"] else (214, 114, 48)
            cor_haste = (240, 165, 95)

            ponta1 = (px - int(math.cos(inclinacao) * 9), py - int(math.sin(inclinacao) * 9))
            ponta2 = (px + int(math.cos(inclinacao) * 9), py + int(math.sin(inclinacao) * 9))
            pygame.draw.ellipse(superficie, cor_pena, (px - 7, py - 3, 14, 7))
            pygame.draw.line(superficie, cor_haste, ponta1, ponta2, 2)

        if self.estado not in ("DESCENDO", "PAIRANDO", "SUBINDO", "REBATIDO"):
            return

        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        bater_asa = math.sin(self.fase_asa) * 11.0

        cor_asa_cobre = (212, 106, 42)
        cor_asa_ferrugem = (158, 72, 28)
        cor_asa_verde = (78, 152, 114)

        for lado in (-1, 1):
            base_x = tx + lado * 18
            base_y = ty - 22
            ponta_x = tx + lado * 46
            ponta_y = ty - 34 + int(bater_asa)
            meio_x = tx + lado * 33
            meio_y = ty - 14 + int(bater_asa * 0.5)

            pts_asa = [(base_x, base_y - 4), (ponta_x, ponta_y), (meio_x, meio_y), (base_x, base_y + 6)]
            pygame.draw.polygon(superficie, cor_asa_cobre, pts_asa)
            pygame.draw.polygon(superficie, cor_asa_ferrugem, pts_asa, 2)

            pygame.draw.circle(superficie, cor_asa_verde, (tx + lado * 31, ty - 24 + int(bater_asa * 0.5)), 5)
            pygame.draw.circle(superficie, cor_asa_verde, (tx + lado * 40, ty - 30 + int(bater_asa * 0.8)), 3)

        cor_cobre_claro = (232, 134, 66)
        cor_cobre_medio = (196, 98, 42)
        cor_cobre_escuro = (135, 62, 26)
        cor_azinhavre = (76, 148, 112)

        base_pts = [(tx - 24, ty), (tx + 24, ty), (tx + 18, ty - 9), (tx - 18, ty - 9)]
        pygame.draw.polygon(superficie, cor_cobre_escuro, base_pts)
        pygame.draw.polygon(superficie, (95, 42, 18), base_pts, 2)

        pygame.draw.rect(superficie, cor_cobre_medio, (tx - 12, ty - 19, 24, 11))

        topo_pts = [
            (tx - 30, ty - 26),
            (tx - 16, ty - 30),
            (tx + 23, ty - 30),
            (tx + 23, ty - 19),
            (tx - 16, ty - 19),
        ]
        pygame.draw.polygon(superficie, cor_cobre_claro, topo_pts)
        pygame.draw.polygon(superficie, cor_cobre_escuro, topo_pts, 2)

        pygame.draw.circle(superficie, cor_azinhavre, (tx + 11, ty - 24), 4)
        pygame.draw.circle(superficie, cor_azinhavre, (tx - 9, ty - 5), 3)
        pygame.draw.line(superficie, (255, 185, 120), (tx - 13, ty - 28), (tx + 19, ty - 28), 2)


def gerar_inimigos_rodada(config, paredes):
    inimigos = []
    margem = 100
    centro_x = 0.0
    centro_y = config.mapa_profundidade / 2

    if config.perigo_aernis_ativo:
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

    if config.perigo_perseqtor_ativo:
        ang = random.uniform(0, math.pi * 2)
        dist_spawn = min(config.mapa_largura, config.mapa_profundidade) * 0.42
        px = max(-config.mapa_largura / 2 + 60, min(config.mapa_largura / 2 - 60, centro_x + math.cos(ang) * dist_spawn))
        py = max(60, min(config.mapa_profundidade - 60, centro_y + math.sin(ang) * dist_spawn))
        inimigos.append(Perseqtor(px, py))

    if config.perigo_bigon_ativo:
        inimigos.append(Bigon(centro_x, centro_y))

    return inimigos