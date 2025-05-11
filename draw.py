import pygame

heart_image = pygame.image.load('images_png\heart.png')  # Remplacez par le chemin de votre image de cœur
heart_image = pygame.transform.scale(heart_image, (30, 30))  # Redimensionnez l'image si nécessaire

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

def draw_health(screen, ball,screen_size):
    """
    Dessine le nombre de vies restantes pour une balle donnée.

    :param screen: Surface sur laquelle dessiner.
    :param ball: Objet Ball dont on veut afficher les vies.
    :param x: Position x pour le dessin.
    :param y: Position y pour le dessin.
    """
    # Affichage du nombre de vies restantes
    if ball.name == 'blue':
        for i in range(ball.life):
            screen.blit(heart_image, (5, 5 + i * 35))  # Dessinez les cœurs en haut à gauche pour la balle bleue
    elif ball.name == 'red':
        for i in range(ball.life):
            screen.blit(heart_image, (screen_size[0]-35, 5 + i * 35)) # Dessinez les cœurs en haut à droite pour la balle rouge