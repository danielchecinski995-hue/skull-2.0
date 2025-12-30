"""
Chainfall - Entity Core (Raster Snake Movement with Path History)
"""
import pygame
import math
from config import SNAKE_SPEED_X, SNAKE_SPACING, SNAKE_DROP_STEP, SNAKE_LENGTH, SPRING_STIFFNESS, RETURN_FORCE, DAMPING, MASS, SCREEN_WIDTH, SCREEN_HEIGHT

class SnakeSegment:
    def __init__(self, x, y, image=None):
        self.x = x
        self.y = y
        self.image = image
        self.active = True
        self.radius = 20
        self.velocity_y = 0.0 # Kept for hit feedback

    def hit(self, force=300):
        """Visual feedback"""
        self.velocity_y = -5 

    def update_physics(self, dt):
        # purely visual pop-up decay (offset from the path position)
        if self.velocity_y != 0:
            # We don't change .y directly because that's controlled by path
            # We would need a visual offset. 
            # For simplicity, we'll accept that hit reaction might fight the path for a frame
            # Or we can just ignore physics for now as requested "strict movement"
            pass

    def draw(self, screen, offset_y=0):
        draw_y = self.y + offset_y
        if self.image:
             rect = self.image.get_rect(center=(int(self.x), int(draw_y)))
             if screen: screen.blit(self.image, rect)
        else:
             if screen: pygame.draw.circle(screen, (220, 220, 210), (int(self.x), int(draw_y)), self.radius)
             
    def get_position(self):
        return (self.x, self.y)

    def get_radius(self):
        return self.radius

    def take_damage(self, amount):
        self.hit()
        return False

class BoneSnake:
    def __init__(self, screen_width, screen_height, segment_image=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = segment_image
        self.segments = []
        
        # State Machine
        self.direction = 1 # 1: Right, -1: Left
        self.state = "MOVING" # MOVING, DROPPING
        self.target_y = 0
        
        # Initialize at Top Left
        start_x = 50.0
        start_y = 50.0
        
        # Spawn Head
        self.head_x = start_x
        self.head_y = start_y
        
        # Path History: List of (x, y) tuples
        self.path_history = [(start_x, start_y)]
             
        # Create Head Segment
        self.segments.append(SnakeSegment(start_x, start_y, self.image))
            
    def update(self, dt):
        # --- 1. Move Head ---
        move_speed = SNAKE_SPEED_X
        margin = 60
        
        if self.state == "MOVING":
            # Move Horizontally
            self.head_x += move_speed * self.direction * dt
            
            # Check Boundaries
            if self.direction == 1 and self.head_x > self.screen_width - margin:
                self.start_drop(self.head_y + SNAKE_DROP_STEP)
            elif self.direction == -1 and self.head_x < margin:
                self.start_drop(self.head_y + SNAKE_DROP_STEP)
                
        elif self.state == "DROPPING":
            # Move Vertically
            self.head_y += move_speed * 1.5 * dt # Drop a bit faster
            
            # Check Destination (Simple limit check)
            if self.head_y >= self.target_y:
                self.head_y = self.target_y
                self.end_drop()

        # --- 2. Update Path History ---
        # Only record if moved significant distance to save memory
        last_rec_x, last_rec_y = self.path_history[0]
        dist_moved = math.sqrt((self.head_x - last_rec_x)**2 + (self.head_y - last_rec_y)**2)
        
        if dist_moved >= 2.0: # Record every 2 pixels
            self.path_history.insert(0, (self.head_x, self.head_y))

        # --- 3. Dynamic Infinite Spawning ---
        # Calculate approximate path length
        # Or simpler: count segments vs history points
        # If we record every 2px, and spacing is 25px, we need 1 segment per ~12.5 points
        
        # Better: Walk the path from the end (Tail)
        # If distance from last segment to history end > Spacing, spawn!
        # NO, history end (last index) is the START point.
        # History front (index 0) is HEAD.
        
        # We want to fill the snake BACKWARDS from the head.
        # So we check if we need more segments to cover the current path length.
        
        # Optimization: calculate total path length is expensive every frame?
        # Not really for 2000 points.
        
        # Just check if the last segment is far enough from the start of the path (History End)
        # If the last segment is significantly far from the 'Origin', it means there's a gap at the tail?
        # WAIT. The snake grows FROM THE START? 
        # "Generuj w nieskonczonosc" = keeps coming.
        # So yes, we want segments to fill the path all the way to the "Start Point".
        
        # Logic: Ensure there is a segment every SNAKE_SPACING units along the path_history.
        # We just iterate and place segments. If we run out of segments but still have path, ADD SEGMENT.
        
        current_path_idx = 0
        self.segments[0].x = self.path_history[0][0]
        self.segments[0].y = self.path_history[0][1]
        
        for i in range(1, len(self.segments)):
            current_path_idx = self._place_segment(i, current_path_idx)
            
        # Check if we need more segments
        # Look at where the last segment ended up (current_path_idx)
        # If there is still significant path remaining, spawn a new one
        if len(self.path_history) - current_path_idx > 15: # Arbitrary buffer (approx 30px)
             # Adds a new segment at the end
             # We initiate it at the last known position to avoid jumping
             last_x, last_y = self.segments[-1].x, self.segments[-1].y
             new_seg = SnakeSegment(last_x, last_y, self.image)
             self.segments.append(new_seg)
             
    def _place_segment(self, segment_idx, start_path_idx):
        target_dist = SNAKE_SPACING
        accumulated_dist = 0
        
        # Scan history
        for j in range(start_path_idx, len(self.path_history) - 1):
            p1 = self.path_history[j]
            p2 = self.path_history[j+1]
            
            step_dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            accumulated_dist += step_dist
            
            if accumulated_dist >= target_dist:
                # Interpolate
                overshoot = accumulated_dist - target_dist
                ratio = 1.0 - (overshoot / step_dist) if step_dist > 0 else 0
                
                new_x = p1[0] + (p2[0] - p1[0]) * ratio
                new_y = p1[1] + (p2[1] - p1[1]) * ratio
                
                self.segments[segment_idx].x = new_x
                self.segments[segment_idx].y = new_y
                
                return j # New start index
                
        # If ran out of history
        last = self.path_history[-1]
        self.segments[segment_idx].x = last[0]
        self.segments[segment_idx].y = last[1]
        return len(self.path_history) - 1

    def start_drop(self, target_y):
        self.state = "DROPPING"
        self.target_y = target_y

    def end_drop(self):
        self.state = "MOVING"
        self.direction *= -1 # Flip X direction

    def draw(self, screen):
        # Draw from tail to head
        for seg in reversed(self.segments):
            seg.draw(screen)

    def get_segments(self):
        return self.segments

class EntityManager:
    def __init__(self, screen_width, screen_height, image=None):
        self.snake = BoneSnake(screen_width, screen_height, image)

    def spawn_entity(self, params=None):
        pass

    def update(self, dt):
        self.snake.update(dt)

    def draw(self, screen):
        self.snake.draw(screen)

    def get_entities(self):
        return self.snake.get_segments()
    
    def notify_hit(self):
        pass
