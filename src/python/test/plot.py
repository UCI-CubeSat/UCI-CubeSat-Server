import random
import urllib

import matplotlib
from matplotlib import pyplot, animation
from matplotlib.animation import FuncAnimation
from skyfield.toposlib import wgs84
import numpy

from src.python.service import skyfieldService, tleService

matplotlib.use("TkAgg")

IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/8/83/Equirectangular_projection_SW.jpg"
IRVINE = wgs84.latlon(33.643831, -117.841132, elevation_m=17)
DURATION = 2.0 * 3600
RESOLUTION = 1


def getColor():
    red = random.random()
    blue = random.random()
    grey = random.random()
    return red, grey, blue


def getAllSat():
    satellites = []
    response = tleService.readTwoLineElement()
    for k in response.keys():
        satellites.append(
            skyfieldService.getPath(
                response[k],
                "latLng",
                DURATION,
                RESOLUTION))
    return satellites


def plotPath() -> FuncAnimation:
    data = getAllSat()
    fig, ax = pyplot.subplots(figsize=(15, 7.5))
    img = pyplot.imread(urllib.request.urlopen(IMAGE_URL), format='jpg')

    def setup():
        ax.set_xlim([-180, 180])
        ax.set_ylim([-90, 90])
        ax.imshow(img, origin='upper', extent=[-180, 180, -90, 90], alpha=0.75)
        ax.annotate(
            f'. {"Irvine, CA"}',
            (-117.841132,
             33.643831),
            color='black')
        ax.annotate(f'. {"Plano, TX"}', (-96.697442, 32.999553), color='black')
        ax.annotate(f'. {"Dalian, China"}', (121.6147, 38.9140), color='black')
        ax.set(xlabel='longitude', ylabel='latitude', title='NAME')

    def init():
        setup()
        ax.set(
            xlabel='longitude',
            ylabel='latitude',
            title=data[0]["identifier"])
        lng = data[0]["lngArray"]
        lat = data[0]["latArray"]
        currPath = ax.plot(
            lng,
            lat,
            'black',
            label='ground track',
            linewidth=2)
        ax.legend(loc='lower right')
        return currPath,

    def update(frame):
        ax.cla()
        # gc.collect()
        setup()
        ax.set(xlabel='longitude', ylabel='latitude',
               title=data[frame + 1]["identifier"])
        lng = data[frame + 1]["lngArray"]
        lat = data[frame + 1]["latArray"]
        currPath = ax.plot(
            lng,
            lat,
            'black',
            label='ground track',
            linewidth=2)
        ax.legend(loc='lower right')
        return currPath,

    return animation.FuncAnimation(fig, update, frames=len(data) - 1,
                                   init_func=init, interval=1000)


def plotRealTime():
    satelliteToPlot = getAllSat()[0]

    # plot movement of first satellite
    fig = pyplot.figure()
    ax = fig.add_subplot()
    img = pyplot.imread(urllib.request.urlopen(IMAGE_URL), format='jpg')

    x = satelliteToPlot["lngArray"]
    y = satelliteToPlot["latArray"]

    # create the first plot
    point, = ax.plot([x[0]], [y[0]], 'ro')
    ax.legend()
    ax.set_xlim([-180, 180])
    ax.set_ylim([-90, 90])
    ax.imshow(img, origin='upper', extent=[-180, 180, -90, 90], alpha=0.75)
    ax.annotate(f'. {"Irvine, CA"}', (-117.841132, 33.643831), color='black')
    # ax.annotate(f'. {"Plano, TX"}', (-96.697442, 32.999553), color='black')
    ax.annotate(f'. {"Dalian, China"}', (121.6147, 38.9140), color='black')
    ax.annotate(f'. {"Sydney, AUS"}', (151.2093, -33.8688), color='black')
    ax.set(xlabel='longitude', ylabel='latitude',
           title=satelliteToPlot["identifier"])

    # move the point position at every frame
    def update_point(n, x, y, point):
        point.set_data(numpy.array([x[n], y[n]]))
        return point

    return animation.FuncAnimation(fig, update_point, 99, fargs=(x, y, point))


if __name__ == "__main__":
    # flight path of every available satellite
    _ = plotPath()

    pyplot.show()

    # for every available satellite, an animation of its flight path
    _ = plotRealTime()

    pyplot.show()
