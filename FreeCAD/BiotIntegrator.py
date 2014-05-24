import sys
sys.path.append('/home/marmei/umri/python/FreeCAD/')
sys.path.append('/home/marmei/umri/python/FieldModeling/')
from PySide import QtGui, QtCore
import Plot, FreeCADGui, FreeCAD, scipy
import ConductorModel, FieldContourPlot, pylab
reload(ConductorModel)
reload(FieldContourPlot)

class BiotMain(QtGui.QDockWidget):
    doubleValidator = QtGui.QDoubleValidator()
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.resize(250,250)        
        self.setObjectName("Biot Savart Calculator")
        self.setWindowTitle("Biot Savart Calculator")
        FreeCADGui.ActiveDocument.ActiveView.setAxisCross(True)
        self.mainTabWidget = QtGui.QTabWidget()
        self.conductorTab()
        self.setupTab()
        self.setWidget(self.mainTabWidget)

    def setupTab(self):
        widSetupTab = QtGui.QWidget()
        layoutSetupTab = QtGui.QVBoxLayout()
        widSetupTab.setLayout(layoutSetupTab)
        
        layoutSetupTab.addWidget(self.groupBoxXY())
        layoutSetupTab.addStretch(1)
        self.mainTabWidget.addTab(widSetupTab, "Setup")

    def groupBoxXY(self):
        groupBoxXY = QtGui.QGroupBox("Field-Plot XY-Plane")
        groupBoxXY.setCheckable(True)
        xScaleLabelXY = QtGui.QLabel("x Scale:")
        self.xScaleMinLineEdit = QtGui.QLineEdit("-1.0")
        self.xScaleMinLineEdit.setValidator(self.doubleValidator)
        self.xScaleMaxLineEdit = QtGui.QLineEdit("1.0")
        self.xScaleMaxLineEdit.setValidator(self.doubleValidator)
        yScaleLabelXY = QtGui.QLabel("y Scale:")
        self.yScaleMinLineEdit = QtGui.QLineEdit("1.0")
        self.yScaleMinLineEdit.setValidator(self.doubleValidator)
        self.yScaleMaxLineEdit = QtGui.QLineEdit("1.0")
        self.yScaleMaxLineEdit.setValidator(self.doubleValidator)
        zOffsetLabelXY = QtGui.QLabel("z Offset:")
        self.zOffsetLineEdit = QtGui.QLineEdit("0.5")
        self.zOffsetLineEdit.setValidator(self.doubleValidator)

        gridXY = QtGui.QGridLayout()
        gridXY.addWidget(xScaleLabelXY, 0, 0)
        gridXY.addWidget(self.xScaleMinLineEdit, 0, 1)
        gridXY.addWidget(self.xScaleMaxLineEdit, 0, 2)
        gridXY.addWidget(yScaleLabelXY, 1, 0)
        gridXY.addWidget(self.yScaleMinLineEdit, 1, 1)
        gridXY.addWidget(self.yScaleMaxLineEdit, 1, 2)
        gridXY.addWidget(zOffsetLabelXY, 2, 0)
        gridXY.addWidget(self.zOffsetLineEdit, 2, 1)
        
        groupBoxXY.setLayout(gridXY)

        return groupBoxXY

    def conductorTab(self):
        wid1 = QtGui.QWidget() ## base widget for embedding the VBoxLayout
        layout = QtGui.QVBoxLayout()
        wid1.setLayout(layout)
        self.mainTabWidget.addTab(wid1, "Conductors")
        
        # list of conductors
        addVertices = QtGui.QPushButton("Add Vetices")
        delVertices = QtGui.QPushButton("Clear Vetices")
        listadd = QtGui.QIcon.fromTheme("list-add") 
        listdel = QtGui.QIcon.fromTheme("edit-delete") 
        addVertices.setIcon(listadd)
        delVertices.setIcon(listdel)
        buttonlayout = QtGui.QHBoxLayout()
        buttonlayout.addWidget(addVertices)
        buttonlayout.addWidget(delVertices)
        layout.addLayout(buttonlayout)
        addVertices.clicked.connect(self.addVertices)
        delVertices.clicked.connect(self.delVertices)

        self.verticeslist = QtGui.QTableView()
        self.verticeslist.setMaximumHeight(200)
        self._tm = ConductorModel.ConductorModel()
        self.verticeslist.setModel(self._tm)
        layout.addWidget(self.verticeslist)
        FreeCAD.Console.PrintMessage(self._tm.rowCount())
        FreeCAD.Console.PrintMessage("\n")
        self.conductorSelectionModel = QtGui.QItemSelectionModel(self._tm)
        self.verticeslist.setSelectionModel(self.conductorSelectionModel)
        
        # conductor table
        tabBar = QtGui.QTabWidget()
        conductorTable = QtGui.QTableView()
        tabBar.addTab(conductorTable, "Elements")
        layout.addWidget(tabBar)

        ## conductorTable.setModel(self.model)
        # self.conductorList = ConductorList()
        # self.conductorList.setModel(self.model)
        
        # add calculate button
        calculate = QtGui.QPushButton("Calculate") 
        layout.addWidget(calculate)
        calculate.clicked.connect(self.calcBField)

    def calcBField(self):
    #     reload(ConductorModel)
    #     self._tm.calculate()  ## BiotSavartCalculate(self._tm.ConductorList[0][2])
    # def PlotBfieldXY(self):
        reload(FieldContourPlot)
        reload(ConductorModel)
        roi=scipy.array([[-1.0,-1.0,-1.0],[1.0,1.0,1.0]])
        # FieldContourPlot.FieldContourPlot(conductorModel=self._tm, roi=roi)
        fig = pylab.figure()
        subfig_grad_z = fig.add_subplot(111)
        FieldContourPlot.CContourPlot( ax=subfig_grad_z,
                      conductorModel =self._tm,
                      axisX="x",
                      axisY="y",
                      axisconst="z",
                      axisV="z",
                      figure=fig,
                      posaxis_const=1.0,
                      roi=roi,
                      cbarLabel=r"$\frac{B_z}{I_x} \, \left[ \frac{T}{A} \right]$")
        pylab.show()
        
    def delVertices(self):
        selections = self.selectionModel
        FreeCAD.Console.PrintMessage(selections.currentIndex().row()) ## isSelected((0,2))
        # while ( self._tm.rowCount() ):
        #     self._tm.removeRows(0)
        
    def addVertices(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) == 0:
            QtGui.QMessageBox.information(None,"BiotSavart Line Integrator", "Nothing Selected")
        else:
            row = 0
            for n in sel:
                self._tm.insertRows(position=1,
                                    StartVertex=n,
                                    Current=10)
                row += 1
        
if __name__ == '__main__':
    m = FreeCADGui.getMainWindow()
    w = m.findChild(QtGui.QDockWidget,"Biot Savart Calculator")
    # if w:
    #     if w.isVisible():
    #         w.hide()
    #     else:
    #         w.show()
    # else:
    m.addDockWidget(QtCore.Qt.RightDockWidgetArea,BiotMain())
