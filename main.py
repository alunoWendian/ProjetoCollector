import pygame
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
COR_PARRY = (255, 250, 220)       # Branco-dourado intenso (Parry)
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


def desenhar_fundo_selecao_cartas(superficie, tempo):
    """Bordas diagonais vermelhas nos cantos (estilo Sonic) com chevrons animados ao longo das faixas."""
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((12, 13, 18, 200))

    prog_entrada = min(1.0, tempo / 0.25)
    ease = 1.0 - (1.0 - prog_entrada) ** 3
    recuo = int((1.0 - ease) * 260)

    # --- CANTO SUPERIOR ESQUERDO ---
    off_tl = -recuo
    pts_tl_sombra = [(off_tl, 0), (318 + off_tl, 0), (0, 318 + off_tl)]
    pts_tl_princ = [(off_tl, 0), (288 + off_tl, 0), (0, 288 + off_tl)]
    pts_tl_inner = [(off_tl, 0), (222 + off_tl, 0), (0, 222 + off_tl)]

    pygame.draw.polygon(overlay, (95, 16, 26, 235), pts_tl_sombra)
    pygame.draw.polygon(overlay, (185, 32, 46, 245), pts_tl_princ)
    pygame.draw.polygon(overlay, (130, 20, 32, 245), pts_tl_inner)

    espaco_chev = 44
    desloc_tl = (tempo * 75.0) % espaco_chev
    for k in range(-2, 10):
        dist = k * espaco_chev + desloc_tl
        px = dist + off_tl
        py = 255 - dist + off_tl
        if -40 <= px <= 290 and -40 <= py <= 290:
            pts_c = [
                (px - 10, py - 24),
                (px + 6, py - 24),
                (px + 20, py - 10),
                (px + 6, py + 4),
                (px - 10, py + 4),
                (px + 4, py - 10),
            ]
            pygame.draw.polygon(overlay, (255, 85, 95, 120), pts_c)

    pygame.draw.line(overlay, (255, 75, 88, 255), (288 + off_tl, 0), (0, 288 + off_tl), 4)
    pygame.draw.line(overlay, (255, 195, 90, 210), (222 + off_tl, 0), (0, 222 + off_tl), 2)

    # --- CANTO INFERIOR DIREITO ---
    off_br = recuo
    pts_br_sombra = [(LARGURA + off_br, ALTURA), (LARGURA - 318 + off_br, ALTURA), (LARGURA, ALTURA - 318 + off_br)]
    pts_br_princ = [(LARGURA + off_br, ALTURA), (LARGURA - 288 + off_br, ALTURA), (LARGURA, ALTURA - 288 + off_br)]
    pts_br_inner = [(LARGURA + off_br, ALTURA), (LARGURA - 222 + off_br, ALTURA), (LARGURA, ALTURA - 222 + off_br)]

    pygame.draw.polygon(overlay, (95, 16, 26, 235), pts_br_sombra)
    pygame.draw.polygon(overlay, (185, 32, 46, 245), pts_br_princ)
    pygame.draw.polygon(overlay, (130, 20, 32, 245), pts_br_inner)

    desloc_br = (tempo * 75.0) % espaco_chev
    for k in range(-2, 10):
        dist = k * espaco_chev + desloc_br
        px = LARGURA - dist + off_br
        py = ALTURA - 255 + dist + off_br
        if LARGURA - 290 <= px <= LARGURA + 40 and ALTURA - 290 <= py <= ALTURA + 40:
            pts_c = [
                (px + 10, py + 24),
                (px - 6, py + 24),
                (px - 20, py + 10),
                (px - 6, py - 4),
                (px + 10, py - 4),
                (px - 4, py + 10),
            ]
            pygame.draw.polygon(overlay, (255, 85, 95, 120), pts_c)

    pygame.draw.line(overlay, (255, 75, 88, 255), (LARGURA - 288 + off_br, ALTURA), (LARGURA, ALTURA - 288 + off_br), 4)
    pygame.draw.line(overlay, (255, 195, 90, 210), (LARGURA - 222 + off_br, ALTURA), (LARGURA, ALTURA - 222 + off_br), 2)

    superficie.blit(overlay, (0, 0))


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


def desenhar_radar(superficie, jogador, cristais, paredes, minas, inimigos, config):
    from perigo import Perseqtor, Bigon

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

    for mina in minas:
        mx, my = para_radar(mina.x, mina.y)
        pygame.draw.circle(superficie, (255, 125, 55), (mx, my), 3)

    for cristal in cristais:
        cx, cy = para_radar(cristal.x, cristal.y)
        pygame.draw.circle(superficie, COR_CRISTAL, (cx, cy), 3)

    for inimigo in inimigos:
        if isinstance(inimigo, Bigon) and not inimigo.ativo_no_ceu:
            continue
        ix, iy = para_radar(inimigo.x, inimigo.y)
        if isinstance(inimigo, Perseqtor):
            cor_inimigo_rad = (120, 100, 150) if inimigo.esta_tonto else (175, 130, 235)
        elif isinstance(inimigo, Bigon):
            cor_inimigo_rad = (214, 114, 48)
        else:
            cor_inimigo_rad = (150, 140, 120) if inimigo.esta_tonto else (255, 70, 40)
        pygame.draw.circle(superficie, cor_inimigo_rad, (ix, iy), 5)

    if not jogador.morto:
        jx, jy = para_radar(jogador.x, jogador.y)
        pygame.draw.circle(superficie, COR_JOGADOR, (jx, jy), 4)


def desenhar_hud_superior(superficie, pontos, cristais, inimigos, config, fonte, fonte_pequena, fonte_mini):
    from perigo import Bigon
    from modificador import cor_multiplicador

    texto_pontos = fonte.render(f"Pontuação: {pontos} | Restantes: {len(cristais)}/{config.qtd_cristais}", True, COR_TEXTO)
    superficie.blit(texto_pontos, (20, 18))

    mult = config.multiplicador_onda_atual
    cor_mult = cor_multiplicador(mult)
    teto_txt = " (Máx x3)" if config.errei_conta_ativo else ""
    surf_mult = fonte_pequena.render(f"Multiplicador: x{mult}{teto_txt}", True, cor_mult)
    surf_mult.set_alpha(175)
    superficie.blit(surf_mult, (20, 44))

    offset_info_x = 20 + surf_mult.get_width() + 18

    if config.stacks_cabuum > 0:
        cor_m = (255, 85, 95) if config.explosoes_mina_sofridas >= 2 else (255, 145, 70)
        surf_minas = fonte_mini.render(
            f"Explosões: {config.explosoes_mina_sofridas}/{config.max_explosoes_mina}",
            True,
            cor_m
        )
        surf_minas.set_alpha(195)
        superficie.blit(surf_minas, (offset_info_x, 45))
        offset_info_x += surf_minas.get_width() + 16

    for inimigo in inimigos:
        if isinstance(inimigo, Bigon):
            cor_b = (255, 85, 95) if inimigo.batidas_na_onda >= 2 else (224, 138, 76)
            surf_bigon = fonte_mini.render(
                f"Peso Bigon: {inimigo.batidas_na_onda}/{inimigo.max_batidas_onda}",
                True,
                cor_b
            )
            surf_bigon.set_alpha(190)
            superficie.blit(surf_bigon, (offset_info_x, 45))
            offset_info_x += surf_bigon.get_width() + 16


def desenhar_hud_jogador(superficie, jogador, config, fonte, fonte_mini):
    from modificador import calcular_multiplicador_por_tempo, cor_multiplicador

    x, y = 20, 72
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
        largura_extra = int((excesso / jogador.bonus_vel_parry) * 105)
        if jogador.boost_parry_ativo:
            cor_extra = COR_PARRY
        elif jogador.boost_wk_ativo:
            cor_extra = COR_WALL_KICK
        else:
            cor_extra = COR_SLIDE
        pygame.draw.rect(superficie, cor_extra, (x + largura_barra, y, largura_extra, altura_barra))

    pct_embalo = int(round(jogador.fator_embalo_mod * 100))
    if jogador.boost_parry_ativo:
        texto_status = "PARRY BOOST!"
        cor_label = COR_PARRY
    elif jogador.lento_por_bigon:
        texto_status = "PESADO!"
        cor_label = (95, 185, 135)
    elif jogador.boost_wk_ativo:
        texto_status = "WALL KICK!"
        cor_label = COR_WALL_KICK
    elif jogador.slide_ativo:
        texto_status = "AIR SLIDE!" if jogador.slide_foi_no_ar else "SLIDE!"
        cor_label = COR_SLIDE
    else:
        texto_status = f"Embalo ({pct_embalo}%)"
        cor_label = (180, 180, 190)

    label = fonte.render(texto_status, True, cor_label)
    fim_embalo_x = x + max(largura_max_visual, largura_barra + 105) + 10
    superficie.blit(label, (fim_embalo_x, y - 3))

    py = y + 20
    largura_parry = 120
    altura_parry = 7
    pygame.draw.rect(superficie, (28, 28, 34), (x, py, largura_parry, altura_parry))

    if jogador.parry_bloqueado:
        pygame.draw.rect(superficie, (110, 105, 95), (x, py, largura_parry, altura_parry))
        pygame.draw.rect(superficie, (80, 80, 95), (x, py, largura_parry, altura_parry), 1)

        meio_x = x + largura_parry // 2
        rachadura_pts = [
            (meio_x - 5, py - 3),
            (meio_x + 2, py + 2),
            (meio_x - 3, py + 5),
            (meio_x + 4, py + altura_parry + 3),
        ]
        pygame.draw.lines(superficie, COR_FUNDO, False, rachadura_pts, 4)
        pygame.draw.lines(superficie, (255, 85, 95), False, rachadura_pts, 1)

        lbl_parry = fonte.render("PARRY: QUEBRADO", True, (255, 95, 105))
        superficie.blit(lbl_parry, (x + largura_parry + 10, py - 4))
    else:
        if jogador.cooldown_parry <= 0.0:
            pygame.draw.rect(superficie, COR_PARRY, (x, py, largura_parry, altura_parry))
            lbl_parry = fonte.render("Parry [E / Botão Dir.]", True, COR_PARRY)
        else:
            prog_cd = 1.0 - (jogador.cooldown_parry / jogador.cooldown_parry_max)
            pygame.draw.rect(superficie, (110, 105, 95), (x, py, int(largura_parry * max(0.0, prog_cd)), altura_parry))
            lbl_parry = fonte.render(f"Parry ({jogador.cooldown_parry:.1f}s)", True, (135, 135, 145))

        pygame.draw.rect(superficie, (80, 80, 95), (x, py, largura_parry, altura_parry), 1)
        superficie.blit(lbl_parry, (x + largura_parry + 10, py - 4))

    relogio_x = fim_embalo_x + label.get_width() + 26
    relogio_y = y + 12

    potencial_mult = calcular_multiplicador_por_tempo(config.tempo_onda, config)
    cor_rel = cor_multiplicador(potencial_mult)

    surf_relogio = pygame.Surface((32, 32), pygame.SRCALPHA)
    rcx, rcy = 16, 16
    pygame.draw.circle(surf_relogio, (24, 24, 32, 130), (rcx, rcy), 13)
    pygame.draw.circle(surf_relogio, (*cor_rel, 165), (rcx, rcy), 13, 2)
    pygame.draw.line(surf_relogio, (*cor_rel, 180), (rcx, 1), (rcx, 3), 2)

    ang_ponteiro = -math.pi / 2 + (config.tempo_onda * (math.pi / 3.0))
    px = rcx + int(math.cos(ang_ponteiro) * 8)
    py_ptr = rcy + int(math.sin(ang_ponteiro) * 8)
    pygame.draw.line(surf_relogio, (*cor_rel, 195), (rcx, rcy), (px, py_ptr), 2)
    pygame.draw.circle(surf_relogio, (*cor_rel, 200), (rcx, rcy), 2)
    superficie.blit(surf_relogio, (relogio_x - 16, relogio_y - 16))

    surf_tempo = fonte.render(f"{config.tempo_onda:04.1f}s", True, cor_rel)
    surf_tempo.set_alpha(175)
    superficie.blit(surf_tempo, (relogio_x + 20, relogio_y - 13))

    surf_prox = fonte_mini.render(f"Próx: x{potencial_mult}", True, cor_rel)
    surf_prox.set_alpha(155)
    superficie.blit(surf_prox, (relogio_x + 20, relogio_y + 4))


def desenhar_menu_pausa(superficie, pontos, config, fonte_titulo, fonte, fonte_pequena, fonte_mini):
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((10, 12, 18, 205))
    superficie.blit(overlay, (0, 0))

    largura_caixa = 440
    altura_caixa = 310
    rect_caixa = pygame.Rect(
        (LARGURA - largura_caixa) // 2,
        (ALTURA - altura_caixa) // 2,
        largura_caixa,
        altura_caixa
    )
    pygame.draw.rect(superficie, (28, 28, 36), rect_caixa, border_radius=14)
    pygame.draw.rect(superficie, (255, 190, 80), rect_caixa, 2, border_radius=14)

    t_pausa = fonte_titulo.render("JOGO PAUSADO", True, (255, 190, 80))
    superficie.blit(t_pausa, t_pausa.get_rect(center=(rect_caixa.centerx, rect_caixa.y + 42)))

    t_score = fonte_pequena.render(
        f"Pontuação: {pontos}  |  Multiplicador: x{config.multiplicador_onda_atual}",
        True,
        (180, 225, 240)
    )
    superficie.blit(t_score, t_score.get_rect(center=(rect_caixa.centerx, rect_caixa.y + 78)))

    pygame.draw.line(
        superficie,
        (65, 65, 80),
        (rect_caixa.x + 36, rect_caixa.y + 102),
        (rect_caixa.right - 36, rect_caixa.y + 102),
        1
    )

    opcoes = [
        ("[ENTER]  Continuar Partida", COR_TEXTO),
        ("[R]      Reiniciar Run", (255, 175, 95)),
        ("[ESC]    Fechar Jogo", (255, 100, 110)),
    ]
    for i, (texto, cor) in enumerate(opcoes):
        surf = fonte.render(texto, True, cor)
        superficie.blit(surf, surf.get_rect(center=(rect_caixa.centerx, rect_caixa.y + 138 + i * 36)))

    txt_parry_dica = "PARRY: QUEBRADO" if config.ossos_vidro_ativo else "Parry: [E] ou Botão Dir."
    dica_controles = fonte_mini.render(f"{txt_parry_dica} | Slide: [Shift]", True, (150, 155, 170))
    superficie.blit(dica_controles, dica_controles.get_rect(center=(rect_caixa.centerx, rect_caixa.bottom - 26)))


def iniciar_nova_rodada(config, jogador, camera, mestre, propaganda):
    from modificador import gerar_paredes_rodada, gerar_cristais, gerar_minas_rodada
    from perigo import gerar_inimigos_rodada

    config.tempo_onda = 0.0
    jogador.resetar_para_centro(config)
    camera.centralizar(config)
    mestre.resetar_ciclo()
    propaganda.resetar()
    paredes = gerar_paredes_rodada(config)
    cristais = gerar_cristais(config, paredes)
    minas = gerar_minas_rodada(config, paredes, cristais)
    inimigos = gerar_inimigos_rodada(config, paredes)
    return paredes, cristais, minas, inimigos


def main():
    from jogador import Jogador
    from perigo import MestreHUD, GerenciadorPropaganda, Bigon
    from modificador import (
        ConfigPartida,
        calcular_multiplicador_por_tempo,
        cor_multiplicador,
        gerar_opcoes_cartas,
        aplicar_modificador,
    )

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
    mestre = MestreHUD()
    propaganda = GerenciadorPropaganda()
    paredes, cristais, minas, inimigos = iniciar_nova_rodada(config, jogador, camera, mestre, propaganda)
    explosoes_visuais = []
    pontos = 0
    tempo_jogo = 0.0
    tempo_tela_cartas = 0.0
    tempo_gameover = 0.0
    motivo_gameover = "FIM DE JOGO!"

    timer_hitstop = 0.0
    timer_flash_parry = 0.0

    estado = "JOGANDO"
    cartas_atuais = []
    escolhas_restantes_onda = 0
    total_escolhas_onda = 1

    def abrir_selecao_cartas(reiniciar_fila=True):
        nonlocal estado, tempo_tela_cartas, cartas_atuais, escolhas_restantes_onda, total_escolhas_onda
        if reiniciar_fila:
            total_escolhas_onda = 1 + config.stacks_de_novo
            escolhas_restantes_onda = total_escolhas_onda
        estado = "ESCOLHA_CARTA"
        tempo_tela_cartas = 0.0
        cartas_atuais = gerar_opcoes_cartas(config)

    def acionar_gameover(motivo, fonte_x=None):
        nonlocal estado, motivo_gameover, tempo_gameover, timer_hitstop
        motivo_gameover = motivo
        estado = "GAME_OVER"
        tempo_gameover = 0.0
        timer_hitstop = 0.12
        jogador.iniciar_animacao_morte(camera, fonte_x=fonte_x)

    rodando = True
    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if estado == "JOGANDO":
                        estado = "PAUSADO"
                    elif estado == "PAUSADO":
                        estado = "JOGANDO"

                elif evento.key == pygame.K_c:
                    if estado == "JOGANDO":
                        config.multiplicador_onda_atual = calcular_multiplicador_por_tempo(config.tempo_onda, config)
                        abrir_selecao_cartas(reiniciar_fila=True)
                    elif estado == "ESCOLHA_CARTA":
                        abrir_selecao_cartas(reiniciar_fila=False)

                elif evento.key == pygame.K_b and estado == "JOGANDO":
                    ativar = not (config.perigo_bigon_ativo and config.errei_conta_ativo)
                    config.perigo_bigon_ativo = ativar
                    config.errei_conta_ativo = ativar
                    if ativar:
                        config.multiplicador_onda_atual = min(3, config.multiplicador_onda_atual)
                        if not any(isinstance(ini, Bigon) for ini in inimigos):
                            inimigos.append(Bigon(jogador.x, jogador.y))
                    else:
                        inimigos = [ini for ini in inimigos if not isinstance(ini, Bigon)]

                elif evento.key == pygame.K_r and estado in ("GAME_OVER", "PAUSADO"):
                    config = ConfigPartida()
                    jogador = Jogador(config)
                    camera = Camera(config)
                    mestre = MestreHUD()
                    propaganda = GerenciadorPropaganda()
                    paredes, cristais, minas, inimigos = iniciar_nova_rodada(config, jogador, camera, mestre, propaganda)
                    explosoes_visuais.clear()
                    pontos = 0
                    timer_hitstop = 0.0
                    timer_flash_parry = 0.0
                    tempo_gameover = 0.0
                    escolhas_restantes_onda = 0
                    total_escolhas_onda = 1
                    estado = "JOGANDO"

                elif evento.key == pygame.K_ESCAPE and estado == "PAUSADO":
                    rodando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if estado == "JOGANDO" and config.perigo_propaganda_ativo:
                    propaganda.processar_clique(evento.pos)

                elif estado == "ESCOLHA_CARTA":
                    for carta in cartas_atuais:
                        if carta.rect.collidepoint(evento.pos):
                            aplicar_modificador(carta.id_mod, config, jogador, mestre, propaganda)
                            escolhas_restantes_onda -= 1

                            if escolhas_restantes_onda > 0:
                                abrir_selecao_cartas(reiniciar_fila=False)
                            else:
                                paredes, cristais, minas, inimigos = iniciar_nova_rodada(config, jogador, camera, mestre, propaganda)
                                explosoes_visuais.clear()
                                estado = "JOGANDO"
                            break

        if estado == "JOGANDO":
            if timer_flash_parry > 0.0:
                timer_flash_parry = max(0.0, timer_flash_parry - dt)

            for exp in explosoes_visuais[:]:
                exp["vida"] -= dt
                if exp["vida"] <= 0.0:
                    explosoes_visuais.remove(exp)

            if timer_hitstop > 0.0:
                timer_hitstop = max(0.0, timer_hitstop - dt)
            else:
                tempo_jogo += dt
                config.tempo_onda += dt

                teto_tempo = calcular_multiplicador_por_tempo(config.tempo_onda, config)
                if config.multiplicador_onda_atual > teto_tempo:
                    config.multiplicador_onda_atual = teto_tempo

                teclas = pygame.key.get_pressed()
                botoes_mouse = pygame.mouse.get_pressed()

                jogador.atualizar(teclas, botoes_mouse, config, paredes, dt)
                camera.atualizar(jogador.x, jogador.y)

                if config.perigo_propaganda_ativo and estado == "JOGANDO":
                    propaganda.atualizar(dt)
                    if jogador.parry_ativo and propaganda.pode_dar_parry():
                        propaganda.bloquear_com_parry()
                        jogador.executar_parry_sucesso()
                        timer_hitstop = 0.11
                        timer_flash_parry = 0.22

                for mina in minas[:]:
                    mina.atualizar(dt)
                    if jogador.parry_ativo and mina.colidiu_com_jogador(jogador, margem_extra=12.0):
                        fuga_x = jogador.x - mina.x
                        fuga_y = jogador.y - mina.y
                        jogador.executar_parry_sucesso(fuga_x, fuga_y)
                        minas.remove(mina)
                        explosoes_visuais.append({"x": mina.x, "y": mina.y, "vida": 0.35, "max_vida": 0.35, "parry": True})
                        timer_hitstop = 0.10
                        timer_flash_parry = 0.20
                    elif (
                        jogador.timer_invulneravel_parry <= 0.0 and
                        mina.colidiu_com_jogador(jogador) and
                        estado == "JOGANDO"
                    ):
                        minas.remove(mina)
                        explosoes_visuais.append({"x": mina.x, "y": mina.y, "vida": 0.45, "max_vida": 0.45, "parry": False})
                        config.explosoes_mina_sofridas += 1
                        timer_hitstop = 0.09

                        recuo_x = jogador.x - mina.x
                        recuo_y = jogador.y - mina.y
                        comp_recuo = math.hypot(recuo_x, recuo_y)
                        if comp_recuo > 0.001:
                            jogador.dir_x = recuo_x / comp_recuo
                            jogador.dir_y = recuo_y / comp_recuo
                        jogador.velocidade_atual = max(jogador.velocidade_atual, jogador.vel_max * 0.9)

                        if config.explosoes_mina_sofridas >= config.max_explosoes_mina:
                            acionar_gameover("EXPLODIDO PELAS MINAS!", fonte_x=mina.x)

                for inimigo in inimigos:
                    inimigo.atualizar(jogador, config, paredes, dt)

                    if isinstance(inimigo, Bigon):
                        if jogador.parry_ativo and inimigo.jogador_bateu_ao_pular(jogador, margem_extra=14.0):
                            fuga_x = jogador.x - inimigo.x
                            fuga_y = jogador.y - inimigo.y
                            jogador.executar_parry_sucesso(fuga_x, fuga_y)
                            inimigo.rebater_com_parry()
                            timer_hitstop = 0.11
                            timer_flash_parry = 0.22
                        elif (
                            jogador.timer_invulneravel_parry <= 0.0 and
                            inimigo.jogador_bateu_ao_pular(jogador) and
                            estado == "JOGANDO"
                        ):
                            atingiu_limite = inimigo.registrar_batida_pulo(jogador)
                            if atingiu_limite:
                                acionar_gameover(inimigo.motivo_morte, fonte_x=inimigo.x)
                    else:
                        if jogador.parry_ativo and inimigo.colidiu_com_jogador(jogador, margem_extra=6.0):
                            fuga_x = jogador.x - inimigo.x
                            fuga_y = jogador.y - inimigo.y
                            jogador.executar_parry_sucesso(fuga_x, fuga_y)
                            inimigo.atordoar(duracao=2.8)
                            timer_hitstop = 0.11
                            timer_flash_parry = 0.22
                        elif (
                            jogador.timer_invulneravel_parry <= 0.0 and
                            inimigo.colidiu_com_jogador(jogador) and
                            estado == "JOGANDO"
                        ):
                            motivo = getattr(inimigo, "motivo_morte", "PICOTADO PELO AERNIS-03!")
                            acionar_gameover(motivo, fonte_x=inimigo.x)

                if config.perigo_mestre_ativo and estado == "JOGANDO":
                    mestre.atualizar(dt)
                    if mestre.detectou_movimento(jogador):
                        if jogador.parry_ativo:
                            mestre.forcar_fechar()
                            jogador.executar_parry_sucesso()
                            timer_hitstop = 0.11
                            timer_flash_parry = 0.22
                        elif jogador.timer_invulneravel_parry <= 0.0:
                            acionar_gameover("O MESTRE VIU VOCÊ SE MEXER!")

                for cristal in cristais[:]:
                    cristal.atualizar(tempo_jogo, jogador, config, paredes, dt)
                    dist_3d = math.sqrt(
                        (jogador.x - cristal.x) ** 2 +
                        (jogador.y - cristal.y) ** 2 +
                        (jogador.z - cristal.z) ** 2
                    )
                    if dist_3d < (jogador.raio + cristal.raio):
                        cristais.remove(cristal)
                        pontos += 1 * config.multiplicador_onda_atual

                if len(cristais) == 0 and estado == "JOGANDO":
                    config.multiplicador_onda_atual = calcular_multiplicador_por_tempo(config.tempo_onda, config)
                    abrir_selecao_cartas(reiniciar_fila=True)

        elif estado == "ESCOLHA_CARTA":
            tempo_tela_cartas += dt

        elif estado == "GAME_OVER":
            if timer_hitstop > 0.0:
                timer_hitstop = max(0.0, timer_hitstop - dt)
            else:
                tempo_gameover += dt
                jogador.atualizar_morte(dt)

        # --- RENDERIZAÇÃO ---
        tela.fill(COR_FUNDO)
        desenhar_terreno(tela, camera, config)

        for parede in paredes:
            parede.desenhar_sombra(tela, camera)
        for mina in minas:
            mina.desenhar_sombra(tela, camera)
        for cristal in cristais:
            cristal.desenhar_sombra(tela, camera)
        for inimigo in inimigos:
            inimigo.desenhar_sombra(tela, camera)
        jogador.desenhar_sombra(tela, camera)

        entidades = cristais + paredes + minas + inimigos + [jogador]
        entidades.sort(key=lambda obj: obj.sort_y if hasattr(obj, "sort_y") else obj.y)

        for entidade in entidades:
            entidade.desenhar(tela, camera)

        for exp in explosoes_visuais:
            ex, ey = mundo_para_tela(exp["x"], exp["y"], 8, camera)
            prog = 1.0 - (exp["vida"] / exp["max_vida"])
            raio_exp = int(16 + prog * 54)
            cor_ext = (255, 240, 175) if exp["parry"] else (255, 95, 40)
            cor_int = (255, 250, 230) if exp["parry"] else (255, 200, 65)
            pygame.draw.circle(tela, cor_ext, (ex, ey), raio_exp, 4)
            if prog < 0.65:
                pygame.draw.circle(tela, cor_int, (ex, ey), max(4, int(raio_exp * 0.55)))

        if config.perigo_mestre_ativo:
            mestre.desenhar(tela, fonte_pequena, pausado=(estado in ("PAUSADO", "GAME_OVER")))

        if timer_flash_parry > 0.0:
            flash = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            alpha_flash = int(145 * (timer_flash_parry / 0.22))
            flash.fill((255, 252, 240, alpha_flash))
            tela.blit(flash, (0, 0))

        # HUD
        desenhar_hud_superior(tela, pontos, cristais, inimigos, config, fonte, fonte_pequena, fonte_mini)

        lista_perigos = []
        if config.perigo_aernis_ativo:
            lista_perigos.append("Aernis-03")
        if config.perigo_mestre_ativo:
            lista_perigos.append("Mestre")
        if config.perigo_perseqtor_ativo:
            lista_perigos.append("Perseqtor")
        if config.perigo_bigon_ativo:
            lista_perigos.append("Bigon")
        if config.perigo_propaganda_ativo:
            lista_perigos.append("Propaganda")
        perigos_txt = ", ".join(lista_perigos) if lista_perigos else "Nenhum"

        extras_txt = ""
        if config.stacks_de_novo > 0:
            extras_txt += f" | De novo:{config.stacks_de_novo}"
        if config.ossos_vidro_ativo:
            extras_txt += " | Ossos de Vidro"
        if config.errei_conta_ativo:
            extras_txt += " | Errei a Conta"

        resumo_mods = (
            f"Mais?:{config.stacks_mais} | Espaçoso:{config.stacks_espacoso} | "
            f"Volta Aqui!:{config.stacks_volta_aqui} | Cabuum!:{config.stacks_cabuum} | "
            f"Lerdo:{config.stacks_lerdo}/3 | Slide:{config.stacks_escorregou}/3 | "
            f"WK:{config.stacks_brochou}/3 | Maze:{config.stacks_maze}{extras_txt} | Perigos: {perigos_txt}"
        )
        texto_mods = fonte_mini.render(resumo_mods, True, (210, 140, 150))

        parry_hud_ctrl = "PARRY: QUEBRADO" if config.ossos_vidro_ativo else "[E]/Botão Dir: Parry"
        texto_controles = fonte_mini.render(
            f"WASD/Setas: Mover | Espaço: Pular/WK | Shift: Slide | {parry_hud_ctrl} | [Enter]: Pausar",
            True,
            (140, 140, 150)
        )
        tela.blit(texto_mods, (20, ALTURA - 50))
        tela.blit(texto_controles, (20, ALTURA - 28))

        desenhar_hud_jogador(tela, jogador, config, fonte_pequena, fonte_mini)
        desenhar_radar(tela, jogador, cristais, paredes, minas, inimigos, config)

        if config.perigo_propaganda_ativo and estado in ("JOGANDO", "PAUSADO"):
            propaganda.desenhar(
                tela,
                pos_mouse,
                fonte_pequena,
                fonte,
                fonte_mini,
                mestre_ativo=config.perigo_mestre_ativo
            )

        if estado == "PAUSADO":
            desenhar_menu_pausa(tela, pontos, config, fonte_grande, fonte, fonte_pequena, fonte_mini)

        elif estado == "ESCOLHA_CARTA":
            desenhar_fundo_selecao_cartas(tela, tempo_tela_cartas)

            escolha_atual_num = (total_escolhas_onda - escolhas_restantes_onda) + 1
            if config.escolhas_cartas_realizadas == 0:
                titulo_str = "ESCOLHA SUA AMEAÇA INICIAL"
                cor_titulo = (255, 85, 95)
            elif total_escolhas_onda > 1:
                if escolha_atual_num == 1:
                    titulo_str = f"ESCOLHA SEU DESAFIO ({escolha_atual_num}/{total_escolhas_onda})"
                    cor_titulo = (255, 190, 80)
                else:
                    titulo_str = f"DE NOVO! ESCOLHA EXTRA ({escolha_atual_num}/{total_escolhas_onda})"
                    cor_titulo = (225, 125, 255)
            else:
                titulo_str = "ESCOLHA SEU PRÓXIMO DESAFIO"
                cor_titulo = (255, 190, 80)

            titulo_tela = fonte_grande.render(titulo_str, True, cor_titulo)
            rect_titulo = titulo_tela.get_rect(center=(LARGURA // 2, 92))
            tela.blit(titulo_tela, rect_titulo)

            cor_mult_prox = cor_multiplicador(config.multiplicador_onda_atual)
            sub_mult = fonte_pequena.render(
                f"Ritmo da Onda: {config.tempo_onda:.1f}s  ->  Multiplicador da Próxima Onda: x{config.multiplicador_onda_atual}",
                True,
                cor_mult_prox
            )
            tela.blit(sub_mult, sub_mult.get_rect(center=(LARGURA // 2, 126)))

            for i, carta in enumerate(cartas_atuais):
                atraso = i * 0.05
                prog = max(0.0, min(1.0, (tempo_tela_cartas - atraso) / 0.24))
                ease = 1.0 - (1.0 - prog) ** 3
                offset_entrada = int((1.0 - ease) * 55)
                carta.desenhar(tela, pos_mouse, fonte, fonte_pequena, fonte_mini, offset_y=offset_entrada)

            dica_reroll = fonte_mini.render("[C] Re-sortear cartas (Debug)", True, (205, 195, 210))
            tela.blit(dica_reroll, dica_reroll.get_rect(center=(LARGURA // 2, ALTURA - 42)))

        elif estado == "GAME_OVER":
            prog_overlay = min(1.0, tempo_gameover / 0.35)
            alpha_overlay = int(195 * prog_overlay)
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((25, 10, 14, alpha_overlay))
            tela.blit(overlay, (0, 0))

            if timer_hitstop <= 0.0:
                alpha_texto = int(255 * min(1.0, tempo_gameover / 0.25))
                t_go = fonte_grande.render(motivo_gameover, True, (255, 65, 75))
                t_pts = fonte.render(f"Pontuação Final: {pontos} cristais", True, COR_TEXTO)
                t_reiniciar = fonte_pequena.render("Pressione [R] para jogar novamente", True, (200, 200, 210))

                t_go.set_alpha(alpha_texto)
                t_pts.set_alpha(alpha_texto)
                t_reiniciar.set_alpha(alpha_texto)

                tela.blit(t_go, t_go.get_rect(center=(LARGURA // 2, ALTURA // 2 - 45)))
                tela.blit(t_pts, t_pts.get_rect(center=(LARGURA // 2, ALTURA // 2 + 5)))
                tela.blit(t_reiniciar, t_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 55)))

            jogador.desenhar_animacao_morte(tela)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()