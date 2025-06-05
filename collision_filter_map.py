import sys, os
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets, QtWebChannel

class Handler(QtCore.QObject):
    coordinates_received = QtCore.pyqtSignal(list)  # Define the signal here

    @QtCore.pyqtSlot(str)
    def sendCoordinates(self, coords_json):
        import json
        coords = json.loads(coords_json)
        self.coordinates_received.emit(coords)  # Emit the signal

def select_polygon_map():
    os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    view = QtWebEngineWidgets.QWebEngineView()
    handler = Handler()
    coords_container = {}

    def on_coords(coords):
        # # Uncomment to save CSV file of polygon coordinates
        # with open('polygon_coords.csv', 'w', newline='') as f:
        #     import csv
        #     writer = csv.writer(f)
        #     writer.writerow(['Latitude', 'Longitude'])
        #     for point in coords:
        #         writer.writerow([point['lat'], point['lng']])
        coords_container['coords'] = coords
        print("Polygon saved. Close this map when ready.")

    handler.coordinates_received.connect(on_coords)

    channel = QtWebChannel.QWebChannel()
    channel.registerObject('pyHandler', handler)

    view.page().setWebChannel(channel)
    view.load(QtCore.QUrl("http://localhost:8000/map.html"))
    view.show()

    app.exec_()  # Let app keep running; user can close when ready

    return coords_container.get('coords')

if __name__ == '__main__':

    select_polygon_map()
