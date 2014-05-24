import sys
from PySide import QtCore
import FreeCAD, scipy
import BiotLineIntegral

class ConductorModel(QtCore.QAbstractTableModel):
    """
    Main Object self.ConductorList
    0: start shape
    1: start Vertex
    2: current
    """
    cLength = 0.10
    discretizeLength = 0.01
    def __init__(self, ConductorList=None, parent=None):
        super(ConductorModel, self).__init__(parent)
        if ConductorList is None:
            self.ConductorList = []
        else:
            self.ConductorList = ConductorList

    def rowCount(self, index=QtCore.QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.ConductorList)

    def columnCount(self, index=QtCore.QModelIndex()):
        """ Returns the number of columns the model holds. """
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not 
            returning data, return None (PySide equivalent of QT's 
            "invalid QVariant").
        """
        if not index.isValid():
            return None
        if not 0 <= index.row() < len(self.ConductorList):
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        if index.column() == 0:
            return self.ConductorList[index.row()][0].Label
        if index.column() == 1:
            return self.ConductorList[index.row()][1]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            header = ["Start Vertex", "Current [A]"]
            return header[section]
        return None

    def insertRows(self, position=None, StartVertex=None, Current=None, rows=1, index=QtCore.QModelIndex()):
        """ Insert a row into the model. """
        if position == None:
            position = len(self.ConductorList)
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)

        ConductorElements = self.setConductors(StartVertex.Shape.Point)
        
        for row in range(rows):
            self.ConductorList.insert(position + row, [StartVertex,Current,ConductorElements, None])
        for n in ConductorElements:
            FreeCAD.Console.PrintMessage(n[0].Label + " added;")
            FreeCAD.Console.PrintMessage(n[1])
            FreeCAD.Console.PrintMessage("\n")
        self.endInsertRows()
        return True

    def setConductors(self, startVertex):        
        ### fill list of FC objects compatible with curves
        ConductorElements = []
        unOrderedConductorList = []
        for fcObject in FreeCAD.ActiveDocument.Objects:
            if hasattr(fcObject, "Shape"):
                if hasattr(fcObject.Shape, "Curve"):
                    unOrderedConductorList.append(fcObject)
        while len(unOrderedConductorList) != 0:
            for nexn in unOrderedConductorList:
                conductor = self.__closestConductor(startVertex, unOrderedConductorList)
                if conductor[0] == None :
                    unOrderedConductorList = []
                else:
                    ConductorElements.append(conductor)
                    unOrderedConductorList.remove(conductor[0])
                    startVertex = conductor[0].Shape.Vertexes[not conductor[1]].Point
        self.debug(ConductorElements)
        return ConductorElements

    def __closestConductor(self, startVertex, conductorList):
        """
        find closest conductor to  startVertex
        """
        closestConductor = [None, 0] ### [freecad conductor object, end point vertex]
        for n in conductorList:
            startStop = [n.Shape.Vertexes[0].Point, n.Shape.Vertexes[1].Point] 
            if round(startVertex.sub(startStop[0]).Length,7) < round(startVertex.sub(startStop[1]).Length,7):
                if round(startVertex.sub(startStop[0]).Length,7) < self.cLength:
                    closestConductor = [n, 0]
            else:
                if round(startVertex.sub(startStop[1]).Length,7) < self.cLength:
                    closestConductor = [n, 1]
        return closestConductor
    
    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        del self.ConductorList[position:position+rows]
        self.endRemoveRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """ Adjust the data (set it to <value>) depending on the given 
            index and role. 
        """
        if role != QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.ConductorList):
            self.ConductorList[index.row()][index.column()] = value
            FreeCAD.Console.PrintMessage(self.ConductorList[index.row()][index.column()])
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're 
            implementing this function just to see how it's done, as we 
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.column() == 2:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) |
                            QtCore.Qt.ItemIsEditable)
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) |
                            QtCore.Qt.ItemIsSelectable)

    def calculate(self, r_p=scipy.array([[0.0, 3.0, 5.0]])):
        B = scipy.zeros_like(r_p)
        self.debug(self.ConductorList)
        for conductor in self.ConductorList:
            for subelem in conductor[2]:
                fcObject = subelem[0]
                direction = subelem[1]
                FreeCAD.Console.PrintMessage(fcObject.Name)
                FreeCAD.Console.PrintMessage(" Processing\n")
                if direction == 0:
                    # vect_arr = scipy.asarray(fcObject.Shape.discretize(int(fcObject.Shape.Length/self.discretizeLength)))
                    vect_arr = scipy.asarray(fcObject.Shape.discretize(int(fcObject.Shape.Curve.length()/self.discretizeLength)))
                else:
                    vect_arr = scipy.asarray(fcObject.Shape.discretize(int(fcObject.Shape.Curve.length()/self.discretizeLength))[::-1])
                FreeCAD.Console.PrintMessage("B\n")
                FreeCAD.Console.PrintMessage(B)
                B  += BiotLineIntegral.BiotLineIntegral( vect_arr, r_p )
        self.debug(B)
        return B

    def debug(self, ConductorList):
        FreeCAD.Console.PrintMessage("Calculate\n")
        FreeCAD.Console.PrintMessage(ConductorList)
