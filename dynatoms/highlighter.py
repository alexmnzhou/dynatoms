import vtk

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

	def __init__(self, pickupdatefunc, parent=None):
		self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
		self.LastPickedActor = None
		self.pickedupdate = pickupdatefunc #Only enable the add joint options if something is actually selected and send the picked actor data to the main window class

	def leftButtonPressEvent(self, obj, event):

		clickPos = self.GetInteractor().GetEventPosition()
		picker = vtk.vtkPropPicker()
		picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
		self.NewPickedActor = picker.GetActor() # Get the new Actor
		if self.NewPickedActor: # If something was selected

    		# Highlight/unhighlight the picked actor by changing its properties
			if self.LastPickedActor == self.NewPickedActor:
				if self.NewPickedActor.GetProperty().GetColor() == (1.0,0.0,0.0):
					self.NewPickedActor.GetProperty().SetColor(1.0,1.0,1.0)
					self.pickedupdate(False, self.NewPickedActor,
                                      int(self.NewPickedActor.GetProperty().GetSpecularPower()))
				else:
					self.NewPickedActor.GetProperty().SetColor(1.0,0.0,0.0)
					self.pickedupdate(True, self.NewPickedActor,
                                      int(self.NewPickedActor.GetProperty().GetSpecularPower()))
			else:
				self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
				self.pickedupdate(True, self.NewPickedActor,
                                  int(self.NewPickedActor.GetProperty().GetSpecularPower()))
				if self.LastPickedActor != None: #If NewPickedActor is not the first selection, unhighlight the last selection made
					self.LastPickedActor.GetProperty().SetColor(1.0,1.0,1.0)

            # save the last picked actor
			self.LastPickedActor = self.NewPickedActor
		self.OnLeftButtonDown()
		return
