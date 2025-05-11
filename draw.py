import pygame

def draw_text(text, font, color, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    return textobj, textrect

def draw_text_with_outline(screen, text, font, color, outline_color, x, y):
    # Rendu du texte principal
    text_surface = font.render(text, True, color)

    # Rendu du contour
    for dx in [-1, 1]:
        for dy in [-1, 1]:
            outline_surface = font.render(text, True, outline_color)
            outline_rect = outline_surface.get_rect(center=(x + dx, y + dy))
            screen.blit(outline_surface, outline_rect)

    # Rendu du texte principal
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_health(screen, ball, x, y):
    """
    Dessine le nombre de vies restantes pour une balle donnée.

    :param screen: Surface sur laquelle dessiner.
    :param ball: Objet Ball dont on veut afficher les vies.
    :param x: Position x pour le dessin.
    :param y: Position y pour le dessin.
    """
    font = pygame.font.Font(None, 36)  # Police par défaut, taille 36

    # Affichage du nombre de vies restantes
    health_text = f"Hearts: {ball.life}"
    draw_text_with_outline(screen, health_text, font, (255, 255, 255), (0, 0, 0), x, y)