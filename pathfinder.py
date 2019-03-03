import random
from PIL import ImageColor, Image, ImageDraw

class Map:
    """
    Represents a map
    """
    def __init__(self, file, map_drawer, path_finder, y_coord=0):
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
        self.optimal_path_all = self.path_finder.find_path_all(self.height, self.elevations)
        self.optimal_path_image = self.map_drawer.draw_optimal_path(self.map_image, self.optimal_path)
        self.optimal_path_image_all = self.map_drawer.draw_optimal_path_all(self.map_image, self.optimal_path_all)
        self.best_optimal_path_all = self.path_finder.find_best_path(self.optimal_path_all, self.elevations)
        self.best_optimal_path_image = self.map_drawer.draw_optimal_path(self.optimal_path_image_all, self.best_optimal_path_all)

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
            map_image.putpixel(coordinate, ImageColor.getcolor('lime', 'RGBA')) 
        return map_image

    def draw_optimal_path_all(self, map_image, all_optimal_coordinates):
        """
        Given a 2-D list of optimal coordinates, draw all optimal paths onto an elevation map image
        """
        for line in all_optimal_coordinates:
            for coordinate in line:
                map_image.putpixel(coordinate, ImageColor.getcolor('cyan', 'RGBA')) 
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
                y = height - 2 
            bottom_path = elevations[y+1][x+1]
            
            top_delta = abs(starting_point - top_path)
            middle_delta = abs(starting_point - middle_path)
            bottom_delta = abs(starting_point - bottom_path)
            min_delta = min([top_delta, middle_delta, bottom_delta])
            if top_delta == min_delta and top_delta == bottom_delta and top_delta != middle_delta:
                if random.randint(0, 1) == 0:
                    y -= 1
                else:
                    y += 1
            elif top_delta == min_delta and top_delta != middle_delta:
                y -= 1 
            elif bottom_delta == min_delta and bottom_delta != middle_delta:
                y += 1
            x += 1    
            optimal_path.append((x, y))
        return optimal_path

    def find_best_path(self, all_paths, elevations_list):
        """
        Given a list of all possible paths and list of elevations, 
        return the path with the least total elevation change
        """
        # create list of [path/elevation pairs:[coordinates[(x, y),..], elevations[<ints>,..]],..]
        path_elevation_list = []
        for path in all_paths:
            elevations = []
            for coord in path:
                elevations.append(elevations_list[coord[1]][coord[0]])
            path_elevation_list.append([path, elevations])
        
        # create list of [path/elevation-change pairs: [coordinates[(x,y),..], elevation-changes[<ints>,..],..],..]
        path_elev_diffs = []
        for item in path_elevation_list:
            elevation_difference = []
            for elevation in range(len(item[1])-1):
                elevation_difference.append(abs(item[1][elevation] - item[1][elevation + 1]))
            path_elev_diffs.append([item[0], elevation_difference])

        # create list of [[paths:[coordinates[(x,y),..], <total elevation change>],..]
        path_elev_change_sums = []
        for item in path_elev_diffs:
            total_change = 0
            for diff in range(len(item[1])):
                total_change += item[1][diff]
            path_elev_change_sums.append([item[0], total_change])

        # determine the path with the lowest total elevation change
        min_elev_change = path_elev_change_sums[0][1]
        path_least_elevation_change = []
        for item in range(len(path_elev_change_sums)):
            if path_elev_change_sums[item][1] < min_elev_change:
                min_elev_change = path_elev_change_sums[item][1]
                path_least_elevation_change = path_elev_change_sums[item][0] 

        return path_least_elevation_change
    
    def find_path_all(self, height, elevations):
        """
        Given a map height and 2-D list of elevations,
        return a list of all possible paths of least resistance from west to east
        """
        optimal_path_all = []
        for i in range(height):
            optimal_path_all.append(self.find_path(i, elevations))
        return optimal_path_all


if __name__ == "__main__":
    map_info = MapDrawer()
    optimal_path_info = PathFinder()
    optimal_path_map_all = Map("elevation_small.txt", map_info, optimal_path_info)
    best_optimal_path_image = optimal_path_map_all.best_optimal_path_image
    best_optimal_path_image.save('best_optimal_path_image_test.png')





    #### Normal Mode ####
    # optimal_path_map = Map("elevation_small.txt", map_info, optimal_path_info, 0)
    # optimal_path_image = optimal_path_map.optimal_path_image
    # optimal_path_image.save('optimal_path_map_test.png')

    ### optimal path test ####
    # map_info2 = MapDrawer()
    # optimal_path_info2 = PathFinder()
    # optimal_path_map2 = Map("elevation_small.txt", map_info, optimal_path_info, 299)
    # optimal_path_image2 = optimal_path_map.optimal_path_image
    # print(optimal_path_map.optimal_path == optimal_path_map2.optimal_path)
    #     # ran multiple times and returned both True and False
