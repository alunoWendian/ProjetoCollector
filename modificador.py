import pygame
import random
import math


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
        self.stacks_escorregou = 0
        self.max_stacks_escorregou = 3
        self.stacks_brochou = 0
        self.max_stacks_brochou = 3
        self.stacks_volta_aqui = 0          # Modificador acumulável: cristais fogem
        self.stacks_cabuum = 0              # Modificador acumulável: +3 minas por stack
        self.explosoes_mina_sofridas = 0    # 3 explosões = Game Over
        self.max_explosoes_mina = 3
        self.stacks_de_novo = 0             # Modificador acumulável raro: +1 escolha de carta por onda
        self.ossos_vidro_ativo = False      # Modificador único: remove o Parry
        self.errei_conta_ativo = False      # Modificador único: limita multiplicador a x3, x2, x1

        # Controle dos Perigos únicos ativos
        self.perigo_aernis_ativo = False
        self.perigo_mestre_ativo = False
        self.perigo_perseqtor_ativo = False
        self.perigo_bigon_ativo = False
        self.perigo_propaganda_ativo = False

        # Controle de progressão de seleções na run
        self.escolhas_cartas_realizadas = 0

        # Sistema de Tempo por Onda e Multiplicador Regressivo
        self.tempo_onda = 0.0
        self.multiplicador_onda_atual = 1


def velocidade_fuga_cristal(stacks):
    """Calcula a velocidade dos cristais fugitivos com base nos acúmulos de 'Volta Aqui!'."""
    if stacks <= 0:
        return 0.0
    return 1.8 + (stacks - 1) * 1.2


def calcular_limites_tempo_onda(config):
    """Calcula tempos justos escalando com cristais, tamanho da arena e perigos."""
    fator_cristais = config.qtd_cristais * 0.56
    fator_arena = ((config.mapa_largura - 1800) / 300.0) * 2.4
    fator_perigos = (
        (1.8 if config.perigo_mestre_ativo else 0.0) +
        (1.2 if config.perigo_aernis_ativo else 0.0) +
        (1.0 if config.perigo_perseqtor_ativo else 0.0) +
        (1.3 if config.perigo_bigon_ativo else 0.0) +
        (1.1 if config.perigo_propaganda_ativo else 0.0) +
        (config.stacks_maze * 0.9) +
        (config.stacks_volta_aqui * 0.7) +
        (config.stacks_cabuum * 0.6)
    )
    tempo_base = 4.5 + fator_cristais + fator_arena + fator_perigos
    passo = 5.5 + (config.qtd_cristais * 0.10)
    return (
        tempo_base,
        tempo_base + passo,
        tempo_base + passo * 2.0,
        tempo_base + passo * 3.0,
    )


def calcular_multiplicador_por_tempo(tempo, config):
    """Retorna o multiplicador (5..1 normal ou 3..1 com 'Errei a Conta')."""
    t5, t4, t3, t2 = calcular_limites_tempo_onda(config)

    if config.errei_conta_ativo:
        limite_x3 = t4
        limite_x2 = t2
        if tempo <= limite_x3:
            return 3
        elif tempo <= limite_x2:
            return 2
        return 1

    if tempo <= t5:
        return 5
    elif tempo <= t4:
        return 4
    elif tempo <= t3:
        return 3
    elif tempo <= t2:
        return 2
    return 1


def cor_multiplicador(mult):
    """Retorna a cor temática para cada nível de multiplicador."""
    cores = {
        5: (255, 215, 70),    # Dourado intenso
        4: (80, 240, 255),    # Ciano elétrico
        3: (125, 245, 145),   # Verde vibrante
        2: (255, 165, 80),    # Laranja
        1: (185, 185, 195),   # Neutro
    }
    return cores.get(mult, (185, 185, 195))


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
        from main import mundo_para_tela, COR_SOMBRA

        p1 = mundo_para_tela(self.min_x - 4, self.min_y - 4, 0, camera)
        p2 = mundo_para_tela(self.max_x + 4, self.min_y - 4, 0, camera)
        p3 = mundo_para_tela(self.max_x + 4, self.max_y + 4, 0, camera)
        p4 = mundo_para_tela(self.min_x - 4, self.max_y + 4, 0, camera)
        pygame.draw.polygon(superficie, COR_SOMBRA, [p1, p2, p3, p4])

    def desenhar(self, superficie, camera):
        from main import mundo_para_tela, COR_PAREDE_TOPO, COR_PAREDE_FRENTE, COR_PAREDE_BORDA

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


class Mina:
    """Mina terrestre gerada pelo modificador 'Cabuum!'. Pode ser pulada ou desarmada no Parry."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0.0
        self.raio = 16
        self.altura_pulo_seguro = 16.0
        self.fase_pulso = random.uniform(0, math.pi * 2)

    @property
    def sort_y(self):
        return self.y - 2.0

    def atualizar(self, dt):
        self.fase_pulso += dt * 5.5

    def colidiu_com_jogador(self, jogador, margem_extra=0.0):
        if jogador.z > self.altura_pulo_seguro:
            return False
        dist_xy = math.hypot(jogador.x - self.x, jogador.y - self.y)
        return dist_xy < (jogador.raio + self.raio - 3 + margem_extra)

    def desenhar_sombra(self, superficie, camera):
        from main import mundo_para_tela, INCLINACAO_Y, COR_SOMBRA

        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        largura = int(self.raio * 2.2)
        altura = int(self.raio * 2.2 * INCLINACAO_Y)
        pygame.draw.ellipse(superficie, COR_SOMBRA, (sx - largura // 2, sy - altura // 2, largura, altura))

    def desenhar(self, superficie, camera):
        from main import mundo_para_tela, INCLINACAO_Y

        tx, ty = mundo_para_tela(self.x, self.y, 0, camera)
        pulso = 0.5 + 0.5 * math.sin(self.fase_pulso)

        raio_anel = int(self.raio + 4 + pulso * 3)
        rect_anel = pygame.Rect(
            tx - raio_anel,
            ty - int(raio_anel * INCLINACAO_Y),
            raio_anel * 2,
            int(raio_anel * 2 * INCLINACAO_Y)
        )
        pygame.draw.ellipse(superficie, (190, 65, 45), rect_anel, 1)

        largura_base = int(self.raio * 2.0)
        altura_base = int(self.raio * 2.0 * INCLINACAO_Y)
        rect_base = pygame.Rect(tx - largura_base // 2, ty - altura_base // 2 - 2, largura_base, altura_base)
        pygame.draw.ellipse(superficie, (52, 54, 62), rect_base)
        pygame.draw.ellipse(superficie, (28, 30, 36), rect_base, 2)

        for ang_deg in (30, 150, 210, 330):
            ang = math.radians(ang_deg)
            px = tx + int(math.cos(ang) * (self.raio - 1))
            py = (ty - 2) + int(math.sin(ang) * (self.raio - 1) * INCLINACAO_Y)
            pygame.draw.circle(superficie, (95, 100, 112), (px, py), 3)

        cor_led = (255, int(65 + 135 * pulso), 40)
        pygame.draw.circle(superficie, (30, 26, 30), (tx, ty - 4), 6)
        pygame.draw.circle(superficie, cor_led, (tx, ty - 4), 4)


class Cristal:
    def __init__(self, x, y, fugitivo=False, z=8):
        self.x = x
        self.y = y
        self.z_base = z
        self.z = z
        self.raio = 10
        self.fase_flutuacao = random.uniform(0, math.pi * 2)

        # Propriedades do modificador 'Volta Aqui!'
        self.fugitivo = fugitivo
        self.correndo = False
        self.dir_fuga_x = 1.0
        self.dir_fuga_y = 0.0
        self.fase_corrida = random.uniform(0, math.pi * 2)

    @property
    def sort_y(self):
        return self.y

    def resolver_colisao_paredes(self, paredes):
        raio_col = self.raio + 4
        for parede in paredes:
            mais_prox_x = max(parede.min_x, min(self.x, parede.max_x))
            mais_prox_y = max(parede.min_y, min(self.y, parede.max_y))
            dx = self.x - mais_prox_x
            dy = self.y - mais_prox_y
            dist_sq = dx * dx + dy * dy
            if dist_sq < raio_col * raio_col:
                dist = math.sqrt(dist_sq)
                if dist > 0.0001:
                    sobreposicao = raio_col - dist
                    self.x += (dx / dist) * sobreposicao
                    self.y += (dy / dist) * sobreposicao
                else:
                    self.y = parede.max_y + raio_col

    def atualizar(self, tempo, jogador, config, paredes, dt):
        self.correndo = False

        if self.fugitivo and config.stacks_volta_aqui > 0:
            dx = self.x - jogador.x
            dy = self.y - jogador.y
            dist = math.hypot(dx, dy)
            raio_susto = 310.0

            if dist < raio_susto:
                self.correndo = True
                vel = velocidade_fuga_cristal(config.stacks_volta_aqui)

                if dist > 0.001:
                    fx, fy = dx / dist, dy / dist
                else:
                    ang = random.uniform(0, math.pi * 2)
                    fx, fy = math.cos(ang), math.sin(ang)

                margem_borda = 130.0
                limite_x = (config.mapa_largura / 2) - self.raio - 10
                if self.x < -limite_x + margem_borda:
                    fx += 0.85
                elif self.x > limite_x - margem_borda:
                    fx -= 0.85

                if self.y < self.raio + margem_borda:
                    fy += 0.85
                elif self.y > config.mapa_profundidade - self.raio - margem_borda:
                    fy -= 0.85

                comp = math.hypot(fx, fy)
                if comp > 0.001:
                    fx /= comp
                    fy /= comp

                self.dir_fuga_x = fx
                self.dir_fuga_y = fy
                self.fase_corrida += dt * (11.0 + vel * 2.2)

                self.x += fx * vel
                self.y += fy * vel

                self.x = max(-limite_x, min(limite_x, self.x))
                self.y = max(self.raio + 10, min(config.mapa_profundidade - self.raio - 10, self.y))
                self.resolver_colisao_paredes(paredes)

        if self.correndo:
            self.z = self.z_base + abs(math.sin(self.fase_corrida)) * 4.5
        else:
            self.z = self.z_base + math.sin(tempo * 4 + self.fase_flutuacao) * 4

    def desenhar_sombra(self, superficie, camera):
        from main import mundo_para_tela, COR_SOMBRA

        sx, sy = mundo_para_tela(self.x, self.y, 0, camera)
        rect_sombra = pygame.Rect(sx - 8, sy - 5, 16, 10)
        pygame.draw.ellipse(superficie, COR_SOMBRA, rect_sombra)

    def desenhar(self, superficie, camera):
        from main import mundo_para_tela, COR_CRISTAL, COR_CRISTAL_BRILHO

        tx, ty = mundo_para_tela(self.x, self.y, self.z, camera)
        centro_y = ty - self.raio

        if self.fugitivo:
            passo = math.sin(self.fase_corrida) * 4.0 if self.correndo else 0.0
            dir_olhar = 1 if self.dir_fuga_x >= 0 else -1
            cor_bota = (218, 128, 52)
            cor_sola = (130, 68, 28)

            for i, lado in enumerate((-1, 1)):
                desloc = int(passo if i == 0 else -passo)
                bx = tx + lado * 5 + desloc
                by = centro_y + 8 - abs(desloc) // 2
                rect_bota = pygame.Rect(bx - 4 + (dir_olhar if self.correndo else 0), by, 8, 5)
                pygame.draw.rect(superficie, cor_bota, rect_bota, border_radius=2)
                pygame.draw.line(superficie, cor_sola, (rect_bota.left, rect_bota.bottom - 1), (rect_bota.right - 1, rect_bota.bottom - 1), 1)

        pygame.draw.circle(superficie, COR_CRISTAL, (tx, centro_y), self.raio)
        pygame.draw.circle(superficie, COR_CRISTAL_BRILHO, (tx - 3, centro_y - 3), 3)


def desenhar_icone_carta(superficie, id_mod, centro, cor_destaque):
    """Desenha um emblema vetorial exclusivo para cada tipo de modificador ou perigo."""
    from main import COR_JOGADOR, COR_JOGADOR_BORDA, COR_CRISTAL, COR_CRISTAL_BRILHO

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

    elif id_mod == "VOLTA_AQUI":
        pygame.draw.line(superficie, (130, 235, 255), (cx - 25, cy - 11), (cx - 14, cy - 11), 2)
        pygame.draw.line(superficie, (130, 235, 255), (cx - 28, cy - 3), (cx - 16, cy - 3), 2)
        pygame.draw.line(superficie, (130, 235, 255), (cx - 24, cy + 5), (cx - 14, cy + 5), 2)

        ccx, ccy = cx + 4, cy - 5
        pygame.draw.circle(superficie, COR_CRISTAL, (ccx, ccy), 13)
        pygame.draw.circle(superficie, COR_CRISTAL_BRILHO, (ccx - 3, ccy - 4), 4)

        cor_bota = (224, 134, 54)
        cor_cano = (186, 98, 36)
        pygame.draw.line(superficie, (200, 220, 235), (ccx - 4, ccy + 10), (ccx - 11, ccy + 15), 2)
        pygame.draw.rect(superficie, cor_bota, (ccx - 17, ccy + 13, 10, 6), border_radius=2)
        pygame.draw.rect(superficie, cor_cano, (ccx - 14, ccy + 11, 5, 4), border_radius=1)

        pygame.draw.line(superficie, (200, 220, 235), (ccx + 4, ccy + 10), (ccx + 11, ccy + 16), 2)
        pygame.draw.rect(superficie, cor_bota, (ccx + 8, ccy + 14, 11, 6), border_radius=2)
        pygame.draw.rect(superficie, cor_cano, (ccx + 8, ccy + 12, 5, 4), border_radius=1)

    elif id_mod == "CABUUM":
        bx, by = cx - 2, cy + 4
        pygame.draw.circle(superficie, (52, 56, 66), (bx, by), 16)
        pygame.draw.circle(superficie, (95, 102, 118), (bx, by), 16, 2)
        pygame.draw.circle(superficie, (125, 132, 148), (bx - 5, by - 5), 4)

        pygame.draw.rect(superficie, (80, 84, 96), (bx + 6, by - 18, 7, 6), border_radius=1)
        pygame.draw.lines(superficie, (210, 175, 115), False, [(bx + 11, by - 18), (bx + 16, by - 24), (bx + 21, by - 22)], 2)

        fx, fy = bx + 22, by - 22
        pygame.draw.circle(superficie, (255, 120, 45), (fx, fy), 5)
        pygame.draw.circle(superficie, (255, 235, 110), (fx, fy), 2)
        for ang_deg in range(0, 360, 60):
            ang = math.radians(ang_deg)
            pygame.draw.line(
                superficie,
                (255, 195, 70),
                (fx + math.cos(ang) * 4, fy + math.sin(ang) * 4),
                (fx + math.cos(ang) * 8, fy + math.sin(ang) * 8),
                2
            )

    elif id_mod == "DE_NOVO":
        # Duas setas curvas formando um ciclo de repetição (+1 escolha)
        rect_arco = pygame.Rect(cx - 20, cy - 20, 40, 40)
        pygame.draw.arc(superficie, cor_destaque, rect_arco, math.radians(25), math.radians(175), 4)
        pygame.draw.arc(superficie, cor_destaque, rect_arco, math.radians(205), math.radians(355), 4)

        # Ponta da seta superior direita
        p1 = (cx + 18, cy - 8)
        pygame.draw.polygon(superficie, cor_destaque, [p1, (p1[0] - 9, p1[1] - 3), (p1[0] - 2, p1[1] - 10)])

        # Ponta da seta inferior esquerda
        p2 = (cx - 18, cy + 8)
        pygame.draw.polygon(superficie, cor_destaque, [p2, (p2[0] + 9, p2[1] + 3), (p2[0] + 2, p2[1] + 10)])

        # Brilho "+1" central
        pygame.draw.line(superficie, (255, 255, 255), (cx - 6, cy), (cx + 2, cy), 2)
        pygame.draw.line(superficie, (255, 255, 255), (cx - 2, cy - 4), (cx - 2, cy + 4), 2)
        pygame.draw.line(superficie, (255, 255, 255), (cx + 6, cy - 4), (cx + 6, cy + 4), 2)

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

    elif id_mod == "ESCORREGOU":
        cor_banana = (255, 225, 55)
        cor_sombra_banana = (210, 165, 25)
        cor_ponta = (110, 75, 35)

        pygame.draw.rect(superficie, cor_ponta, (cx - 3, cy - 23, 6, 8), border_radius=2)

        aba_esq = [(cx - 2, cy - 15), (cx - 12, cy - 4), (cx - 22, cy + 12), (cx - 13, cy + 15), (cx - 4, cy + 1)]
        aba_meio = [(cx - 3, cy - 15), (cx + 3, cy - 15), (cx + 6, cy + 16), (cx - 4, cy + 18)]
        aba_dir = [(cx + 2, cy - 15), (cx + 13, cy - 3), (cx + 22, cy + 12), (cx + 13, cy + 15), (cx + 4, cy + 1)]

        pygame.draw.polygon(superficie, cor_banana, aba_esq)
        pygame.draw.polygon(superficie, cor_sombra_banana, aba_esq, 2)
        pygame.draw.polygon(superficie, cor_banana, aba_dir)
        pygame.draw.polygon(superficie, cor_sombra_banana, aba_dir, 2)
        pygame.draw.polygon(superficie, (255, 240, 110), aba_meio)
        pygame.draw.polygon(superficie, cor_sombra_banana, aba_meio, 2)

    elif id_mod == "BROCHOU":
        rect_parede = pygame.Rect(cx - 7, cy - 24, 14, 48)
        pygame.draw.rect(superficie, (115, 72, 78), rect_parede, border_radius=2)
        pygame.draw.rect(superficie, cor_destaque, rect_parede, 2, border_radius=2)

        rachadura = [
            (cx - 1, cy - 22),
            (cx + 4, cy - 11),
            (cx - 4, cy - 1),
            (cx + 3, cy + 9),
            (cx - 2, cy + 21)
        ]
        pygame.draw.lines(superficie, (22, 22, 28), False, rachadura, 3)

    elif id_mod == "OSSOS_VIDRO":
        cor_osso = (210, 238, 250)
        cor_borda_osso = (120, 190, 225)
        for ang_deg in (42, -42):
            ang = math.radians(ang_deg)
            dx = math.cos(ang) * 18
            dy = math.sin(ang) * 18
            p1 = (cx - dx, cy - dy)
            p2 = (cx + dx, cy + dy)
            pygame.draw.line(superficie, cor_borda_osso, p1, p2, 8)
            pygame.draw.line(superficie, cor_osso, p1, p2, 5)
            perp_x = -math.sin(ang) * 3.5
            perp_y = math.cos(ang) * 3.5
            for ponta in (p1, p2):
                for sinal in (-1, 1):
                    bx = int(ponta[0] + perp_x * sinal)
                    by = int(ponta[1] + perp_y * sinal)
                    pygame.draw.circle(superficie, cor_osso, (bx, by), 4)
                    pygame.draw.circle(superficie, cor_borda_osso, (bx, by), 4, 1)

        pygame.draw.line(superficie, (22, 22, 28), (cx - 4, cy - 5), (cx + 2, cy + 1), 2)
        pygame.draw.line(superficie, (22, 22, 28), (cx + 2, cy + 1), (cx - 2, cy + 6), 2)

    elif id_mod == "ERREI_CONTA":
        pygame.draw.line(superficie, (255, 95, 110), (cx - 23, cy), (cx - 9, cy), 5)
        x_cx = cx + 8
        pygame.draw.line(superficie, cor_destaque, (x_cx - 11, cy - 11), (x_cx + 11, cy + 11), 5)
        pygame.draw.line(superficie, cor_destaque, (x_cx - 11, cy + 11), (x_cx + 11, cy - 11), 5)

    elif id_mod == "AERNIS03":
        pontos_serra = []
        num_pontas = 4
        for i in range(num_pontas * 2):
            ang = -math.pi / 4 + (i * math.pi / num_pontas)
            r = 26 if i % 2 == 0 else 11
            pontos_serra.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))

        pygame.draw.polygon(superficie, (195, 205, 215), pontos_serra)
        pygame.draw.polygon(superficie, (95, 105, 118), pontos_serra, 2)
        pygame.draw.circle(superficie, (140, 150, 165), (cx, cy), 8)
        pygame.draw.circle(superficie, (22, 22, 28), (cx, cy), 4)

    elif id_mod == "MESTRE":
        losango = [(cx, cy - 21), (cx + 28, cy), (cx, cy + 21), (cx - 28, cy)]
        pygame.draw.polygon(superficie, (85, 12, 18), losango)
        pygame.draw.polygon(superficie, (255, 35, 45), losango, 3)
        pygame.draw.circle(superficie, (255, 40, 50), (cx, cy), 6)

    elif id_mod == "PERSEQTOR":
        icone_surf = pygame.Surface((72, 72), pygame.SRCALPHA)

        px = 26
        for c in range(3):
            exp = (3 - c) * 3
            al = 28 + c * 28
            pygame.draw.circle(icone_surf, (20, 16, 30, al), (px, 21), 8 + exp)
            pygame.draw.ellipse(icone_surf, (20, 16, 30, al), (px - 12 - exp, 28, (12 + exp) * 2, 28))

        pygame.draw.circle(icone_surf, (10, 8, 16, 230), (px, 21), 8)
        pygame.draw.polygon(
            icone_surf,
            (10, 8, 16, 215),
            [(px - 11, 30), (px + 11, 30), (px + 8, 52), (px - 8, 52)]
        )
        pygame.draw.circle(icone_surf, (215, 195, 245, 210), (px + 1, 20), 2)
        pygame.draw.circle(icone_surf, (215, 195, 245, 210), (px + 6, 20), 2)

        for y in range(34, 62):
            prog = min(1.0, (y - 34) / 20.0)
            manter = max(0.0, 1.0 - prog)
            for x in range(8, 46):
                r, g, b, a = icone_surf.get_at((x, y))
                if a > 0:
                    icone_surf.set_at((x, y), (r, g, b, int(a * manter)))

        jx, jy = 46, 46
        pygame.draw.ellipse(icone_surf, (14, 14, 18, 170), (jx - 10, jy + 8, 20, 7))
        pygame.draw.circle(icone_surf, COR_JOGADOR, (jx, jy), 11)
        pygame.draw.circle(icone_surf, COR_JOGADOR_BORDA, (jx, jy), 11, 2)

        superficie.blit(icone_surf, (cx - 36, cy - 34))

    elif id_mod == "BIGON":
        cor_mente = (218, 145, 168)
        cor_mente_borda = (155, 88, 112)

        pygame.draw.ellipse(superficie, cor_mente, (cx - 19, cy + 4, 21, 16))
        pygame.draw.ellipse(superficie, cor_mente, (cx - 2, cy + 4, 21, 16))
        pygame.draw.ellipse(superficie, cor_mente_borda, (cx - 19, cy + 4, 21, 16), 2)
        pygame.draw.ellipse(superficie, cor_mente_borda, (cx - 2, cy + 4, 21, 16), 2)
        pygame.draw.line(superficie, cor_mente_borda, (cx - 11, cy + 10), (cx - 5, cy + 12), 2)
        pygame.draw.line(superficie, cor_mente_borda, (cx + 5, cy + 12), (cx + 11, cy + 10), 2)

        cor_cobre = (224, 118, 52)
        cor_cobre_esc = (138, 64, 26)
        cor_verde = (78, 152, 114)

        pygame.draw.polygon(
            superficie,
            cor_cobre_esc,
            [(cx - 14, cy + 4), (cx + 14, cy + 4), (cx + 10, cy - 2), (cx - 10, cy - 2)]
        )
        pygame.draw.rect(superficie, cor_cobre, (cx - 7, cy - 9, 14, 7))
        topo_bigorna = [
            (cx - 21, cy - 14),
            (cx - 10, cy - 17),
            (cx + 16, cy - 17),
            (cx + 16, cy - 9),
            (cx - 10, cy - 9),
        ]
        pygame.draw.polygon(superficie, cor_cobre, topo_bigorna)
        pygame.draw.polygon(superficie, cor_cobre_esc, topo_bigorna, 2)
        pygame.draw.circle(superficie, cor_verde, (cx + 7, cy - 13), 3)

    elif id_mod == "PROPAGANDA":
        rect_win = pygame.Rect(cx - 23, cy - 18, 46, 36)
        pygame.draw.rect(superficie, (192, 192, 192), rect_win)
        pygame.draw.line(superficie, (255, 255, 255), rect_win.topleft, rect_win.topright, 2)
        pygame.draw.line(superficie, (255, 255, 255), rect_win.topleft, rect_win.bottomleft, 2)
        pygame.draw.line(superficie, (70, 70, 75), rect_win.bottomleft, rect_win.bottomright, 2)
        pygame.draw.line(superficie, (70, 70, 75), rect_win.topright, rect_win.bottomright, 2)

        pygame.draw.rect(superficie, (0, 0, 128), (rect_win.x + 2, rect_win.y + 2, rect_win.width - 4, 8))

        ccy = rect_win.y + 22
        pygame.draw.circle(superficie, (225, 32, 42), (cx, ccy), 10)
        pygame.draw.circle(superficie, (130, 18, 25), (cx, ccy), 10, 2)
        pygame.draw.line(superficie, (255, 255, 255), (cx - 4, ccy - 4), (cx + 4, ccy + 4), 2)
        pygame.draw.line(superficie, (255, 255, 255), (cx - 4, ccy + 4), (cx + 4, ccy - 4), 2)


class CartaModificador:
    def __init__(self, id_mod, tipo, indice, total_cartas, titulo, subtitulo, detalhe, cor_destaque):
        from main import LARGURA, ALTURA

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

    def desenhar(self, superficie, pos_mouse, fonte_titulo, fonte_sub, fonte_detalhe, offset_y=0):
        from main import (
            COR_TEXTO,
            COR_CARTA_FUNDO,
            COR_CARTA_HOVER,
            COR_CARTA_BORDA,
            COR_CARTA_BORDA_HOVER,
            COR_PERIGO_FUNDO,
            COR_PERIGO_HOVER,
            COR_PERIGO_BORDA,
            COR_PERIGO_BORDA_HOVER,
        )

        rect_base = self.rect.move(0, offset_y)
        hover = (offset_y == 0) and rect_base.collidepoint(pos_mouse)
        rect_desenho = rect_base.move(0, -10) if hover else rect_base

        eh_perigo = (self.tipo == "PERIGO")
        if eh_perigo:
            cor_fundo = COR_PERIGO_HOVER if hover else COR_PERIGO_FUNDO
            cor_borda = COR_PERIGO_BORDA_HOVER if hover else COR_PERIGO_BORDA
        else:
            cor_fundo = COR_CARTA_HOVER if hover else COR_CARTA_FUNDO
            cor_borda = COR_CARTA_BORDA_HOVER if hover else COR_CARTA_BORDA

        pygame.draw.rect(superficie, cor_fundo, rect_desenho, border_radius=12)
        pygame.draw.rect(superficie, cor_borda, rect_desenho, 3 if hover else 2, border_radius=12)

        if self.tipo == "PERIGO":
            texto_tag = "PERIGO ÚNICO"
            cor_tag = (255, 85, 95)
        elif self.tipo == "MOD_UNICO":
            texto_tag = "MODIFICADOR ÚNICO"
            cor_tag = (165, 225, 255)
        elif self.tipo == "MOD_RARO":
            texto_tag = "MODIFICADOR RARO"
            cor_tag = (235, 145, 255)
        else:
            texto_tag = "MODIFICADOR"
            cor_tag = (150, 160, 180)

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
                fugitivo = (config.stacks_volta_aqui > 0) and (random.random() < 0.25)
                cristais.append(Cristal(cx, cy, fugitivo=fugitivo))
                break

    return cristais


def gerar_minas_rodada(config, paredes, cristais):
    """Gera 3 minas por acúmulo de 'Cabuum!', mantendo distância segura de cristais e spawn."""
    total_minas = config.stacks_cabuum * 3
    if total_minas <= 0:
        return []

    minas = []
    margem = 75
    centro_x = 0.0
    centro_y = config.mapa_profundidade / 2
    dist_min_cristal = 115.0
    dist_min_entre_minas = 85.0

    for _ in range(total_minas):
        for _tentativa in range(120):
            mx = random.uniform(-config.mapa_largura / 2 + margem, config.mapa_largura / 2 - margem)
            my = random.uniform(margem, config.mapa_profundidade - margem)

            if math.hypot(mx - centro_x, my - centro_y) < 170:
                continue

            dentro_parede = False
            for parede in paredes:
                prox_x = max(parede.min_x, min(mx, parede.max_x))
                prox_y = max(parede.min_y, min(my, parede.max_y))
                if math.hypot(mx - prox_x, my - prox_y) < 36:
                    dentro_parede = True
                    break
            if dentro_parede:
                continue

            perto_cristal = any(math.hypot(mx - c.x, my - c.y) < dist_min_cristal for c in cristais)
            if perto_cristal:
                continue

            perto_mina = any(math.hypot(mx - m.x, my - m.y) < dist_min_entre_minas for m in minas)
            if perto_mina:
                continue

            minas.append(Mina(mx, my))
            break

    return minas


def gerar_opcoes_cartas(config):
    vel_fuga_atual = velocidade_fuga_cristal(config.stacks_volta_aqui)
    vel_fuga_prox = velocidade_fuga_cristal(config.stacks_volta_aqui + 1)

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
        (
            "VOLTA_AQUI",
            "MODIFICADOR",
            "Volta Aqui!",
            "Os cristais se movem\npara longe de você",
            f"25% fogem | Vel: {vel_fuga_atual:.1f} -> {vel_fuga_prox:.1f}",
            (95, 235, 255)
        ),
        (
            "CABUUM",
            "MODIFICADOR",
            "Cabuum!",
            "Adiciona minas\nna arena",
            f"+3 minas ({config.stacks_cabuum * 3} -> {(config.stacks_cabuum + 1) * 3})\n3 explosões = Game Over",
            (255, 125, 55)
        ),
    ]

    # Modificador RARO e acumulável: De novo (~22% de chance de entrar no pool da seleção)
    if config.escolhas_cartas_realizadas > 0 and random.random() < 0.22:
        escolhas_atual = 1 + config.stacks_de_novo
        escolhas_prox = escolhas_atual + 1
        disponiveis.append(
            (
                "DE_NOVO",
                "MOD_RARO",
                "De novo",
                "Faz escolher\nmais uma vez",
                f"Escolhas por onda: {escolhas_atual} -> {escolhas_prox}\n(Raro e acumulável)",
                (225, 125, 255)
            )
        )

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

    if config.stacks_escorregou < config.max_stacks_escorregou:
        slide_atual_pct = int(round((1.0 - config.stacks_escorregou * 0.25) * 100))
        slide_prox_pct = int(round((1.0 - (config.stacks_escorregou + 1) * 0.25) * 100))
        disponiveis.append(
            (
                "ESCORREGOU",
                "MODIFICADOR",
                "Escorregou na Real",
                "Slide/Air Slide\nserão mais fracos",
                f"Potência Slide: {slide_atual_pct}% -> {slide_prox_pct}%\n({config.stacks_escorregou}/{config.max_stacks_escorregou} escolhidos)",
                (255, 215, 65)
            )
        )

    if config.stacks_brochou < config.max_stacks_brochou:
        wk_atual_pct = int(round((1.0 - config.stacks_brochou * 0.25) * 100))
        wk_prox_pct = int(round((1.0 - (config.stacks_brochou + 1) * 0.25) * 100))
        disponiveis.append(
            (
                "BROCHOU",
                "MODIFICADOR",
                "Brochou",
                "Wall Kick\nMais fraco",
                f"Impulso WK: {wk_atual_pct}% -> {wk_prox_pct}%\n({config.stacks_brochou}/{config.max_stacks_brochou} escolhidos)",
                (110, 215, 255)
            )
        )

    if not config.ossos_vidro_ativo:
        disponiveis.append(
            (
                "OSSOS_VIDRO",
                "MOD_UNICO",
                "Ossos de Vidro",
                "Remove o Parry",
                "Desativa o Parry pelo resto\nda run (Escolha única)",
                (170, 230, 255)
            )
        )

    if not config.errei_conta_ativo:
        disponiveis.append(
            (
                "ERREI_CONTA",
                "MOD_UNICO",
                "Errei a Conta",
                "Multiplicador de pontos\nreduzido",
                "Limita o multiplicador máximo\npara x3, x2 e x1 (Único)",
                (255, 165, 95)
            )
        )

    if not config.perigo_aernis_ativo:
        disponiveis.append(
            (
                "AERNIS03",
                "PERIGO",
                "Zé do Picadinho",
                "Adiciona Aernis-03\nna arena",
                "Serra defeituosa que quica\npelas paredes (Pule ou dê Parry!)",
                (255, 110, 35)
            )
        )

    if not config.perigo_mestre_ativo:
        disponiveis.append(
            (
                "MESTRE",
                "PERIGO",
                "O Mestre Mandou",
                "Adiciona o Mestre\nno topo da tela",
                "Quando os olhos abrirem,\nfique completamente parado!",
                (255, 55, 65)
            )
        )

    if not config.perigo_perseqtor_ativo:
        disponiveis.append(
            (
                "PERSEQTOR",
                "PERIGO",
                "Atrás de mim?",
                "Adiciona o Perseqtor",
                "Sombra humanoide lenta que\nte persegue atravessando paredes!",
                (185, 145, 235)
            )
        )

    if not config.perigo_bigon_ativo:
        disponiveis.append(
            (
                "BIGON",
                "PERIGO",
                "Peso na Consciência",
                "Adiciona o Bigon",
                "Paira sobre você na 3ª pena;\npular nele 3x = Game Over!",
                (224, 130, 72)
            )
        )

    if not config.perigo_propaganda_ativo:
        disponiveis.append(
            (
                "PROPAGANDA",
                "PERIGO",
                "Propaganda",
                "Adiciona Pop-up",
                "Feche com o mouse ou dê Parry\nno aviso antes de abrir!",
                (120, 185, 255)
            )
        )

    if config.escolhas_cartas_realizadas == 0:
        apenas_perigos = [carta for carta in disponiveis if carta[1] == "PERIGO"]
        if len(apenas_perigos) >= 3:
            disponiveis = apenas_perigos

    qtd_sortear = min(3, len(disponiveis))
    escolhidas = random.sample(disponiveis, qtd_sortear)

    return [
        CartaModificador(id_mod, tipo, i, qtd_sortear, titulo, sub, det, cor)
        for i, (id_mod, tipo, titulo, sub, det, cor) in enumerate(escolhidas)
    ]


def aplicar_modificador(id_mod, config, jogador, mestre, propaganda):
    config.escolhas_cartas_realizadas += 1

    if id_mod == "MAIS":
        config.qtd_cristais += 5
        config.stacks_mais += 1

    elif id_mod == "ESPACOSO":
        config.mapa_largura += 300
        config.mapa_profundidade += 300
        config.stacks_espacoso += 1

    elif id_mod == "VOLTA_AQUI":
        config.stacks_volta_aqui += 1

    elif id_mod == "CABUUM":
        config.stacks_cabuum += 1

    elif id_mod == "DE_NOVO":
        config.stacks_de_novo += 1

    elif id_mod == "LERDO":
        if config.stacks_lerdo < config.max_stacks_lerdo:
            config.stacks_lerdo += 1
            jogador.fator_embalo_mod = max(0.40, 1.0 - (config.stacks_lerdo * 0.20))

    elif id_mod == "ESCORREGOU":
        if config.stacks_escorregou < config.max_stacks_escorregou:
            config.stacks_escorregou += 1
            jogador.fator_slide_mod = max(0.25, 1.0 - (config.stacks_escorregou * 0.25))

    elif id_mod == "BROCHOU":
        if config.stacks_brochou < config.max_stacks_brochou:
            config.stacks_brochou += 1
            jogador.fator_wk_mod = max(0.25, 1.0 - (config.stacks_brochou * 0.25))

    elif id_mod == "MAZE":
        config.stacks_maze += 1

    elif id_mod == "OSSOS_VIDRO":
        config.ossos_vidro_ativo = True
        jogador.parry_bloqueado = True
        jogador.timer_parry_ativo = 0.0

    elif id_mod == "ERREI_CONTA":
        config.errei_conta_ativo = True
        config.multiplicador_onda_atual = min(3, config.multiplicador_onda_atual)

    elif id_mod == "AERNIS03":
        config.perigo_aernis_ativo = True

    elif id_mod == "MESTRE":
        config.perigo_mestre_ativo = True
        mestre.resetar_ciclo()

    elif id_mod == "PERSEQTOR":
        config.perigo_perseqtor_ativo = True

    elif id_mod == "BIGON":
        config.perigo_bigon_ativo = True

    elif id_mod == "PROPAGANDA":
        config.perigo_propaganda_ativo = True
        propaganda.resetar()