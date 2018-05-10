from PIL import Image
import random
import numpy


class ClusterObject(object):

    def __init__(self):
        self.pixels = []
        self.centroid = None

    def addPoint(self, pixel):
        self.pixels.append(pixel)

    def setNewCentroid(self):
        R = [colour[0] for colour in self.pixels]
        G = [colour[1] for colour in self.pixels]
        B = [colour[2] for colour in self.pixels]
        print('R: ', len(R))
        try:
            G = sum(G) / len(G)
            B = sum(B) / len(B)
            R = sum(R) / len(R)
        except:
            G = 0
            R = 0
            B = 0
        self.centroid = (R, G, B)
        self.pixels = []

        return self.centroid


class Kmeans(object):

    def __init__(self, k=3, min_distance=2.0, size=1000):
        self.k = k
        self.min_distance = min_distance
        self.size = (size, size)

    def run(self, image):
        self.image = image
        self.image.thumbnail(self.size)
        self.pixels = numpy.array(image.getdata(), dtype=numpy.uint8)
        self.clusters = [None for i in range(self.k)]
        self.oldClusters = None

        randomPixels = random.sample(list(self.pixels), self.k)
        for idx in range(self.k):
            self.clusters[idx] = ClusterObject()
            self.clusters[idx].centroid = randomPixels[idx]

        iterations = 0

        while self.shouldExit(iterations) is False:
            print('Old')

            self.oldClusters = [cluster.centroid for cluster in self.clusters]
            print (self.oldClusters)
            print (iterations)

            for pixel in self.pixels:
                self.assignClusters(pixel)

            for cluster in self.clusters:
                cluster.setNewCentroid()

            iterations += 1
        # self.plot_image()

        color_centroid = [None, None, None]
        for channel in range(3):
            pixels_c = self.image.getdata(band=channel)
            values = []
            for pixel in pixels_c:
                values.append(pixel)
            color_centroid[channel] = sum (values)/len(values)

        #return [cluster.centroid for cluster in self.clusters]
        print ([cluster.centroid for cluster in self.clusters])
        return tuple(color_centroid)

    def assignClusters(self, pixel):
        shortest = float('Inf')
        for cluster in self.clusters:
            distance = self.calcDistance(cluster.centroid, pixel)
            if distance < shortest:
                shortest = distance
                nearest = cluster

        nearest.addPoint(pixel)

    def calcDistance(self, a, b):

        result = numpy.sqrt(sum((a - b) ** 2))
        return result

    def shouldExit(self, iterations):

        if self.oldClusters is None:
            return False

        for i in range(self.k):
            dist = self.calcDistance(
                numpy.array(self.clusters[i].centroid),
                numpy.array(self.oldClusters[i])
            )
            if dist < self.min_distance:
                return True

        return True


    def plot_image(self):
        from matplotlib import pyplot
        from mpl_toolkits.mplot3d import Axes3D
        import random


        fig = pyplot.figure()
        ax = Axes3D(fig)

        sequence_containing_x_vals = list(range(0, 100))
        sequence_containing_y_vals = list(range(0, 100))
        sequence_containing_z_vals = list(range(0, 100))
        x_val = []
        y_val = []
        z_val = []
        color_set = []
        size_set = []
        marker_set = []
        for cluster in self.clusters:
            print(cluster.centroid)
            x_val.append(cluster.centroid[0])
            y_val.append(cluster.centroid[1])
            z_val.append(cluster.centroid[2])
            color_set.append([cluster.centroid[0]/255.0, cluster.centroid[1]/255.0, cluster.centroid[2]/255.0])
            size_set.append(1000)
            marker_set.append('^')
        #ax.scatter(x_val, y_val, z_val, c=color_set, marker='^',s=[100,200,300])

        for pixel in self.pixels:
            x_val.append(pixel[0])
            y_val.append(pixel[1])
            z_val.append(pixel[2])
            #print (pixel)
            color_set.append([pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0])
            print()
            size_set.append(30)
            marker_set.append('.')

        ax.scatter(x_val, y_val, z_val, c=color_set,s=size_set, marker='^')

        pyplot.show()
