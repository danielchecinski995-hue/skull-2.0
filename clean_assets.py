import pygame
import os

def remove_background(filename):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    try:
        image = pygame.image.load(path).convert_alpha()
        width, height = image.get_size()
        
        # Sample the background colors from the top-left corner
        # We assume the object is centered and doesn't touch the corner
        bg_colors = set()
        for x in range(30): # Scan 30x30 area
            for y in range(30):
                if x < width and y < height:
                    c = image.get_at((x, y))
                    bg_colors.add((c.r, c.g, c.b, c.a))
        
        print(f"Processing {filename}... Detected {len(bg_colors)} potential background colors.")
        
        # Determine tolerance
        tolerance = 30
        
        for x in range(width):
            for y in range(height):
                pixel = image.get_at((x, y))
                
                # Check if pixel matches any of the sampled background colors
                is_bg = False
                for bg_c in bg_colors:
                     dist = sum([abs(pixel[i] - bg_c[i]) for i in range(3)])
                     if dist < tolerance:
                         is_bg = True
                         break
                
                if is_bg:
                    image.set_at((x, y), (0, 0, 0, 0)) # Set to transparent

        pygame.image.save(image, path)
        print(f"Saved cleaned {filename}")
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")

pygame.init()
screen = pygame.display.set_mode((100, 100)) # Init display context

remove_background("enemy.png")
remove_background("player.png")

pygame.quit()
