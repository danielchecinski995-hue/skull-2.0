"""
Chainfall - Path Manager (Spline System)
Handles the generation of smooth curves and distance-based point retrieval.
"""
import math

class Path:
    def __init__(self, control_points, resolution=20):
        """
        control_points: list of (x, y) tuples
        resolution: number of interpolated points between control points
        """
        self.points = []
        self._generate_spline(control_points, resolution)
        self.total_length = self.points[-1][0] if self.points else 0

    def _generate_spline(self, points, resolution):
        """Generate Catmull-Rom spline points and calculate accumulated distance."""
        if len(points) < 4:
            # Not enough points for Catmull-Rom, fallback to linear or duplicate end points
            # For simplicity, let's assume valid input or straight lines
            raw_points = points
        else:
            # Catmull-Rom implementation
            raw_points = []
            for i in range(len(points) - 1):
                p0 = points[max(0, i - 1)]
                p1 = points[i]
                p2 = points[i + 1]
                p3 = points[min(len(points) - 1, i + 2)]

                for t_step in range(resolution):
                    t = t_step / resolution
                    x = 0.5 * ((2 * p1[0]) +
                               (-p0[0] + p2[0]) * t +
                               (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t**2 +
                               (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t**3)
                    y = 0.5 * ((2 * p1[1]) +
                               (-p0[1] + p2[1]) * t +
                               (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t**2 +
                               (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t**3)
                    raw_points.append((x, y))
            # Add last point
            raw_points.append(points[-1])

        # Calculate accumulated distances
        dist = 0.0
        self.points = [(0.0, raw_points[0][0], raw_points[0][1])] # (dist, x, y)
        
        for i in range(1, len(raw_points)):
            p_prev = raw_points[i-1]
            p_curr = raw_points[i]
            dx = p_curr[0] - p_prev[0]
            dy = p_curr[1] - p_prev[1]
            d = math.sqrt(dx*dx + dy*dy)
            dist += d
            self.points.append((dist, p_curr[0], p_curr[1]))

    def get_point(self, distance):
        """Get (x, y) at specific distance along path."""
        # Clamp distance
        if distance <= 0:
            return self.points[0][1], self.points[0][2]
        if distance >= self.total_length:
            return self.points[-1][1], self.points[-1][2]

        # Binary search for performance (or just linear given resolution)
        # Linear search is fine for now
        for i in range(len(self.points) - 1):
            d1, x1, y1 = self.points[i]
            d2, x2, y2 = self.points[i+1]
            
            if d1 <= distance <= d2:
                # Interpolate
                ratio = (distance - d1) / (d2 - d1) if d2 > d1 else 0
                x = x1 + (x2 - x1) * ratio
                y = y1 + (y2 - y1) * ratio
                return x, y
        
        return self.points[-1][1], self.points[-1][2]
