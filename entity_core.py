"""
Chainfall - Entity Core (Raster Snake Movement with Path History)
"""
import pygame
import math
from config import SNAKE_SPEED_X, SNAKE_SPACING, SNAKE_DROP_STEP, SNAKE_LENGTH, SPRING_STIFFNESS, RETURN_FORCE, DAMPING, MASS, SCREEN_WIDTH, SCREEN_HEIGHT


class SegmentGroup:
    def __init__(self, start_hp=20):
        self.hp = start_hp
        self.max_hp = start_hp
        self.segments = [] # List of SnakeSegment objects
        self.flash_timer = 0.0
        
    def add_segment(self, segment):
        self.segments.append(segment)
        segment.group = self
        
    def take_damage(self, amount):
        self.hp -= amount
        self.flash_timer = 0.25 # Flash red for 0.25s
        if self.hp <= 0:
            return True # Destroyed
        return False
        
    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt

class SnakeSegment:
    def __init__(self, x, y, image=None, group=None, is_head=False, head_image=None):
        self.x = x
        self.y = y
        self.image = image
        self.head_image = head_image  # Separate sprite for head
        self.active = True
        self.radius = 20
        self.velocity_y = 0.0 
        self.group = group # Reference to SegmentGroup
        self.font = pygame.font.Font(None, 24)
        self.is_head = is_head  # Head is visually distinct and indestructible
        self.is_head = is_head  # Head is visually distinct and indestructible
        self.facing_angle = 0  # Legacy angle, unused for head logic now.
        self.facing_dir = "RIGHT" # "RIGHT", "LEFT", "UP", "DOWN"
        
        # Spring render layer
        self.render_x = x
        self.render_y = y
        self.vel_rx = 0.0
        self.vel_ry = 0.0
        
        # Hit scale effect
        self.hit_scale = 1.0
        self.hit_timer = 0.0

    def draw(self, screen, offset_y=0):
        draw_y = self.render_y + offset_y
        
        # Determine which image to use
        if self.is_head and self.head_image:
            draw_image = self.head_image
        else:
            draw_image = self.image
        
        # Flash effect
        if self.group and self.group.flash_timer > 0 and draw_image:
             draw_image = draw_image.copy()
             draw_image.fill((255, 50, 50, 150), special_flags=pygame.BLEND_RGBA_MULT)
             
        if draw_image:
             # Apply hit scale only (no base_scale since head image is pre-scaled)
             total_scale = self.hit_scale
             if total_scale != 1.0:
                  w, h = draw_image.get_size()
                  scaled_w = int(w * total_scale)
                  scaled_h = int(h * total_scale)
                  draw_image = pygame.transform.scale(draw_image, (scaled_w, scaled_h))
             
             # Rotate head based on direction (Stable Logic)
             if self.is_head:
                 if self.facing_dir == "LEFT":
                     draw_image = pygame.transform.flip(draw_image, True, False)
                 elif self.facing_dir == "DOWN":
                     draw_image = pygame.transform.rotate(draw_image, -90)
                 elif self.facing_dir == "UP":
                     draw_image = pygame.transform.rotate(draw_image, 90)
                 # RIGHT is default (no change)

             rect = draw_image.get_rect(center=(int(self.render_x), int(draw_y)))
             if screen: screen.blit(draw_image, rect)
        else:
             # Fallback circle - head is 1.5x larger and different color
             base_scale = 1.5 if self.is_head else 1.0
             draw_radius = int(self.radius * base_scale * self.hit_scale)
             head_color = (180, 50, 50) if self.is_head else (220, 220, 210)
             if screen: pygame.draw.circle(screen, head_color, (int(self.render_x), int(draw_y)), draw_radius)
        
        # Draw HP only on the middle segment of the group
        if self.group and len(self.group.segments) > 0:
             center_idx = len(self.group.segments) // 2
             if self.group.segments[center_idx] == self:
                  if self.group.hp < self.group.max_hp:
                       color = (255, 100, 100)
                  else:
                       color = (200, 200, 200)
                  text = self.font.render(str(self.group.hp), True, color)
                  if screen: screen.blit(text, (self.render_x - 5, self.render_y - 15))

    def take_damage(self, amount):
        # Head is indestructible
        if self.is_head:
            return False
        # Trigger hit scale effect
        self.hit_scale = 1.15
        self.hit_timer = 0.1
        if self.group:
            return self.group.take_damage(amount)
        return False

    def update_render(self, dt, snap_active=False, freeze_active=False):
        """Spring physics for visual smoothing"""
        # HEAD OR FREEZE: instant follow (no spring delay)
        if self.is_head or freeze_active:
            self.render_x = self.x
            self.render_y = self.y
            self.vel_rx = 0
            self.vel_ry = 0
            return
        
        # Target = logical position (from path_history)
        dx = self.x - self.render_x
        dy = self.y - self.render_y
        
        # Reduced stiffness during snap-back (0.4x) to prevent whip effect
        effective_stiffness = SPRING_STIFFNESS * 0.4 if snap_active else SPRING_STIFFNESS
        
        # Spring force
        self.vel_rx += dx * effective_stiffness * dt
        self.vel_ry += dy * effective_stiffness * dt
        
        # Damping
        self.vel_rx *= (1.0 - DAMPING * dt)
        self.vel_ry *= (1.0 - DAMPING * dt)
        
        # Limit max render step to prevent S-shape at tail
        max_step = 1.2
        step_x = self.vel_rx * dt
        step_y = self.vel_ry * dt
        if abs(step_x) > max_step:
            step_x = max_step if step_x > 0 else -max_step
        if abs(step_y) > max_step:
            step_y = max_step if step_y > 0 else -max_step
        
        # Apply velocity (with limited step)
        self.render_x += step_x
        self.render_y += step_y
        
        # Snap if very close (prevent jitter)
        if abs(dx) < 0.5 and abs(dy) < 0.5:
            self.render_x = self.x
            self.render_y = self.y
            self.vel_rx = 0
            self.vel_ry = 0

    def reset_render_pos(self):
        """Reset visual position to logical position (prevents glitches)"""
        self.render_x = self.x
        self.render_y = self.y
        self.vel_rx = 0
        self.vel_ry = 0

# ... inside BoneSnake ...

    def remove_segment(self, segment):
        """
        Removes a segment and snaps the front part of the snake back 
        to fill the gap.
        """
        if segment in self.segments:
            self.segments.remove(segment)
            
            # Snap Back Logic:
            # We need to rewind the path history by SNAKE_SPACING distance.
            # This effectively pulls the head back.
            
            # Estimate how many points to pop based on average distance
            # Since we insert every ~2px (dist_moved >= 2.0), 
            # and spacing is 25px, we need to remove approx 12-13 points.
            
            # More robust: Walk from history[0] and remove until distance > SNAKE_SPACING
            
            points_to_remove = 0
            accumulated = 0
            for i in range(len(self.path_history) - 1):
                p1 = self.path_history[i]
                p2 = self.path_history[i+1]
                dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                accumulated += dist
                points_to_remove += 1
                
                if accumulated >= SNAKE_SPACING:
                    break
            
            # Remove points from front (Head history)
            if points_to_remove > 0:
                 self.path_history = self.path_history[points_to_remove:]
                 # Reposition head to new history start
                 if self.path_history:
                     self.head_x = self.path_history[0][0]
                     self.head_y = self.path_history[0][1]
            
            return True
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
            
    def __init__(self, screen_width, screen_height, segment_image=None, head_image=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = segment_image
        self.head_image = head_image
        self.segments = []
        self.groups = [] # Track groups
        
        # State Machine
        self.direction = 1 # 1: Right, -1: Left
        self.state = "MOVING" # MOVING, DROPPING
        self.target_y = 0
        self.target_y = 0
        self.snap_timer = 0.0  # Timer for reduced spring during snap-back
        self.snap_timer = 0.0  # Timer for reduced spring during snap-back
        self.freeze_timer = 0.0 # Timer to freeze spring physics for 1 frame
        
        # Head tracking for rotation
        self.prev_head_x = 0
        self.prev_head_y = 0
        self.head_dir = "RIGHT"
        
        # Initialize at Top Left
        start_x = 50.0
        start_y = 50.0
        
        # Spawn Head
        self.head_x = start_x
        self.head_y = start_y
        self.prev_head_x = start_x
        self.prev_head_y = start_y
        
        # Path History: List of (x, y) tuples
        self.path_history = [(start_x, start_y)]
             
        # Create Head Segment Group
        self.current_group = SegmentGroup(start_hp=20)
        self.groups.append(self.current_group)
        
        # First segment is the HEAD (visually distinct, indestructible)
        head_seg = SnakeSegment(start_x, start_y, self.image, group=self.current_group, is_head=True, head_image=self.head_image)
        self.current_group.add_segment(head_seg)
        self.segments.append(head_seg)
            
    def remove_segment(self, segment):
        """
        Removes a segment's GROUP and snaps back total length.
        """
        group = segment.group
        if not group: 
             # Fallback
             return False
        
        segments_to_remove = group.segments[:] # Copy list
        
        # Count only non-head segments for snap-back distance
        body_segments = [s for s in segments_to_remove if not s.is_head]
        total_len = len(body_segments) * SNAKE_SPACING
        
        # Remove Logic - NEVER remove head segment
        for seg in segments_to_remove:
            if seg.is_head:
                # Head is indestructible - detach it from the group but keep it
                seg.group = None
                continue
            if seg in self.segments:
                self.segments.remove(seg)
        
        if group in self.groups:
            self.groups.remove(group)
        
        # Trigger reduced spring stiffness for smooth snap-back
        # Trigger reduced spring stiffness for smooth snap-back
        self.snap_timer = 0.15
        self.freeze_timer = 0.05 # FREEZE physics for 0.05s (approx 3 frames @ 60fps) to prevent glitch
        
        # If head lost its group, assign it to the next available group (or create new one)
        if self.segments and self.segments[0].is_head and self.segments[0].group is None:
            if len(self.groups) > 0:
                # Attach head to first existing group
                self.segments[0].group = self.groups[0]
            else:
                # Create new group for head
                new_group = SegmentGroup(start_hp=20)
                self.groups.append(new_group)
                self.segments[0].group = new_group

        # Snap Back Logic:
        target_cut_dist = total_len
        accumulated = 0
        
        cut_found = False
        cut_index = 0
        
        for i in range(len(self.path_history) - 1):
            p1 = self.path_history[i]
            p2 = self.path_history[i+1]
            dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            
            if accumulated + dist >= target_cut_dist:
                # Found cut point
                remaining = target_cut_dist - accumulated
                ratio = remaining / dist if dist > 0 else 0
                
                new_x = p1[0] + (p2[0] - p1[0]) * ratio
                new_y = p1[1] + (p2[1] - p1[1]) * ratio
                
                self.path_history = self.path_history[i+1:]
                self.path_history.insert(0, (new_x, new_y))
                
                self.head_x = new_x
                self.head_y = new_y
                
                # Deduce State
                if len(self.path_history) >= 2:
                    p_next = self.path_history[1]
                    dx = new_x - p_next[0]
                    dy = new_y - p_next[1] # Forward vector
                    
                    if abs(dy) > abs(dx):
                         self.state = "DROPPING"
                         row = int((self.head_y - 50.0) / SNAKE_DROP_STEP)
                         self.target_y = 50.0 + (row + 1) * SNAKE_DROP_STEP
                         self.direction = 1 if self.head_x > self.screen_width / 2 else -1
                    else:
                         self.state = "MOVING"
                         self.direction = 1 if dx > 0 else -1
                
                # CRITICAL: Reset visuals for ALL segments to match new logical positions instantly
                for seg in self.segments:
                    seg.reset_render_pos()
                
                return True
            
            accumulated += dist
            
        return True

    def update(self, dt):
        # --- 1. Move Head ---
        move_speed = SNAKE_SPEED_X
        margin = 60
        
        if self.state == "MOVING":
            # Move Horizontally
            self.head_x += move_speed * self.direction * dt
            
            # Update head facing angle (0 = right, 180 = left)
            if self.segments:
                self.segments[0].facing_angle = 0 if self.direction == 1 else 180
            
            # Check Boundaries
            if self.direction == 1 and self.head_x > self.screen_width - margin:
                self.start_drop(self.head_y + SNAKE_DROP_STEP)
            elif self.direction == -1 and self.head_x < margin:
                self.start_drop(self.head_y + SNAKE_DROP_STEP)
                
        elif self.state == "DROPPING":
            # Move Vertically
            self.head_y += move_speed * 1.5 * dt # Drop a bit faster
            
            # Update head facing angle (270 = down)
            if self.segments:
                self.segments[0].facing_angle = 270
            
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
        
        # --- 3. Dynamic Infinite Spawning ---
        # Logic: Ensure there is a segment every SNAKE_SPACING units along the path_history.
        
        current_path_idx = 0
        if not self.path_history:
             # Fallback: re-initialize history with head position if lost
             self.path_history = [(self.head_x, self.head_y)]

        if not self.segments:
             # Fallback: Respawn head if all segments destroyed (shouldn't happen with protected head)
             self.current_group = SegmentGroup(start_hp=20)
             self.groups.append(self.current_group)
             head_seg = SnakeSegment(self.head_x, self.head_y, self.image, group=self.current_group, is_head=True, head_image=self.head_image)
             head_seg.reset_render_pos() # Ensure no jump
             self.current_group.add_segment(head_seg)
             self.segments.append(head_seg)
             
        self.segments[0].x = self.path_history[0][0]
        self.segments[0].y = self.path_history[0][1]
        
        for i in range(1, len(self.segments)):
            current_path_idx = self._place_segment(i, current_path_idx)
            
        # Check if we need more segments
        if len(self.path_history) - current_path_idx > 15: # Arbitrary buffer (approx 30px)
             # Adds a new segment at the end
             last_x, last_y = self.segments[-1].x, self.segments[-1].y
             
             # Group Logic
             if not self.current_group or len(self.current_group.segments) >= 5:
                  self.current_group = SegmentGroup(start_hp=20)
                  self.groups.append(self.current_group)

             new_seg = SnakeSegment(last_x, last_y, self.image, group=self.current_group)
             new_seg.reset_render_pos() # Ensure no jump
             self.current_group.add_segment(new_seg)
             self.segments.append(new_seg)

        # Update Groups (Timers)
        for group in self.groups:
            group.update(dt)
        
        # Update snap timer
        if self.snap_timer > 0:
            self.snap_timer -= dt

        # Update freeze timer
        if self.freeze_timer > 0:
            self.freeze_timer -= dt

        # Update segment render positions (spring physics)
        snap_active = self.snap_timer > 0
        freeze_active = self.freeze_timer > 0
        
        # Calculate stable head direction (frame-to-frame delta)
        hx = self.head_x
        hy = self.head_y
        dx = hx - self.prev_head_x
        dy = hy - self.prev_head_y
        
        # Determine strict 4-way direction
        if abs(dx) > abs(dy):
            if dx > 0:
                self.head_dir = "RIGHT"
            elif dx < 0:
                self.head_dir = "LEFT"
        else:
            if dy > 0:
                self.head_dir = "DOWN"
            elif dy < 0:
                self.head_dir = "UP"
        
        # Update Trackers
        self.prev_head_x = hx
        self.prev_head_y = hy

        for seg in self.segments:
            # Pass direction to head segment
            if seg.is_head:
                seg.facing_dir = self.head_dir
            seg.update_render(dt, snap_active, freeze_active)
             
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
    def __init__(self, screen_width, screen_height, image=None, head_image=None):
        self.snake = BoneSnake(screen_width, screen_height, image, head_image)

    def spawn_entity(self, params=None):
        pass

    def update(self, dt):
        self.snake.update(dt)

    def draw(self, screen):
        self.snake.draw(screen)

    def get_entities(self):
        return self.snake.get_segments()
    
    def remove_entity(self, entity):
        """Called when a segment is destroyed"""
        return self.snake.remove_segment(entity)

    def notify_hit(self):
        pass
