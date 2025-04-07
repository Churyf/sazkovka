import pygame

# Inicializace
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test Pygame")

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)  # Vyčisti obrazovku

    # Vykresli bílou čáru uprostřed (vertikálně)
    pygame.draw.line(screen, WHITE, (400, 0), (400, 600), 2)

    pygame.display.flip()  # Aktualizace obrazovky

pygame.quit()
