import numpy as np
import numpy.linalg as la
from numpy import pi, arctan2, rad2deg
import math

class Vector(list):
    @staticmethod
    def Angle(vectorA, vectorB, mantissa=4):
        """
        Returns the angle in degrees between the two input vectors

        Parameters
        ----------
        vectorA : list
            The first vector.
        vectorB : list
            The second vector.
        mantissa : int, optional
            The length of the desired mantissa. The default is 4.

        Returns
        -------
        float
            The angle in degrees between the two input vectors.

        """
        n_v1=la.norm(vectorA)
        n_v2=la.norm(vectorB)
        if (abs(np.log10(n_v1/n_v2)) > 10):
            vectorA = vectorA/n_v1
            vectorB = vectorB/n_v2
        cosang = np.dot(vectorA, vectorB)
        sinang = la.norm(np.cross(vectorA, vectorB))
        return round(math.degrees(np.arctan2(sinang, cosang)), mantissa)
    
    @staticmethod
    def AzimuthAltitude(vector, mantissa=4):
        """
        Returns a dictionary of azimuth and altitude angles in degrees for the input vector. North is assumed to be the positive Y axis [0,1,0]. Up is assumed to be the positive Z axis [0,0,1].
        Azimuth is calculated in a counter-clockwise fashion from North where 0 is North, 90 is East, 180 is South, and 270 is West. Altitude is calculated in a counter-clockwise fashing where -90 is straight down (negative Z axis), 0 is in the XY plane, and 90 is straight up (positive Z axis).
        If the altitude is -90 or 90, the azimuth is assumed to be 0.

        Parameters
        ----------
        vectorA : list
            The input vector.
        mantissa : int, optional
            The length of the desired mantissa. The default is 4.

        Returns
        -------
        dict
            The dictionary containing the azimuth and altitude angles in degrees. The keys in the dictionary are 'azimuth' and 'altitude'. 

        """
        x, y, z = vector
        if x == 0 and y == 0:
            if z > 0:
                return {"azimuth":0, "altitude":90}
            elif z < 0:
                return {"azimuth":0, "altitude":-90}
            else:
                # undefined
                return None
        else:
            azimuth = math.degrees(math.atan2(y, x))
            if azimuth > 90:
                azimuth -= 360
            azimuth = round(90-azimuth, mantissa)
            xy_distance = math.sqrt(x**2 + y**2)
            altitude = math.degrees(math.atan2(z, xy_distance))
            altitude = round(altitude, mantissa)
            return {"azimuth":azimuth, "altitude":altitude}
    
    @staticmethod
    def ByAzimuthAltitude(azimuth, altitude, north=0, reverse=False):
        """
        Returns the vector specified by the input azimuth and altitude angles.

        Parameters
        ----------
        azimuth : float
            The input azimuth angle in degrees. The angle is computed in an anti-clockwise fashion. 0 is considered North, 90 East, 180 is South, 270 is West
        altitude : float
            The input altitude angle in degrees from the XY plane. Positive is above the XY plane. Negative is below the XY plane
        north : float , optional
            The angle of the north direction in degrees measured from positive Y-axis. The angle is added in anti-clockwise fashion. 0 is considered along the positive Y-axis,
            90 is along the positive X-axis, 180 is along the negative Y-axis, and 270 along the negative Y-axis.
        reverse : bool , optional
            If set to True the direction of the vector is computed from the end point towards the origin. Otherwise, it is computed from the origin towards the end point.

        Returns
        -------
        list
            The resulting vector.

        """
        from topologicpy.Vertex import Vertex
        from topologicpy.Edge import Edge
        from topologicpy.Topology import Topology
        e = Edge.ByVertices([Vertex.Origin(), Vertex.ByCoordinates(0,1,0)])
        e = Topology.Rotate(e, Vertex.Origin(), 1, 0, 0, altitude)
        e = Topology.Rotate(e, Vertex.Origin(), 0, 0, 1, -azimuth-north)
        if reverse:
            return Vector.Reverse(Edge.Direction(e))
        return Edge.Direction(e)
    
    @staticmethod
    def ByCoordinates(x, y, z):
        """
        Creates a vector by the specified x, y, z inputs.

        Parameters
        ----------
        x : float
            The X coordinate.
        y : float
            The Y coordinate.
        z : float
            The Z coodinate.

        Returns
        -------
        list
            The created vector.

        """
        return [x,y,z]
    
    @staticmethod
    def ByVertices(vertices, normalize=True):
        """
        Creates a vector by the specified input list of vertices.

        Parameters
        ----------
        vertices : list
            The the input list of topologic vertices. The first element in the list is considered the start vertex. The last element in the list is considered the end vertex.
        normalize : bool , optional
            If set to True, the resulting vector is normalized (i.e. its length is set to 1)

        Returns
        -------
        list
            The created vector.

        """

        from topologicpy.Vertex import Vertex
        import topologic
        if not isinstance(vertices, list):
            return None
        if not isinstance(normalize, bool):
            return None
        vertices = [v for v in vertices if isinstance(v, topologic.Vertex)]
        if len(vertices) < 2:
            return None
        v1 = vertices[0]
        v2 = vertices[-1]
        vector = [Vertex.X(v2)-Vertex.X(v1), Vertex.Y(v2)-Vertex.Y(v1), Vertex.Z(v2)-Vertex.Z(v1)]
        if normalize:
            vector = Vector.Normalize(vector)
        return vector

    @staticmethod
    def CompassAngle(vectorA, vectorB, mantissa=4, tolerance=0.0001):
        """
        Returns the horizontal compass angle in degrees between the two input vectors. The angle is measured in counter-clockwise fashion. Only the first two elements in the input vectors are considered.

        Parameters
        ----------
        vectorA : list
            The first vector.
        vectorB : list
            The second vector.
        mantissa : int, optional
            The length of the desired mantissa. The default is 4.
        tolerance : float , optional
            The desired tolerance. The default is 0.0001.

        Returns
        -------
        float
            The horizontal compass angle in degrees between the two input vectors.

        """
        if abs(vectorA[0]) < tolerance and abs(vectorA[1]) < tolerance:
            return None
        if abs(vectorB[0]) < tolerance and abs(vectorB[1]) < tolerance:
            return None
        p1 = (vectorA[0], vectorA[1])
        p2 = (vectorB[0], vectorB[1])
        ang1 = arctan2(*p1[::-1])
        ang2 = arctan2(*p2[::-1])
        return round(rad2deg((ang1 - ang2) % (2 * pi)), mantissa)

    @staticmethod
    def Coordinates(vector, outputType="xyz", mantissa=4):
        """
        Returns the coordinates of the input vector.

        Parameters
        ----------
        vector : list
            The input vector.
        outputType : string, optional
            The desired output type. Could be any permutation or substring of "xyz" or the string "matrix". The default is "xyz". The input is case insensitive and the coordinates will be returned in the specified order.
        mantissa : int , optional
            The desired length of the mantissa. The default is 4.

        Returns
        -------
        list
            The coordinates of the input vertex.

        """
        if not isinstance(vector, list):
            return None
        x = round(vector[0], mantissa)
        y = round(vector[1], mantissa)
        z = round(vector[2], mantissa)
        matrix = [[1,0,0,x],
                [0,1,0,y],
                [0,0,1,z],
                [0,0,0,1]]
        output = []
        outputType = outputType.lower()
        if outputType == "matrix":
            return matrix
        else:
            outputType = list(outputType)
            for axis in outputType:
                if axis == "x":
                    output.append(x)
                elif axis == "y":
                    output.append(y)
                elif axis == "z":
                    output.append(z)
        return output
    
    @staticmethod
    def Cross(vectorA, vectorB, mantissa=4, tolerance=0.0001):
        """
        Returns the cross product of the two input vectors. The resulting vector is perpendicular to the plane defined by the two input vectors.

        Parameters
        ----------
        vectorA : list
            The first vector.
        vectorB : list
            The second vector.
        mantissa : int, optional
            The length of the desired mantissa. The default is 4.
        tolerance : float, optional
            the desired tolerance. The default is 0.0001.

        Returns
        -------
        list
            The vector representing the cross product of the two input vectors.

        """
        if not isinstance(vectorA, list) or not isinstance(vectorB, list):
            return None
        if Vector.Magnitude(vector=vectorA, mantissa=mantissa) < tolerance or Vector.Magnitude(vector=vectorB, mantissa=mantissa) < tolerance:
            return None
        vecA = np.array(vectorA)
        vecB = np.array(vectorB)
        vecC = list(np.cross(vecA, vecB))
        if Vector.Magnitude(vecC) < tolerance:
            return None
        return [round(vecC[0], mantissa), round(vecC[1], mantissa), round(vecC[2], mantissa)]

    @staticmethod
    def Down():
        """
        Returns the vector representing the *down* direction. In Topologic, the negative ZAxis direction is considered *down* ([0,0,-1]).

        Returns
        -------
        list
            The vector representing the *down* direction.
        """
        return [0,0,-1]
    
    @staticmethod
    def East():
        """
        Returns the vector representing the *east* direction. In Topologic, the positive XAxis direction is considered *east* ([1,0,0]).

        Returns
        -------
        list
            The vector representing the *east* direction.
        """
        return [1,0,0]
    
    @staticmethod
    def IsCollinear(vectorA, vectorB, tolerance=0.1):
        """
        Returns True if the input vectors are collinear. Returns False otherwise.

        Parameters
        ----------
        vectorA : list
            The first input vector.
        vectorB : list
            The second input vector.

        Returns
        -------
        bool
            Returns True if the input vectors are collinear. Returns False otherwise.
        """

        return Vector.Angle(vectorA, vectorB) < tolerance

    @staticmethod
    def Magnitude(vector, mantissa=4):
        """
        Returns the magnitude of the input vector.

        Parameters
        ----------
        vector : list
            The input vector.
        mantissa : int
            The length of the desired mantissa. The default is 4.

        Returns
        -------
        float
            The magnitude of the input vector.
        """

        return round(np.linalg.norm(np.array(vector)), mantissa)

    @staticmethod
    def Multiply(vector, magnitude, tolerance=0.0001):
        """
        Multiplies the input vector by the input magnitude.

        Parameters
        ----------
        vector : list
            The input vector.
        magnitude : float
            The input magnitude.
        tolerance : float, optional
            the desired tolerance. The default is 0.0001.

        Returns
        -------
        list
            The created vector that multiplies the input vector by the input magnitude.

        """
        oldMag = 0
        for value in vector:
            oldMag += value ** 2
        oldMag = oldMag ** 0.5
        if oldMag < tolerance:
            return [0,0,0]
        newVector = []
        for i in range(len(vector)):
            newVector.append(vector[i] * magnitude / oldMag)
        return newVector

    @staticmethod
    def Normalize(vector):
        """
        Returns a normalized vector of the input vector. A normalized vector has the same direction as the input vector, but its magnitude is 1.

        Parameters
        ----------
        vector : list
            The input vector.

        Returns
        -------
        list
            The normalized vector.
        """

        return list(vector / np.linalg.norm(vector))

    @staticmethod
    def North():
        """
        Returns the vector representing the *north* direction. In Topologic, the positive YAxis direction is considered *north* ([0,1,0]).

        Returns
        -------
        list
            The vector representing the *north* direction.
        """
        return [0,1,0]
    
    @staticmethod
    def NorthEast():
        """
        Returns the vector representing the *northeast* direction. In Topologic, the positive YAxis direction is considered *north* and the positive XAxis direction is considered *east*. Therefore *northeast* is ([1,1,0]).

        Returns
        -------
        list
            The vector representing the *northeast* direction.
        """
        return [1,1,0]
    
    @staticmethod
    def NorthWest():
        """
        Returns the vector representing the *northwest* direction. In Topologic, the positive YAxis direction is considered *north* and the negative XAxis direction is considered *west*. Therefore *northwest* is ([-1,1,0]).

        Returns
        -------
        list
            The vector representing the *northwest* direction.
        """
        return [-1,1,0]
    
    @staticmethod
    def Reverse(vector):
        """
        Returns a reverse vector of the input vector. A reverse vector multiplies all components by -1.

        Parameters
        ----------
        vector : list
            The input vector.

        Returns
        -------
        list
            The normalized vector.
        """
        if not isinstance(vector, list):
            return None
        return [x*-1 for x in vector]
    
    @staticmethod
    def SetMagnitude(vector: list, magnitude: float) -> list:
        """
        Sets the magnitude of the input vector to the input magnitude.

        Parameters
        ----------
        vector : list
            The input vector.
        magnitude : float
            The desired magnitude.

        Returns
        -------
        list
            The created vector.
        """
        return (Vector.Multiply(vector=Vector.Normalize(vector), magnitude=magnitude))
    
    @staticmethod
    def South():
        """
        Returns the vector representing the *south* direction. In Topologic, the negative YAxis direction is considered *south* ([0,-1,0]).

        Returns
        -------
        list
            The vector representing the *south* direction.
        """
        return [0,-1,0]
    
    @staticmethod
    def SouthEast():
        """
        Returns the vector representing the *southeast* direction. In Topologic, the negative YAxis direction is considered *south* and the positive XAxis direction is considered *east*. Therefore *southeast* is ([1,-1,0]).

        Returns
        -------
        list
            The vector representing the *southeast* direction.
        """
        return [1,-1,0]
    
    @staticmethod
    def SouthWest():
        """
        Returns the vector representing the *southwest* direction. In Topologic, the negative YAxis direction is considered *south* and the negative XAxis direction is considered *west*. Therefore *southwest* is ([-1,-1,0]).

        Returns
        -------
        list
            The vector representing the *southwest* direction.
        """
        return [-1,-1,0]
    
    @staticmethod
    def Up():
        """
        Returns the vector representing the up direction. In Topologic, the positive ZAxis direction is considered "up" ([0,0,1]).

        Returns
        -------
        list
            The vector representing the "up" direction.
        """
        return [0,0,1]
    
    @staticmethod
    def West():
        """
        Returns the vector representing the *west* direction. In Topologic, the negative XAxis direction is considered *west* ([-1,0,0]).

        Returns
        -------
        list
            The vector representing the *west* direction.
        """
        return [-1,0,0]
    
    @staticmethod
    def XAxis():
        """
        Returns the vector representing the XAxis ([1,0,0])

        Returns
        -------
        list
            The vector representing the XAxis.
        """
        return [1,0,0]

    @staticmethod
    def YAxis():
        """
        Returns the vector representing the YAxis ([0,1,0])

        Returns
        -------
        list
            The vector representing the YAxis.
        """
        return [0,1,0]
    
    @staticmethod
    def ZAxis():
        """
        Returns the vector representing the ZAxis ([0,0,1])

        Returns
        -------
        list
            The vector representing the ZAxis.
        """
        return [0,0,1]
