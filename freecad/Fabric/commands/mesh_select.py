# -*- coding: utf-8 -*-
import FreeCAD as App
import FreeCADGui as Gui


class MyMesh:
    def __init__(self):
        self.Points = []
        self.Facets = []

    def add_facet(self, points, normal):
        self.Facets.append((points, normal))
        
    def get_point(self, index):
        """Return the point at the given index."""
        return self.Points[index]

    def get_facet_normals(self):
        """Return a list of all facet normal vectors."""
        return [facet[3] for facet in self.Facets]
        
    def get_facet_normal(self,index):
        """Return a list of all facet normal vectors."""
        return self.Facets[index][3]

    def get_facet_points(self, index):
        """Return the three points of the facet at the given index."""
        i, j, k, _ = self.Facets[index]
        return [self.get_point(i), self.get_point(j), self.get_point(k)]
        
    def get_plane_from_facet(self, index):
        """
        Returns the plane equation coefficients [a, b, c, d] for the given facet.
        
        Parameters:
        - index (int): Index of the facet in the self.Facets list.
        
        Returns:
        - np.ndarray: Plane equation coefficients [a, b, c, d].
        """
        facet = self.Facets[index]
        point_index = facet[0]
        normal = np.array(facet[1])  # Convert to NumPy array
        point = np.array(facet[0][0])  # Convert point to NumPy array
        print(point)

        a, b, c = normal
        x0, y0, z0 = point
        d = -(a * x0 + b * y0 + c * z0)

        return np.array([a, b, c, d])
import math

def distance_vectors(V0,V1):
    return math.sqrt(math.pow(V1[0]-V0[0],2)+math.pow(V1[1]-V0[1],2)+math.pow(V1[2]-V0[2],2))
    
import numpy as np

def plane_intersects_triangle(plane, triangle):
    a, b, c, d = plane
    v0, v1, v2 = triangle

    # Signed distance from plane to point
    def signed_distance(p):
        return a * p[0] + b * p[1] + c * p[2] + d

    d0 = signed_distance(v0)
    d1 = signed_distance(v1)
    d2 = signed_distance(v2)

    # Check if plane intersects the triangle
    if (d0 * d1 < 0) or (d1 * d2 < 0) or (d2 * d0 < 0):
        # Compute intersection points on edges
        points = []

        # Edge v0-v1
        if d0 * d1 < 0:
            t = -d0 / (d1 - d0)
            p = (v0[0] + t * (v1[0] - v0[0]),
                 v0[1] + t * (v1[1] - v0[1]),
                 v0[2] + t * (v1[2] - v0[2]))
            points.append(p)

        # Edge v1-v2
        if d1 * d2 < 0:
            t = -d1 / (d2 - d1)
            p = (v1[0] + t * (v2[0] - v1[0]),
                 v1[1] + t * (v2[1] - v1[1]),
                 v1[2] + t * (v2[2] - v1[2]))
            points.append(p)

        # Edge v2-v0
        if d2 * d0 < 0:
            t = -d2 / (d0 - d2)
            p = (v2[0] + t * (v0[0] - v2[0]),
                 v2[1] + t * (v0[1] - v2[1]),
                 v2[2] + t * (v0[2] - v2[2]))
            points.append(p)

        # Return the line segment
        if len(points) == 2:
            return (points[0], points[1])
    return None

def line_plane_intersection(line, plane):
    """
    Find the intersection point between a line and a plane.
    line: (point, direction)
    plane: (normal, point)
    Returns the point of intersection, or None if they are parallel.
    """
    point, direction = line
    normal, plane_point = plane
    denom = np.dot(normal, direction)
    if abs(denom) < 1e-10:
        return None  # Lines are parallel or colinear

    t = np.dot((plane_point - point), normal) / denom
    return point + t * direction

def line_triangle_intersection(line, triangle):
    """
    Find the segment of the line that lies inside the triangle.
    line: (point, direction)
    triangle: (p1, p2, p3)
    Returns a segment (start, end) of the line that is inside the triangle.
    """
    # Find all intersection points of the line with the triangle edges
    p1, p2, p3 = triangle
    line_point, line_dir = line

    # Check line with each edge of the triangle
    intersections = []
    for i in range(3):
        p1_edge = triangle[i]
        p2_edge = triangle[(i+1)%3]
        edge_intersection = line_segment_segment_intersection(
            (line_point, line_dir), (p1_edge, p2_edge)
        )
        if edge_intersection is not None:
            intersections.append(edge_intersection)

    if len(intersections) == 0:
        return None  # Line is entirely outside the triangle

    # Sort the intersection points along the line
    t_values = [np.dot((p - line_point), line_dir) for p in intersections]
    t_values.sort()
    t_min, t_max = t_values[0], t_values[-1]
    segment_start = line_point + t_min * line_dir
    segment_end = line_point + t_max * line_dir

    return (segment_start, segment_end)

def line_segment_segment_intersection(line, segment):
    """
    Find the intersection point between a line and a line segment.
    line: (point, direction)
    segment: (p1, p2)
    Returns the point of intersection, or None if no intersection.
    """
    point, direction = line

    p1, p2 = segment
    p1 = np.array(p1)
    p2 = np.array(p2)
    
    # Find the direction vector of the segment
    seg_dir = p2 - p1
    denom = np.dot(direction, seg_dir)
    if abs(denom) < 1e-10:
        return None  # Lines are parallel

    t = np.dot((p1 - point), seg_dir) / denom
    if t < 0 or t > 1:
        return None  # No intersection with the segment

    return point + t * direction

def compute_intersection_line(plane1, plane2):
    """
    Compute the line of intersection between two planes.
    plane1 and plane2 are tuples (normal, point).
    Returns a line as (point, direction).
    """
    n1, p1 = plane1
    n2, p2 = plane2

    # Convert tuples to NumPy arrays for arithmetic operations
    n1 = np.array(n1)
    n2 = np.array(n2)
    p1 = np.array(p1)
    p2 = np.array(p2)

    direction = np.cross(n1, n2)
    if np.linalg.norm(direction) < 1e-10:
        return None  # Planes are parallel or coincident

    # Find a point on the line of intersection
    t = np.dot((p2 - p1), n1) / np.dot(n1, n1)
    point = p1 + t * n1

    return (point, direction)


def find_intersection_segments(mesh1, mesh2):
    intersections = []

    for f1 in mesh1.Facets:
        for f2 in mesh2.Facets:
            # Extract the normal and a point from each facet
            normal1 = f1[3]
            normal2 = f2[3]
            point1 = mesh1.get_point(f1[0])
            point2 = mesh2.get_point(f2[0])

            # Compute the line of intersection between the two planes
            line = compute_intersection_line((normal1, point1), (normal2, point2))
            if line is None:
                continue

            # Build the triangles for each facet
            triangle1 = (
                mesh1.get_point(f1[0]),
                mesh1.get_point(f1[1]),
                mesh1.get_point(f1[2])
            )
            triangle2 = (
                mesh2.get_point(f2[0]),
                mesh2.get_point(f2[1]),
                mesh2.get_point(f2[2])
            )

            # Find the segment of the line that lies within both triangles
            seg1 = line_triangle_intersection(line, triangle1)
            seg2 = line_triangle_intersection(line, triangle2)

            if seg1 is not None and seg2 is not None:
                intersections.append((seg1[0], seg2[0]))  # Add the full segment

    return intersections
     
def convert_freeCAD_to_your_mesh(freeCAD_mesh):
    """
    Converts a FreeCAD mesh (with Facets) into your custom Mesh class.
    """

    # Step 3: Process each facet to get indices and normal
    mesh = MyMesh()

    indexpt=0
    for facet in freeCAD_mesh.Facets:
        p1 = facet.Points[0]
        p2 = facet.Points[1]
        p3 = facet.Points[2]
        normal = facet.Normal
        mesh.Points.append(p1)
        mesh.Points.append(p2)
        mesh.Points.append(p3)        
 
        i = indexpt
        indexpt+=1
        j = indexpt
        indexpt+=1
        k = indexpt
        indexpt+=1

        mesh.add_facet((p1, p2, p3), normal)

    return mesh
    
import Draft
    
def create_continuous_polyline(segments, tolerance=0.05):
    # Step 1: Collect all points
    all_points = []
    for seg in segments:
        all_points.append(seg[0])
        all_points.append(seg[1])

    # Step 2: Remove duplicates using a tolerance
    unique_points = []
    for point in all_points:
        is_duplicate = False
        for up in unique_points:
            if np.linalg.norm(point - up) < tolerance:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_points.append(point)

    # Step 3: Sort points to form a continuous path
    # For simplicity, we sort by x-coordinate (you can adjust this logic)
    unique_points.sort(key=lambda p: p[0])

    # Step 4: Create a polyline in FreeCAD
    if len(unique_points) < 2:
        print("Not enough points to form a polyline.")
        return

    # Convert NumPy arrays to tuples for FreeCAD
    points = [App.Vector(p) for p in unique_points]
    #print(points)
    wire = Draft.make_wire(points, closed=False, placement=None, face=None, support=None)

    # Create a polyline
    #wire = Part.Wire([Part.Edge(Part.LineSegment(points[i], points[i+1])) for i in range(len(points)-1)])
    #part = Part.Shape(wire)
    doc = App.ActiveDocument
    #doc.addObject("Part::Feature", "Polyline").Shape = part
    doc.recompute()
    App.Console.PrintMessage("Polyline created with tolerance: %.2f\n" % tolerance)
    
def cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def is_point_in_triangle(P, A, B, C):
    v0 = (C[0]-A[0], C[1]-A[1], C[2]-A[2])
    v1 = (B[0]-A[0], B[1]-A[1], B[2]-A[2])
    v2 = (P[0]-A[0], P[1]-A[1], P[2]-A[2])

    dot00 = dot(v0, v0)
    dot01 = dot(v0, v1)
    dot02 = dot(v0, v2)
    dot11 = dot(v1, v1)
    dot12 = dot(v1, v2)

    denominator = dot00 * dot11 - dot01 * dot01

    if abs(denominator) < 1e-10:
        return False

    u = (dot11 * dot02 - dot01 * dot12) / denominator
    v = (dot00 * dot12 - dot01 * dot02) / denominator

    return (u >= 0) and (v >= 0) and (u + v <= 1)

def line_segment_triangle_intersection(S, E, A, B, C):
    # Compute the plane of the triangle
    N = cross((B[0] - A[0], B[1] - A[1], B[2] - A[2]), 
              (C[0] - A[0], C[1] - A[1], C[2] - A[2]))

    if N == (0, 0, 0):
        return None  # Degenerate triangle

    # Check if the line segment lies on the plane
    S_plane = dot(N, (S[0] - A[0], S[1] - A[1], S[2] - A[2]))
    E_plane = dot(N, (E[0] - A[0], E[1] - A[1], E[2] - A[2]))

    if abs(S_plane) < 1e-10 and abs(E_plane) < 1e-10:
        # Line segment lies on the plane
        # Check if endpoints are inside the triangle
        if is_point_in_triangle(S, A, B, C):
            return S
        if is_point_in_triangle(E, A, B, C):
            return E

        # If not, check for intersection with triangle edges
        # (This part is complex and not fully implemented here)

        return None

    # If the line is not on the plane, find the intersection
    t_numerator = -S_plane
    t_denominator = dot(N, (E[0] - S[0], E[1] - S[1], E[2] - S[2]))

    if abs(t_denominator) < 1e-10:
        return None  # Line is parallel to the plane

    t = t_numerator / t_denominator

    if t < 0 or t > 1:
        return None  # Intersection outside the segment

    # Compute the intersection point
    P = (
        S[0] + t * (E[0] - S[0]),
        S[1] + t * (E[1] - S[1]),
        S[2] + t * (E[2] - S[2])
    )

    if is_point_in_triangle(P, A, B, C):
        return P

    return None

import math
import numpy as np

def angle_between_vectors(v1, v2):
    """
    Calculate the angle between two 3D vectors.
    
    Parameters:
    v1, v2: list or tuple of 3 numbers representing 3D vectors
    
    Returns:
    float: angle in radians
    """
    # Convert to numpy arrays if they aren't already
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    # Calculate dot product
    dot_product = np.dot(v1, v2)
    
    # Calculate magnitudes
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    
    # Calculate cosine of angle
    cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
    
    # Handle floating point errors (clamp to [-1, 1])
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    # Calculate and return angle in radians
    angle_rad = np.arccos(cos_angle)
    
    return angle_rad
    
def cos_between_vectors(v1, v2):
    """
    Calculate the angle between two 3D vectors.
    
    Parameters:
    v1, v2: list or tuple of 3 numbers representing 3D vectors
    
    Returns:
    float: angle in radians
    """
    # Convert to numpy arrays if they aren't already
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    # Calculate dot product
    dot_product = np.dot(v1, v2)
    
    # Calculate magnitudes
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    
    # Calculate cosine of angle
    cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
    
    # Handle floating point errors (clamp to [-1, 1])
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    return cos_angle
    
def Arrange_curve(curve,direction):
    len_curve=len(curve)
    Curve_direction = App.Vector(curve[len_curve-1][0]-curve[0][0],curve[len_curve-1][1]-curve[0][1],curve[len_curve-1][2]-curve[0][2])
    factor = cos_between_vectors(direction,Curve_direction)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(curve)
    print(direction,Curve_direction,factor)
    
    if factor >0.0:
        curve=curve[::-1]
    print(curve)
    print("------------------------------------------------------------------")
    return curve

def cut_mesh_with_plan(mesh1,mesh2):
    
    # Plane: x + y = 0.5 → x + y + 0*z - 0.5 = 0
    plane = mesh2.get_plane_from_facet(0)
    
    print("plane")
    print(plane)
    plane_normal=App.Vector(plane[0],plane[1],plane[2])
    print("plane_normal")
    print(plane_normal)
    
    #use the plane main coordinate to orient curve
    
    #cut the mesh with a plan
    segment_array=[]
    normal_array=[]
    for facet in mesh1.Facets:
        triangle=facet[0]
        segment = plane_intersects_triangle(plane, triangle)   
        if segment:
            segment_array.append(segment)
            normal_array.append(facet[1])
            #points = [App.Vector(p) for p in segment]
            #need to feed facet normal
    
    point_array=[]
    seg_array=[]
    
    # round point to be sure that the tolerance fit
    for i in range(len(segment_array)):
        seg_tmp=[App.Vector(round(segment_array[i][0][0],3),round(segment_array[i][0][1],3),round(segment_array[i][0][2],3)),App.Vector(round(segment_array[i][1][0],3),round(segment_array[i][1][1],3),round(segment_array[i][1][2],3)),normal_array[i]]
        if seg_tmp[0]!=seg_tmp[1]:
            seg_array.append(seg_tmp)
    #remove extra points
    index_seg=1
    N_array=[]
    for i in range(len(seg_array)):
        points = [App.Vector(p) for p in seg_array[i]]
        p0=points[0]
        p1=points[1]
        N=points[2]
        p0_exist=False
        p1_exist=False
        for j in range(len(seg_array)):
            if i!=j:
                points = [App.Vector(p) for p in seg_array[j]]
                if p0==points[0] or p0==points[1]:
                    p0_exist=True
                if p1==points[0] or p1==points[1]:
                    p1_exist=True
        if p0_exist==False:
            point_array.append(p0)
            N_array.append(N)
        if p1_exist==False:
            point_array.append(p1)
            N_array.append(N)
        index_seg+=1
#    print(point_array)  
    print("n_array")
    print(N_array)
    multi=False
    if(len(point_array)>2):
        print("multi seg")
        print(point_array)

        Mesh2_pts=mesh2.Facets[0]
        Mesh2_dir=App.Vector(mesh2.Facets[0][0][1][0]-mesh2.Facets[0][0][0][0],mesh2.Facets[0][0][1][1]-mesh2.Facets[0][0][0][1],mesh2.Facets[0][0][1][2]-mesh2.Facets[0][0][0][2])
        print(Mesh2_pts[0],Mesh2_dir)
        multi=True
        index_2_delete=[]
        dist=[]
        for i in range(len(point_array)):
            pt_arr_dir=App.Vector(point_array[i][0]-mesh2.Facets[0][0][0][0],point_array[i][1]-mesh2.Facets[0][0][0][1],point_array[i][2]-mesh2.Facets[0][0][0][2])
            ratio = cos_between_vectors(Mesh2_dir,pt_arr_dir)
            print(pt_arr_dir)
            print(ratio)
            dist.append(ratio*distance_vectors(Mesh2_pts[0][0],point_array[i]))
        sorted_ind = sorted(range(len(dist)),key=dist.__getitem__)
        sorted_ind=sorted_ind[::-1]
        print(sorted_ind)#[3, 0, 2, 1] connect 0 and 2
#        for i in range(1,len(sorted_ind)-1,2):
#            seg_tmp=[point_array[i],point_array[i+1]]
#            print("seg_tmp")
#            print(seg_tmp)
#            seg_array.append(seg_tmp)
#        del point_array[1:-1]
#        del N_array[1:-1]#TODO do it 2 by 2
        
        Norm = App.Vector((N_array[0][0]+N_array[0][0])/2.0,(N_array[0][1]+N_array[0][1])/2.0,(N_array[0][2]+N_array[0][2])/2.0)
        seg_tmp=[point_array[0],point_array[2],Norm]
        seg_array.append(seg_tmp)
        del point_array[0]
        del point_array[1]
        del N_array[0]
        del N_array[1]
#        print(point_array,N_array)
#        print("---------------------------------")
#        print(seg_array)
#        print("---------------------------------")

        #re-arrange point_array and n_array: [Vector (-0.005, 49.999, 200.0), Vector (50.705, 0.0, 194.361), Vector (0.005, 49.999, 200.0), Vector (-50.705, 0.0, 194.361)]
        #[Vector (-0.19024121761322021, 0.956407368183136, 0.2215699851512909), Vector (0.990969181060791, 0.051342807710170746, 0.12387114763259888), Vector (0.19024120271205902, 0.9564073085784912, 0.2215699851512909), Vector (-0.990969181060791, 0.051342789083719254, 0.12387114763259888)]
        #plane norm [ 0.00000000e+00  4.61272976e-01 -4.09008900e+00  7.94954642e+02]

    #find the first starting point (opened curve)    
    final_seg=[]
    next_point=None 
    last_index=0
    p_start=point_array[0]
    for i in range(len(seg_array)):
        points = [App.Vector(p) for p in seg_array[i]]
        if points[0]==p_start:
            print("start here : ",i,"0")
            next_point=points[1]
            last_index=i
    
            final_seg.append([points[0],points[1],i,N_array[0]])
            break
        if points[1]==p_start:
            print("start here : ",i,"1")
            next_point=points[0]
            last_index=i
#            print(i)
            final_seg.append([points[1],points[0],i,N_array[1]])
            break
#    print(last_index,next_point)
#    print(final_seg)
#    print("***********************************************")

    #find all the next point connected together in order
    for j in range(len(seg_array)):
        for i in range(len(seg_array)):
            if i!=last_index:
                points = [App.Vector(p) for p in seg_array[i]]
                if next_point==points[0]:
                    print("next here : ",i,"0")
                    last_index=i
                    next_point=points[1]
                    final_seg.append([points[0],points[1],i,points[2]])
                    break
                if next_point==points[1]:
                    print("next here : ",i,"1")
                    last_index=i
                    next_point=points[0]
                    final_seg.append([points[1],points[0],i,points[2]])
                    break
    print(final_seg)

#    if multi==True : 
#        print("multi seg")
#        exit()
#    print(final_seg)
    #connect all the points
    final_wire=[]
    final_norm=[]
    final_norm.append(final_seg[0][3])
    final_wire.append(final_seg[0][0])
    
    for seg in final_seg:
        final_wire.append(seg[1])
        final_norm.append(seg[3])
#    print(final_wire)
#    print(final_norm)
    return final_wire,final_norm,plane_normal
    #create a wire with the point coordinates
    #check if multiple segment here
    
import numpy as np

def closest_points_on_segments(p1, p2, p3, p4):
    """
    Find the closest points between two 3D line segments.
    
    Parameters:
    p1, p2: Endpoints of first segment (3D points)
    p3, p4: Endpoints of second segment (3D points)
    
    Returns:
    tuple: (point_on_segment1, point_on_segment2, distance)
    """
    # Convert to numpy arrays
    p1, p2, p3, p4 = np.array(p1), np.array(p2), np.array(p3), np.array(p4)
    
    # Vector from p1 to p2
    d1 = p2 - p1
    # Vector from p3 to p4
    d2 = p4 - p3
    
    # Vector between starting points
    r = p1 - p3
    
    # Dot products
    a = np.dot(d1, d1)  # |d1|^2
    b = np.dot(d1, d2)  # d1 · d2
    c = np.dot(d2, d2)  # |d2|^2
    d = np.dot(r, d1)   # r · d1
    e = np.dot(r, d2)   # r · d2
    
    # Calculate parameters for closest points
    denom = a * c - b * b
    
    # If lines are parallel (or nearly parallel)
    if abs(denom) < 1e-10:
        # Use the midpoint of the perpendicular distance
        t1 = 0.0
        t2 = e / c if abs(c) > 1e-10 else 0.0
    else:
        t1 = (b * e - c * d) / denom
        t2 = (a * e - b * d) / denom
    
    # Clamp parameters to [0, 1] to stay within segments
    t1 = max(0.0, min(1.0, t1))
    t2 = max(0.0, min(1.0, t2))
    
    # Calculate closest points on segments
    closest_point1 = p1 + t1 * d1
    closest_point2 = p3 + t2 * d2
    
    # Distance between closest points
    distance = np.linalg.norm(closest_point1 - closest_point2)
    
    return closest_point1, closest_point2, distance

def find_intersection(p1, p2, p3, p4, tolerance=1e-8):
    """
    Find intersection of two 3D line segments.
    
    Parameters:
    p1, p2: Endpoints of first segment
    p3, p4: Endpoints of second segment
    tolerance: Distance tolerance for considering segments as intersecting
    
    Returns:
    tuple: (intersection_point, is_intersecting)
    """
    closest1, closest2, distance = closest_points_on_segments(p1, p2, p3, p4)
    
    # Check if segments intersect (distance is very small)
    is_intersecting = distance < tolerance
    
    if is_intersecting:
        # Return the intersection point (average of closest points)
        intersection = (closest1 + closest2) / 2
        return intersection, True
    else:
        return closest1, False
    
import numpy as np

def create_numpy_lookup(data):
    """Create lookup using NumPy arrays for better performance"""
    
    # Create a dictionary with tuple keys
    lookup = {}
    index_map = {}  # (x,y) -> index
    points_list = []  # List of all points for indexed access
    max_x = float('-inf')
    max_y = float('-inf')
    for index, (x, y, coord_array) in enumerate(data):
        point_data = np.array([coord_array[0], coord_array[1], coord_array[2]])
        lookup[(x, y)] = point_data
        index_map[(x, y)] = index
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        points_list.append((x, y, point_data))

    
    return lookup,max_x,max_y, index_map, points_list

def get_3d_point(x, y, point_lookup):
    """Get 3D point by (x,y) coordinates"""
    return point_lookup.get((x, y), None)

def get_point_index(x, y):
    """Get index of point by (x,y) coordinates"""
    return index_map.get((x, y), -1)  # Return -1 if not found

def get_point_by_index(index):
    """Get point by its index"""
    if 0 <= index < len(points_list):
        return points_list[index]
    return None
    
# doc = App.getDocument("mesh_ex")
# obj = doc.getObject("Mesh")
# obj = doc.getObject("Mesh001")

def create_mesh(doc,mesh1, mesh2):
    obj = doc.getObject("Mesh")
    result_mesh = convert_freeCAD_to_your_mesh(mesh1.Mesh)
    #print(result_mesh.Facets)
    #print(result_mesh.Points)
    #print(result_mesh.get_point(0))


    mesh1=result_mesh
    obj = doc.getObject("Mesh001")
    result_mesh = convert_freeCAD_to_your_mesh(mesh2.Mesh)
    mesh2=result_mesh

    fw,nm,pn = cut_mesh_with_plan(mesh1,mesh2)



    wire = Draft.make_wire(fw, closed=False, placement=None, face=None, support=None)
    doc.recompute()

    #
    #
    #S = (0, 0, 0)
    #E = (0.5, 0.5, 0.5)
    #A = (0, 0, 0.5)
    #B = (1, 0, 0.5)
    #C = (0, 1, 0.5)
    #
    #intersection = line_segment_triangle_intersection(S, E, A, B, C)
    #print("Intersection point:", intersection)


    num_points = 10


    #approximation
    import numpy as np
    from scipy.interpolate import splprep, splev
    points = np.array(fw)
    #print(points)
    tck, u = splprep(points.T, k=2, s=0.5)


    u_new = np.linspace(0, 1, num=num_points)
    curve = splev(u_new, tck, der=0)

    wir=[]

    for i in range(num_points):
        wir.append(App.Vector(curve[0][i],curve[1][i],curve[2][i]))

    directu=App.Vector(0.0,0.0,1.0)
    wir = Arrange_curve(wir,directu)

    #wire = Draft.make_wire(wir, closed=False, placement=None, face=None, support=None)
    doc.recompute()
    last_len=0
    curr_len=0
    fw_max_len=[]
    pnc=None

    U_curve=[]
    V_curve=[]

    directu=pn
    directv=App.Vector(curve[len(curve)-1][0]-curve[0][0],curve[len(curve)-1][1]-curve[0][1],curve[len(curve)-1][2]-curve[0][2])
    old_col=None
    for i in range(0,len(wir)-1):
    #    create a vector
        if(i==num_points-1):
            col_vector=old_col
        else : 
            col_vector=App.Vector(wir[i+1][0]-wir[i][0],wir[i+1][1]-wir[i][1],wir[i+1][2]-wir[i][2])
            old_col=col_vector #store for the last point of the curve
        nm_vector = cross(col_vector,pn)
        p0=wir[i]
        p1=App.Vector(wir[i][0]+pn[0],wir[i][1]+pn[1],wir[i][2]+pn[2])
        p2=App.Vector(wir[i][0]+nm_vector[0],wir[i][1]+nm_vector[1],wir[i][2]+nm_vector[2])
        
        mesh_p = MyMesh()
        mesh_p.add_facet((p0,p1,p2),col_vector)
        fwc,nmc,pnc = cut_mesh_with_plan(mesh1,mesh_p)
        fwc = Arrange_curve(fwc,directu)
        wire = Draft.make_wire(fwc, closed=False, placement=None, face=None, support=None)
        doc.recompute()
        U_curve.append((fwc,nmc,pnc))
        
        curr_len=0
        for j in range(len(fwc)-1):
            curr_len += distance_vectors(fwc[j],fwc[j+1])
        if curr_len>=last_len:
            fw_max_len=fwc
            last_len=curr_len
            pnc=pn
            

    points = np.array(fw_max_len)
    tck, u = splprep(points.T, k=2, s=0.5)
    #num_points = 50
    u_new = np.linspace(0, 1, num=num_points)
    curve = splev(u_new, tck, der=0)
    wir_c=[]

    for j in range(num_points):
        wir_c.append(App.Vector(curve[0][j],curve[1][j],curve[2][j]))

    wire = Draft.make_wire(wir_c, closed=False, placement=None, face=None, support=None)
    doc.recompute()

    old_col=None
    for j in range(0,num_points):
        if(j==num_points-1):
            col_vector=old_col
        else : 
            col_vector=App.Vector(wir_c[j+1][0]-wir_c[j][0],wir_c[j+1][1]-wir_c[j][1],wir_c[j+1][2]-wir_c[j][2])
            old_col=col_vector #store for the last point of the curve

        nm_vector = cross(col_vector,pnc)
        p0=wir_c[j]
        p1=App.Vector(wir_c[j][0]+pnc[0],wir_c[j][1]+pnc[1],wir_c[j][2]+pnc[2])
        p2=App.Vector(wir_c[j][0]+nm_vector[0],wir[j][1]+nm_vector[1],wir_c[j][2]+nm_vector[2])
        
        mesh_p = MyMesh()
        mesh_p.add_facet((p0,p1,p2),col_vector)
        fwc,nmc,pnc = cut_mesh_with_plan(mesh1,mesh_p)
        fwc = Arrange_curve(fwc,directv)
        wire = Draft.make_wire(fwc, closed=False, placement=None, face=None, support=None)
        doc.recompute()
        V_curve.append((fwc,nmc,pnc))
            


    U_array=[]
    wir=[]
    v_index=0
    u_index=0;
    for V in V_curve:
        wir.append(V[0][0])
    #    U_array.append((u_index-1,v_index,V[0][len(V[0])-1]))
        for j in range(len(V[0])-1):
            p2=V[0][j]
            p3=V[0][j+1]
            u_index=0;  
    #        U_array.append((u_index,v_index-1,V[0][0]))   
            for U in U_curve:
                for i in range(len(U[0])-1):
                    p0=U[0][i]
                    p1=U[0][i+1]
            
                    intersection, is_intersecting = find_intersection(p0, p1, p2, p3,tolerance=0.001)
                    if is_intersecting:
                        print(u_index,v_index,f"Segments intersect at: {intersection}")
                        U_array.append((u_index,v_index,intersection))
                        wir.append(App.Vector(intersection))
                        break
    #                    doc.addObject("Part::Vertex","Vertex")
    #                    doc.Vertex.Placement=App.Placement(App.Vector(intersection[0],intersection[1],intersection[2]),App.Rotation(App.Vector(0.00,0.00,1.00),0.00))
                u_index+=1
    #        U_array.append((u_index,v_index+1,V[0][0]))
        wir.append(V[0][len(V[0])-1])
        v_index+=1
            
    print(U_array)
    #wire = Draft.make_wire(wir, closed=False, placement=None, face=None, support=None)
    doc.recompute()
            
    # Create lookup table
    point_lookup,mx,my,index_map, vertices  = create_numpy_lookup(U_array)

    import Mesh

    facets=[]
    for u in range(mx):
        for v in range(my+1):
    #        p0= get_point_index(u, v)
    #        p1= get_point_index(u+1, v)
    #        p2= get_point_index(u+1, v+1)
    #        if (p0!=-1) and (p1!=-1) and (p2!=-1) :
    #            facets.append([p0,p1,p2])
    #        p0= get_point_index(u, v)
    #        p1= get_point_index(u, v+1)
    #        p2= get_point_index(u+1, v+1)
    #        if (p0!=-1) and (p1!=-1) and (p2!=-1) :
    #            facets.append([p0,p1,p2])
            first_p0=None
            second_p0=None
            first_p2=None
            second_p2=None
            p0= get_3d_point(u, v,point_lookup)
            p1= get_3d_point(u+1, v,point_lookup)
            p2= get_3d_point(u+1, v+1,point_lookup)
            First_tri_p0=False
            First_tri_p2=False
            if (p0 is not None) and (p1 is not None) and (p2 is not None) :
                facets.append([p0,p1,p2])
            if (p0 is None) and (p1 is not None) and (p2 is not None) :
                p0=V_curve[v][0][0]
                first_p0=p0
                facets.append([p0,p1,p2])
            if (p0 is not None) and (p1 is not None) and (p2 is None) :
                p2=U_curve[u+1][0][len(U_curve[u+1][0])-1]
                first_p2=p2
                facets.append([p0,p1,p2])
            if (p0 is None) and (p1 is not None) and (p2 is None) :
                p0=V_curve[v][0][0]
                p2=U_curve[u+1][0][len(U_curve[u+1][0])-1]
                facets.append([p0,p1,p2])
    #        if (p0 is not None) and (p1 is None) and (p2 is None) :
    #            p1=V_curve[v][0][len(V_curve[v][0])-1]
    #            p2=V_curve[v+1][0][len(V_curve[v+1][0])-1]
    #            facets.append([p0,p1,p2])
            p0= get_3d_point(u, v,point_lookup)
            p2= get_3d_point(u, v+1,point_lookup)
            p1= get_3d_point(u+1, v+1,point_lookup)
            if (p0 is not None) and (p1 is not None) and (p2 is not None) :
                facets.append([p0,p1,p2])
            if (p0 is not None) and (p1 is not None) and (p2 is None) :
                p2=V_curve[v+1][0][0]
                second_p2=p2
                facets.append([p0,p1,p2])
                First_tri_p2=True
            if (p0 is not None) and (p1 is None) and (p2 is None) :
                p2=U_curve[u][0][len(U_curve[u][0])-1]
                p1=U_curve[u+1][0][len(U_curve[u+1][0])-1]
                facets.append([p0,p1,p2])
            if (p0 is None) and (p1 is not None) and (p2 is not None) :
                p0=U_curve[u][0][0]
                second_p0=p0
                facets.append([p0,p1,p2])
                First_tri_p0=True
    #        if (p0 is not None) and (p1 is None) and (p2 is not None) :
    #            p1=V_curve[v+1][0][len(V_curve[v+1][0])-1]
    #            facets.append([p0,p1,p2])

            if(first_p0 is not None) and (second_p0 is not None) and (p1 is not None):
                facets.append([first_p0,p1,second_p0])
    #        if(first_p2 is not None) and (second_p2 is not None) and (p0 is not None):
    #            facets.append([p0,first_p2,second_p2])
                
                
            first_p0=None
            second_p0=None
            p0= get_3d_point(u, v,point_lookup)
            p1= get_3d_point(u+1, v,point_lookup)
            p2= get_3d_point(u+1, v+1,point_lookup)
            if (p0 is None) and (p1 is None) and (p2 is not None) :
                #find if U or V+1 is the closest point
                if First_tri_p0:
                    p0=U_curve[u][0][0]
                    p1=U_curve[u+1][0][0]
                    facets.append([p0,p1,p2])
                else:
                    p0=V_curve[v+1][0][0]
                    p1=U_curve[u+1][0][0]
                    facets.append([p0,p1,p2])
            first_p2=None
            second_p2=None
            p0= get_3d_point(u, v,point_lookup)
            p2= get_3d_point(u, v+1,point_lookup)
            p1= get_3d_point(u+1, v+1,point_lookup)
            if (p0 is not None) and (p1 is not None) and (p2 is None) :
                if First_tri_p2:
                    p1=V_curve[v+1][0][0]
                    p2=U_curve[u][0][len(U_curve[u][0])-1]
                    facets.append([p0,p1,p2])
    #            else:
    #                p0=V_curve[v+1][0][0]
    #                p1=U_curve[u+1][0][0]
    #                facets.append([p0,p1,p2])
    #print(facets)
    u=0
    for v in range(0,my):
        p0= V_curve[v][0][0]
        p1= get_3d_point(u, v,point_lookup)
        p2= get_3d_point(u, v+1,point_lookup)
        first_tri=False
        if (p0 is not None) and (p1 is not None) and (p2 is not None) :
            facets.append([p0,p1,p2])
            first_tri=True
        p1=p2
        p2= V_curve[v+1][0][0]
        if (p0 is not None) and (p1 is not None) and (p2 is not None) and (first_tri==True):
            facets.append([p0,p1,p2])
    u=mx
    for v in range(0,my):
        p0= get_3d_point(u, v,point_lookup)
        p1= V_curve[v][0][len(V_curve[v][0])-1]
        p2= V_curve[v+1][0][len(V_curve[v+1][0])-1]
        if (p0 is not None) and (p1 is not None) and (p2 is not None) :
            facets.append([p0,p1,p2])
        p1=p2
        p2= get_3d_point(u, v+1,point_lookup)
        if (p0 is not None) and (p1 is not None) and (p2 is not None) :
            facets.append([p0,p1,p2])
    ## Create mesh from data
    ## Convert to the format expected by fromData
    #mesh_data = []
    #for triangle in facets:
    #    # Each triangle is a list of 3 vertex indices
    #    mesh_data.append(triangle)
    #
    ## Create mesh using fromData (this is the correct way)
    #mesh = Mesh.Mesh()
    #mesh.setdata(vertices, facets)  # Use setdata instead
    #
    ## Add to document
    #obj = FreeCAD.ActiveDocument.addObject("Mesh::Feature", "MyMesh")
    #obj.Mesh = mesh
    #obj.recompute()


    # Create mesh data
    mesh_data = []
    for facet in facets:
        vertices = []
        for vertex in facet:
            vertices.append(App.Vector(vertex[0], vertex[1], vertex[2]))
        mesh_data.append(vertices)

    # Create the mesh object
    mesh = Mesh.Mesh()
    for vertices in mesh_data:
        mesh.addFacet(vertices[0], vertices[1], vertices[2])

    # Add to document
    obj = App.ActiveDocument.addObject("Mesh::Feature", "MyMesh")
    obj.Mesh = mesh
    doc.recompute()
    #

    ## Fast access
    #point1 = get_3d_point(10, 10,point_lookup)  # O(1) lookup
    #point2 = get_3d_point(10, 11,point_lookup)  # O(1) lookup
    #
    #print(point1)
    #print(point2)

class MeshSelectCommand:
    """Command to select mesh objects in FreeCAD."""

    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': 'Select Mesh',
            'ToolTip': 'Select all mesh objects in the document'
        }

    def Activated(self):
        # Get the current document
        doc = App.ActiveDocument
        if not doc:
            App.Console.PrintError("No active document\n")
            return
            
        # Select all mesh objects
        mesh_objects = []
        for obj in doc.Objects:
            if hasattr(obj, 'TypeId') and obj.TypeId == 'Mesh::Feature':
                mesh_objects.append(obj)
        
        # Select the objects
        if mesh_objects:
            Gui.Selection.clearSelection()
            for obj in mesh_objects:
                Gui.Selection.addSelection(obj)
            App.Console.PrintMessage(f"Selected {len(mesh_objects)} mesh objects\n")
            create_mesh(doc,mesh_objects[1],mesh_objects[0])
            # meshwork()
        else:
            App.Console.PrintMessage("No mesh objects found in document\n")

    def IsActive(self):
        # Command is active if there's an active document
        return App.ActiveDocument is not None

# Register the command
Gui.addCommand('MeshSelectCommand', MeshSelectCommand())

