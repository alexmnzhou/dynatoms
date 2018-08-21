import sys
import os

from PyQt5 import Qt, QtCore
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import math
import numpy as np
import itertools

from DynatomsUtils import csgjoint
from DynatomsUtils import vtkmath
from DynatomsUtils.chemio import open_mol_format

version = '0.1.0'

radf = open('radii.txt') #Used to determine atom size based on element
rads = list(map(str.split, radf))
rads_arr = np.array(list(itertools.zip_longest(*rads, fillvalue=0))).T #Fills in missing data with 0s to preserve dimensionality
rads_ref = dict(zip(rads_arr[:,1],rads_arr[:,2]))

def run():
	app = Qt.QApplication(sys.argv)
	GUI = Window()
	sys.exit(app.exec_())

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

	def __init__(self, renderupdatefunc, parent=None):
		self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
		self.LastPickedActor = None
		self.buttonupdate = renderupdatefunc

	def leftButtonPressEvent(self, obj, event):
		global pickedActor
		global pickedActorIndex

		clickPos = self.GetInteractor().GetEventPosition()
		picker = vtk.vtkPropPicker()
		picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
		self.NewPickedActor = picker.GetActor() # get the new
		if self.NewPickedActor: # If something was selected

    		# Highlight/unhighlight the picked actor by changing its properties
			if self.LastPickedActor == self.NewPickedActor:
				if self.NewPickedActor.GetProperty().GetColor() == (1.0,0.0,0.0):
					self.NewPickedActor.GetProperty().SetColor(1.0,1.0,1.0)
					self.buttonupdate(False)
				else:
					self.NewPickedActor.GetProperty().SetColor(1.0,0.0,0.0)
					pickedActorIndex = int(self.NewPickedActor.GetProperty().GetSpecularPower())
					pickedActor = self.NewPickedActor
					self.buttonupdate(True)
			else:
				self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
				pickedActorIndex = int(self.NewPickedActor.GetProperty().GetSpecularPower())
				pickedActor = self.NewPickedActor
				self.buttonupdate(True)
				if self.LastPickedActor != None: #If NewPickedActor is not the first selection, unhighlight the last selection made
					self.LastPickedActor.GetProperty().SetColor(1.0,1.0,1.0)

            # save the last picked actor
			self.LastPickedActor = self.NewPickedActor
		self.OnLeftButtonDown()
		return

class Window(Qt.QMainWindow):

	def __init__(self):
		super(Window, self).__init__()
		Qt.QApplication.setStyle(Qt.QStyleFactory.create('Fusion'))

#		self.statusBar() #Function on window to add status bar
		mainMenu = self.menuBar() #Top menu bar

		fileMenu = mainMenu.addMenu('&File')
		importtip = 'Accepts most widely used chemical file formats'
		self.importact = Qt.QAction('Import Molecule', self)
		self.build_action(self.importact,importtip,self.open_file,'Ctrl+O')
		fileMenu.addAction(self.importact)
		exporttip = 'Save under a specific filepath'
		self.exportact = Qt.QAction('Export STL', self)
		self.build_action(self.exportact,exporttip,self.save_file,'Ctrl+Shift+S')
		fileMenu.addAction(self.exportact)
		fileMenu.addSeparator()
		quittip = 'Leave the application'
		self.quitact = Qt.QAction('Quit', self)
		self.build_action(self.quitact,quittip,self.close_application,'Ctrl+Q')
		fileMenu.addAction(self.quitact)

		editMenu = mainMenu.addMenu('&Edit')
		addjointtip = 'Place a joint on selected bond'
		self.addjointact = Qt.QAction('Add Joint to Selected', self)
		self.build_action(self.addjointact,addjointtip,self.place_joint,'Ctrl+B')
		self.addjointact.setDisabled(True)
		editMenu.addAction(self.addjointact)
		removejointtip = 'Remove a joint on selected bond'
		self.removejointact = Qt.QAction('Remove Joint from Selected', self)
		self.build_action(self.removejointact,removejointtip,self.remove_joint,'Del')
		editMenu.addAction(self.removejointact)

		viewMenu = mainMenu.addMenu('&View')
		themeMenu = viewMenu.addMenu('&Theme')

		helpMenu = mainMenu.addMenu('Help')
		abouttip = 'Credits and attributions'
		self.aboutact = Qt.QAction('About', self)
		self.build_action(self.aboutact,abouttip,self.about_trigger)
		helpMenu.addAction(self.aboutact)

		self.include_joint = False
		self.SEGMENTS = 12

		self.home()

	def build_action(self, action, tooltip, trigger, shortcut = None):
		action.setStatusTip(tooltip)
		action.triggered.connect(trigger)
		if shortcut != None:
			action.setShortcut(shortcut)

	def home(self):
		self.scaling = 8
		self.bond_scaling = 1
		self.joint_scaling = 1.2
		self.adjust_high_rads = True

		self.setGeometry(50, 50, 1500, 900)
		self.setWindowTitle("Dynatoms")
		self.setWindowIcon(Qt.QIcon('Dynatoms.png'))

		splitter = Qt.QSplitter(QtCore.Qt.Horizontal)

		sidebar = Qt.QVBoxLayout()
		sidebar.setAlignment(QtCore.Qt.AlignTop)
		sidebarwid = Qt.QWidget() #Create widget to add to splitter
		sidebarwid.setLayout(sidebar)

		jointcbox = Qt.QCheckBox('Include Joint', self)
		sidebar.addWidget(jointcbox)
		jointcbox.resize(jointcbox.sizeHint())
		jointcbox.stateChanged.connect(self.jointcbox_toggle)
		jointcbox.toggle() #Default is on

		comboBox = Qt.QComboBox(self)
		comboBox.addItem("T-Spin Joint")
		comboBox.addItem("Ball Joint")
		comboBox.resize(comboBox.sizeHint())
		sidebar.addWidget(comboBox)
		comboBox.activated[str].connect(self.joint_picker)

		self.stlrenderbtn = Qt.QPushButton("Render STL", self)
		self.stlrenderbtn.setEnabled(False)
		self.stlrenderbtn.clicked.connect(self.gen_stl)
		self.stlrenderbtn.resize(self.stlrenderbtn.sizeHint())
		sidebar.addWidget(self.stlrenderbtn)

		jointplacebtn = Qt.QPushButton("Place Joint Here", self)
		jointplacebtn.clicked.connect(self.place_joint)
		jointplacebtn.resize(jointplacebtn.sizeHint())
		sidebar.addWidget(jointplacebtn)

		self.vtkframe = Qt.QFrame()
		self.vtkWidget = QVTKRenderWindowInteractor(self.vtkframe)
		container = Qt.QHBoxLayout()
		container.addWidget(self.vtkWidget)

		self.renderer = vtk.vtkRenderer()
		self.renderer.SetBackground(0.3,0.4,0.5)
		self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
		self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

		self.style = MouseInteractorHighLightActor(self.render_update)
		self.style.SetDefaultRenderer(self.renderer)
		self.vtkWidget.SetInteractorStyle(self.style)

		self.vtkframe.setLayout(container)

		self.setCentralWidget(splitter)
		splitter.addWidget(sidebarwid)
		splitter.addWidget(self.vtkframe)
		self.vtkframe.setLayout(container)

		self.show()
		self.interactor.ReInitialize()

	def render_update(self, selected): #For disabling render options when nothing is selected
		self.stlrenderbtn.setEnabled(selected) #Selected is a boolean
		self.addjointact.setEnabled(selected)

	def joint_picker(self, text):
		joint_choice = text
		print(joint_choice)

	def jointcbox_toggle(self, state):
		if state == QtCore.Qt.Checked:
			print("Checked")
		else:
			print("Not checked")

	def place_joint(self):
		joint, botheight, topheight = csgjoint.csgTSpin(self.scaling*self.bond_scaling*0.42, self.bond_lens[pickedActorIndex], 0.2, self.joint_scaling, self.SEGMENTS)
		self.draw_joint(joint, botheight, topheight)

	def draw_joint(self, joint, botheight, topheight):

		self.renderer.RemoveActor(pickedActor)

		jtransform = vtk.vtkTransform()
		jtransform.PostMultiply() #To perform transforms in correct order (x->y->z->translate)
		jtransform.RotateX(90)
		jtransform.RotateY(self.bond_angs[pickedActorIndex][1])
		jtransform.RotateZ(self.bond_angs[pickedActorIndex][2])
		jtransform.Translate(*self.bond_locs[pickedActorIndex])
		jtransformFilter = vtk.vtkTransformPolyDataFilter()
		jtransformFilter.SetTransform(jtransform)
		jtransformFilter.SetInputData(joint)
		jtransformFilter.Update()

		j_mapper = vtk.vtkPolyDataMapper()
		j_mapper.SetInputConnection(jtransformFilter.GetOutputPort())
		j_actor = vtk.vtkActor()
		j_actor.SetMapper(j_mapper)

		j_actor.GetProperty().SetSpecular(0.1)
		j_actor.GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
		j_actor.GetProperty().SetSpecularPower(pickedActorIndex) #Used as a quasi-indexer

		self.renderer.AddActor(j_actor)
		self.interactor.Initialize()

	def remove_joint(self):
		print("Placeholder 2")

	def gen_stl(self):
	#	self.renderer.RemoveAllViewProps()
	#	self.renderer.Clear()

		self.modelPolyData = vtk.vtkAppendPolyData()
		actors = self.renderer.GetActors()
		actors.InitTraversal()
		for i in range(actors.GetNumberOfItems()):
			actor = actors.GetNextActor()
			self.modelPolyData.AddInputData(actor.GetMapper().GetInput())
		self.modelPolyData.Update()

		stlWriter = vtk.vtkSTLWriter()
		stlWriter.SetFileName("test.stl")
		stlWriter.SetInputConnection(self.modelPolyData.GetOutputPort())
		stlWriter.Write()

	def save_file(self):
		savePath = Qt.QFileDialog.getSaveFileName(self,'Save File', '/')

	def open_file(self):
		openPath = Qt.QFileDialog.getOpenFileName(self,'Open File', '/')
		extension = os.path.splitext(openPath)[1][1:]
		if extension == "mol":
			self.types, rawcoords, self.bonded = open_mol_format(openPath)
		self.coords = rawcoords*self.scaling*1.4
		self.bond_lens = []
		self.bond_angs = []
		self.bond_locs = []
		for i in range(len(self.bonded)):
			pair = self.bonded[i]
			cpair = [self.coords[pair[0]-1],self.coords[pair[1]-1]]
			self.bond_lens.append(np.linalg.norm(cpair[0]-cpair[1]))
			self.bond_angs.append(vtkmath.find_angle(cpair[0],cpair[1]))
			self.bond_locs.append([(cpair[0][0]+cpair[1][0])/2,(cpair[0][1]+cpair[1][1])/2,(cpair[0][2]+cpair[1][2])/2])

		self.renderer.RemoveAllViewProps() #Clear previous file AFTER new data is parsed and confirmed to be renderable
		self.renderer.Clear()

		#Atom actors
		for i in range(len(self.coords)):
			sph = vtk.vtkSphereSource()
			type = ''.join([c for c in str(self.types[i]) if c.isalpha()])  #Removes non-letter parts (e.g. C3 -> C)
			if type in rads_ref:
				if (float(rads_ref[type])<=0.7 or self.adjust_high_rads == False):
					sph.SetRadius(float(rads_ref[type])*self.scaling)
				else:
					#print(type)
					adj_rad = np.tanh((float(rads_ref[type])-0.7))/3 + 0.7 #Above 0.7 rad, further increases are diminished
					sph.SetRadius(adj_rad*self.scaling)
			else: #If atom type not found in size reference
				sph.SetRadius(.5*self.scaling)

			sph.SetCenter(self.coords[i])
			sph.SetPhiResolution(24)
			sph.SetThetaResolution(24)

			sph_mapper = vtk.vtkPolyDataMapper()
			sph_mapper.SetInputConnection(sph.GetOutputPort())
			sph_actor = vtk.vtkActor()
			sph_actor.SetMapper(sph_mapper)

			sph_actor.GetProperty().SetSpecular(0.1)
			sph_actor.GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
			sph_actor.SetPickable(0) #Makes it so only the bonds are pickable

			self.renderer.AddActor(sph_actor)

		#Bond actors
		for i in range(len(self.bonded)):
			cyltransform = vtk.vtkTransform()
			cyltransform.PostMultiply() #To perform transforms in correct order (x->y->z->translate)
			cyltransform.RotateX(90)
			cyltransform.RotateY(self.bond_angs[i][1])
			cyltransform.RotateZ(self.bond_angs[i][2])
			cyltransform.Translate(*self.bond_locs[i])
			cyltransformFilter = vtk.vtkTransformPolyDataFilter()
			cyltransformFilter.SetTransform(cyltransform)

			cyl = vtk.vtkCylinderSource()
			cyl.SetHeight(self.bond_lens[i])
			cyl.SetRadius(self.scaling*self.bond_scaling*0.42)
			cyl.SetResolution(self.SEGMENTS*2)

			cyltransformFilter.SetInputConnection(cyl.GetOutputPort())
			cyltransformFilter.Update()

			cyl_mapper = vtk.vtkPolyDataMapper()
			cyl_mapper.SetInputConnection(cyltransformFilter.GetOutputPort())
			cyl_actor = vtk.vtkActor()
			cyl_actor.SetMapper(cyl_mapper)

			cyl_actor.GetProperty().SetSpecular(0.1)
			cyl_actor.GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
			cyl_actor.GetProperty().SetSpecularPower(i) #Used as a quasi-indexer

			self.renderer.AddActor(cyl_actor)

		self.renderer.ResetCamera()
		self.interactor.Initialize()

	def about_trigger(self):
		print('Placeholder')

	def close_application(self):
		choice = Qt.QMessageBox.question(self, 'Dynatoms', 'Close without saving?', Qt.QMessageBox.Save | Qt.QMessageBox.Discard | Qt.QMessageBox.Cancel)
		if choice == Qt.QMessageBox.Discard:
			sys.exit()
		elif choice  == Qt.QMessageBox.Save:
			self.save_file()
		else:
			pass

run()
