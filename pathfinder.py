from PIL import ImageColor, Image, ImageDraw

class Map:
    """
    Represents a map
    """
    def __init__(self, file, map_drawer, path_finder, y_coord):
        """
        Parameters:
        - file -- elevation data file to be read in
        - map_drawer -- represents MapDrawer object
        - path_finder -- represents PathFinder object
        - y_coord -- represents starting y coordinate for optimal path
        """
        self.file = file
        self.map_drawer = map_drawer
        self.path_finder = path_finder
        self.y_coord = y_coord
        self.elevations = self.convert_to_list()
        self.intensities = self.map_drawer.convert_to_intensity(self.elevations)
        self.width = len(self.intensities[0])
        self.height = len(self.intensities)
        self.map_image = self.map_drawer.draw_map(self.width, self.height, self.intensities)
        self.optimal_path = self.path_finder.find_path(self.y_coord, self.elevations)
        self.optimal_path_image = self.map_drawer.draw_optimal_path(self.map_image, self.optimal_path)

    def convert_to_list(self):
        """
        Given a text file, return a list of elevations
        """
        elevations = []
        with open(self.file) as file:
            for line in file:
                elevations.append([int(e) for e in line.split(" ")])
        return elevations

class MapDrawer:
    """
    Represents a map drawer.
    """
    def __init__(self):
        """
        Parameters:
        """

    def convert_to_intensity(self, elevations):
        """
        Convert a 2-D list of elevations into rgba values proportional to 255
        """
        max_elevation = max([max(e) for e in elevations])
        min_elevation = min([min(e) for e in elevations])

        intensities = [[int((elevations[y][x] - min_elevation) / (max_elevation - min_elevation) * 255) for x in range(len(elevations[y]))] for y in range(len(elevations))]

        return intensities

    def draw_map(self, width, height, intensities):
        """
        Draw an elevation map using elevations at each (x, y) coordinate
        """
        base_img = Image.new('RGBA', (width, height))
                # 'Image.new(set color mode, size(width, height), background-color)' function creates new image
        for y in range(len(intensities)):
            for x in range(len(intensities)):
                rgba_value = intensities[y][x]
                base_img.putpixel((x, y), (rgba_value, rgba_value, rgba_value))
                    # '.putpixel((x,y), RGBA())' method changes the color at each pixel located at (x, y)   
        return base_img    

    def draw_optimal_path(self, map_image, optimal_coordinates):
        """
        Given a list of optimal coordinates, draw a line displaying the optimal path onto an elevation map image
        """
        for coordinate in optimal_coordinates:
            map_image.putpixel(coordinate, ImageColor.getcolor('green', 'RGBA')) 

        return map_image

    
class PathFinder:
    """
    Represents a path finder that finds the path of least resistance
    """
    def __init__(self):
        """
        Parameters:
        """

    def find_path(self, y, elevations):
        """
        Given a starting y coordinate and 2-D list of elevations,
        return the path of least resistance from west to east
        """
        width = len(elevations[0])
        height = len(elevations)
        optimal_path = [(0, y)]
        x = 0
        while x < width - 1:
            # breakpoint()
            starting_point = elevations[y][x]
            if y - 1 < 0:
                y = 1
            top_path = elevations[y-1][x+1]
            middle_path = elevations[y][x+1]
            if y + 1 >= height:
                y = height - 1 
            bottom_path = elevations[y+1][x+1]
            
            top_delta = abs(starting_point - top_path)
            middle_delta = abs(starting_point - middle_path)
            bottom_delta = abs(starting_point - bottom_path)
            min_delta = min([top_delta, middle_delta, bottom_delta])
            if top_delta == min_delta and top_delta != middle_delta:
                y -= 1 
            elif bottom_delta == min_delta and bottom_delta != middle_delta:
                y += 1
            x += 1    
            optimal_path.append((x, y))
        return optimal_path

if __name__ == "__main__":
    map_info = MapDrawer()
    optimal_path_info = PathFinder()
    optimal_path_map = Map("elevation_small.txt", map_info, optimal_path_info, 299)
    optimal_path_image = optimal_path_map.optimal_path_image

    optimal_path_image.save('optimal_path_map_test.png')
