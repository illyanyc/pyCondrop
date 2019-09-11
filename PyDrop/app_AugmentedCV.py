# PyCondrop - Illya Nayshevsky
# import dependancies
import os
import wx
import cv2
import numpy as np
import controller


# init params
global fileToOpen
global coordinates
# scale factor - scales the image to a smaller size for faster processing
subsample_factor = 2

# main class - triggers UI and init methods
class MyForm(wx.Frame):

    def __init__(self):
        # Constructor
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="PyConDrop V0.1", size=(300, 700))
        self.SetBackgroundColour('gray')
        panel = wx.Panel(self, wx.ID_ANY)

        # UI Features
        sizer = wx.BoxSizer(wx.VERTICAL)
        Sample_Name = wx.StaticText(panel, -1, "Enter the name of the sample:")
        self.sample_name = wx.TextCtrl(panel, -1, size=(225, -1))

        LoadFile_lbl = wx.StaticText(panel, -1, "Load the first image in the sequence")
        LoadFile_lbl2 = wx.StaticText(panel, -1, "Press 'p' when done selecting the points")
        LoadFile_btn = wx.Button(panel, id=wx.ID_ANY, label="1. Load", name="load")

        self.coordinates = wx.StaticText(panel, -1, "")
        First_Frame = wx.StaticText(panel, -1, "Enter the first frame number")
        self.first_frame = wx.TextCtrl(panel, -1, size=(225, -1))

        Sample_Width = wx.StaticText(panel, -1, "Enter the width of the sample [mm]:")
        self.sample_width = wx.TextCtrl(panel, -1, size=(225, -1))

        Process_btn = wx.Button(panel, id=wx.ID_ANY, label="2. Process", name="process")

        self.x1_lbl = wx.StaticText(panel, -1, "")
        self.x2_lbl = wx.StaticText(panel, -1, "")
        self.y1_lbl = wx.StaticText(panel, -1, "")
        self.y2_lbl = wx.StaticText(panel, -1, "")

        Make_Video = wx.StaticText(panel, -1, "Remake videos")
        Video_Name = wx.StaticText(panel, -1, "Enter video name:")
        self.video_name = wx.TextCtrl(panel, -1, size=(225, -1))
        Make_Video_btn = wx.Button(panel, id=wx.ID_ANY, label="Make Videos", name="videos")


        buttons = [Sample_Name, self.sample_name, LoadFile_lbl, LoadFile_lbl2,  LoadFile_btn, self.coordinates, First_Frame,
                   self.first_frame, Sample_Width, self.sample_width, Process_btn, self.x1_lbl , self.x2_lbl, self.y1_lbl, self.y2_lbl, Make_Video, Video_Name, self.video_name, Make_Video_btn]

        for button in buttons:
            self.buildButtons(button, sizer)

        panel.SetSizer(sizer)

    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)
        sizer.Add(btn, 0, wx.ALL, 5)

    global fileToOpen

    #button methods
    def onButton(self, event):
        subsample_factor = 2
        global coordinates
        global fileToOpen
        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)

        buttonPressed = button_by_id.GetName()

        # Event handler for Load button
        if buttonPressed == "load":
           openFileDialog = wx.FileDialog(frame, "Open", "", "",
                                      "Bitmap files (*.*)|*.*",
                                      wx.FD_OPEN)
           openFileDialog.ShowModal()

           fileToOpen = openFileDialog.GetPath()
           openFileDialog.Destroy()
           y1, y2, x1, x2 = open_window_to_pick_points()
           coordinates = (float(y1*subsample_factor), float(y2*subsample_factor), float(x1*subsample_factor), float(x2*subsample_factor))

           self.coordinates.SetLabel("x1:"+str(x1)+" ; y1:"+str(y1)+" ; x2:"+str(x2)+" ; y2:"+str(y2))

        # Event handler for Process button
        if buttonPressed == "process":
           # Parameters to pass

            sample_name = self.sample_name.GetValue()
            start_frame = int(self.first_frame.GetValue())
            sample_width = float(self.sample_width.GetValue())

            path = os.path.abspath(os.path.join(fileToOpen, os.pardir))
            print(path)

            controller.processData(sample_name, start_frame, sample_width, coordinates, subsample_factor, path)

        if buttonPressed == "videos":
            # Select first image in the video
            openFileDialog = wx.FileDialog(frame, "Select the first frame of the video", "", "",
                                           "Bitmap files (*.*)|*.*",
                                           wx.FD_OPEN)
            openFileDialog.ShowModal()

            fileToOpen = openFileDialog.GetPath()
            openFileDialog.Destroy()

            # Select the csv file
            openFileDialog = wx.FileDialog(frame, "Select CSV File", "", "",
                                           "Bitmap files (*.*)|*.*",
                                           wx.FD_OPEN)
            openFileDialog.ShowModal()

            CSVfilePath = openFileDialog.GetPath()
            openFileDialog.Destroy()


            path = os.path.abspath(os.path.join(fileToOpen, os.pardir))
            videos.make_video(path, self.video_name.GetValue(), ".mp4", CSVfilePath, path+"/")

# open windows to select the bouds of the image for processing
def open_window_to_pick_points():
    # Declate a list to take coordiantes of plotted points
    coordinate_list = []

    # Global parameter holding the image path
    global fileToOpen

    # mouse callback function
    def draw_circle(event, x, y, flags, param):
        # sert font of test overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x+10, y)
        fontScale = 0.4
        fontColor = (255, 255, 255)
        lineType = 1

        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(img, (x, y), 5, (0, 0 , 255), -1)
            cv2.putText(img, str(x)+", "+str(y), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            coordinate_list.append([x,y])

    # Write the image to the window canvas and initiate the plotting method
    curr_img = cv2.imread(fileToOpen)
    img = cv2.resize(curr_img, None, fx=1 / subsample_factor, fy=1 / subsample_factor)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_circle)

    # Keep running the method until boolean conditions are satisfied
    while (1):
        cv2.imshow('image', img)
        if (cv2.waitKey(20) & 0xFF == 27) or (len(coordinate_list) == 4):
            cv2.imshow('image', img)
            break

    # Sort through the coordianates
    coordinate_dictionary = {}
    x_list = []
    y_list = []
    for i in coordinate_list:
        x_list.append(i[0])
        y_list.append(i[1])

    y1 = np.min(y_list)
    y2 = np.max(y_list)
    x1 = np.min(x_list)
    x2 = np.max(x_list)

    print (y1, y2, x1, x2)

    key = cv2.waitKey(0)
    #if key in [ord('32')]:
    if key in [ord('p'), ord('P')]:
        cv2.destroyAllWindows()

    return y1, y2, x1, x2

# run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()