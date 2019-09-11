import videos_manual as vid
import wx
import cv2
import os

# main class - triggers UI and init methods
class MyForm(wx.Frame):

    # Initialize/build all GUI items
    def __init__(self):
        # Constructor
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="Py Drop Jump Count", size=(200, 200))
        self.SetBackgroundColour('gray')
        self.panel = wx.Panel(self, wx.ID_ANY)


        # UI Features
        sizer = wx.GridBagSizer(0, 0)

# Name the sample and save the image
        Sample_Name = wx.StaticText(self.panel, -1, "1. Sample Name")
        sizer.Add(Sample_Name, pos=(0, 0), flag=wx.ALL, border=5)
        self.sample_name = wx.TextCtrl(self.panel, -1, size=(225, -1))
        sizer.Add(self.sample_name, pos=(1, 0), flag=wx.ALL, border=5)

# Load file button
        LoadFile_btn = wx.Button(self.panel, id=wx.ID_ANY, label="2. Load", name="Load")
        sizer.Add(LoadFile_btn, pos=(2,0), flag=wx.ALL, border=5)


        buttons = [LoadFile_btn]

        for button in buttons:
            self.buildButtons(button, sizer)

        self.panel.SetSizerAndFit(sizer)

    # Display all the buttons in GUI
    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)

    #Action methods
    def onButton(self, event):

        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)

        buttonPressed = button_by_id.GetName()

        # Event handler for Load button
        if buttonPressed == "Load":
           openFileDialog = wx.FileDialog(frame, "Open", "", "",
                                      "Bitmap files (*.*)|*.*",
                                      wx.FD_OPEN)
           openFileDialog.ShowModal()

           fileToOpen = openFileDialog.GetPath()
           fileName = str(self.sample_name.GetValue())
           path, name = os.path.split(fileToOpen)
           path = path+"/"

           vid.CountDrops(fileToOpen, path, fileName, path)

           openFileDialog.Destroy()

    key = cv2.waitKey(0)
    #if key in [ord('32')]:
    if key in [ord('q'), ord('Q')]:
        cv2.destroyAllWindows()


# run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()