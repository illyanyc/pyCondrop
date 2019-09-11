
import videos_manual as vid
import wx
import cv2
import os
global fileToOpen


# main class - triggers UI and init methods
class MyForm(wx.Frame):

    # Initialize/build all GUI items
    def __init__(self):
        # Constructor
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="Py Video to Frames", size=(500, 400))
        self.SetBackgroundColour('gray')
        self.panel = wx.Panel(self, wx.ID_ANY)


        # UI Features
        sizer = wx.GridBagSizer(0, 0)

# Name the sample and save the image
        Sample_Name = wx.StaticText(self.panel, -1, "1. Sample Name")
        sizer.Add(Sample_Name, pos=(0, 0), flag=wx.ALL, border=5)
        self.sample_name = wx.TextCtrl(self.panel, -1, size=(225, -1))
        sizer.Add(self.sample_name, pos=(0, 1), flag=wx.ALL, border=5)

        Frame_Count = wx.StaticText(self.panel, -1, "Frame Count")
        sizer.Add(Frame_Count, pos=(2, 0), flag=wx.ALL, border=5)
        self.frame_count_lbl = wx.StaticText(self.panel, -1, "")
        sizer.Add(self.frame_count_lbl, pos=(2, 1), flag=wx.ALL, border=5)

        First_Frame = wx.StaticText(self.panel, -1, "First Frame")
        sizer.Add(First_Frame, pos=(3, 0), flag=wx.ALL, border=5)
        self.first_frame_txt = wx.TextCtrl(self.panel, -1, size=(225, -1))
        sizer.Add(self.first_frame_txt, pos=(3, 1), flag=wx.ALL, border=5)

        Last_Frame = wx.StaticText(self.panel, -1, "Last Frame")
        sizer.Add(Last_Frame, pos=(4, 0), flag=wx.ALL, border=5)
        self.last_frame_txt = wx.TextCtrl(self.panel, -1, size=(225, -1))
        sizer.Add(self.last_frame_txt, pos=(4, 1), flag=wx.ALL, border=5)



# Load file button
        LoadFile_btn = wx.Button(self.panel, id=wx.ID_ANY, label="2. Load", name="Load")
        sizer.Add(LoadFile_btn, pos=(1,0), flag=wx.ALL, border=5)

        Go_btn = wx.Button(self.panel, id=wx.ID_ANY, label="3. Process", name="Go")
        sizer.Add(Go_btn, pos=(5, 0), flag=wx.ALL, border=5)


        buttons = [LoadFile_btn, Go_btn]

        for button in buttons:
            self.buildButtons(button, sizer)

        self.panel.SetSizerAndFit(sizer)

    # Display all the buttons in GUI
    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)




    #Action methods
    def onButton(self, event):
        global fileToOpen

        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)

        buttonPressed = button_by_id.GetName()

        # Event handler for Load button
        if buttonPressed == "Load":
           openFileDialog = wx.FileDialog(frame, "Open", "", "",
                                      "MPEG files (*.mp4)|*.mp4",
                                      wx.FD_OPEN)
           openFileDialog.ShowModal()

           fileToOpen = openFileDialog.GetPath()
           fileName = str(self.sample_name.GetValue())
           path, name = os.path.split(fileToOpen)
           frame_count, fps = vid.CheckFrames(path+"/", name)
           self.frame_count_lbl.SetLabel(str(frame_count)+"; "+str(fps))

           openFileDialog.Destroy()

        if buttonPressed == "Go":
           path, name = os.path.split(fileToOpen)
           first_frame = str(self.first_frame_txt.GetValue())
           last_frame = str(self.last_frame_txt.GetValue())
           vid.VideoToFrames(path+"/", name, first_frame, last_frame)


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


# region
# # main class - triggers UI and init methods
# class MyForm(wx.Frame):
#
#     # Initialize/build all GUI items
#     def __init__(self):
#         # Constructor
#         wx.Frame.__init__(self, None, id=wx.ID_ANY, title="Py Drop Jump Count", size=(200, 200))
#         self.SetBackgroundColour('gray')
#         self.panel = wx.Panel(self, wx.ID_ANY)
#
#
#         # UI Features
#         sizer = wx.GridBagSizer(0, 0)
#
# # Set time interval and video length
#         Sample_Name = wx.StaticText(self.panel, -1, "1. Time Interval")
#         sizer.Add(Sample_Name, pos=(0, 0), flag=wx.ALL, border=5)
#         self.sample_name = wx.TextCtrl(self.panel, -1, size=(225, -1))
#         sizer.Add(self.sample_name, pos=(1, 0), flag=wx.ALL, border=5)
#
#         Sample_Name = wx.StaticText(self.panel, -1, "1. Time Interval")
#         sizer.Add(Sample_Name, pos=(0, 0), flag=wx.ALL, border=5)
#         self.sample_name = wx.TextCtrl(self.panel, -1, size=(225, -1))
#         sizer.Add(self.sample_name, pos=(1, 0), flag=wx.ALL, border=5)
#
# # Load file button
#         LoadFile_btn = wx.Button(self.panel, id=wx.ID_ANY, label="2. Start Timelapse", name="Start")
#         sizer.Add(LoadFile_btn, pos=(2,0), flag=wx.ALL, border=5)
#
#
#         buttons = [LoadFile_btn]
#
#         for button in buttons:
#             self.buildButtons(button, sizer)
#
#         self.panel.SetSizerAndFit(sizer)
#
#     # Display all the buttons in GUI
#     def buildButtons(self, btn, sizer):
#         btn.Bind(wx.EVT_BUTTON, self.onButton)
#
#     #Action methods
#     def onButton(self, event):
#
#         button_id = event.GetId()
#         button_by_id = self.FindWindowById(button_id)
#
#         buttonPressed = button_by_id.GetName()
#
#         # Event handler for Load button
#         if buttonPressed == "Load":
#            openFileDialog = wx.FileDialog(frame, "Open", "", "",
#                                       "Bitmap files (*.*)|*.*",
#                                       wx.FD_OPEN)
#            openFileDialog.ShowModal()
#
#            fileToOpen = openFileDialog.GetPath()
#            fileName = str(self.sample_name.GetValue())
#            path, name = os.path.split(fileToOpen)
#            path = path+"/"
#
#            vid.timelapse_video(path, name, interval, length_sec)
#
#            openFileDialog.Destroy()
#
#     key = cv2.waitKey(0)
#     #if key in [ord('32')]:
#     if key in [ord('q'), ord('Q')]:
#         cv2.destroyAllWindows()
#
#
# # run the program
# if __name__ == "__main__":
#     app = wx.App(False)
#     frame = MyForm()
#     frame.Show()
#     app.MainLoop()
# endregion