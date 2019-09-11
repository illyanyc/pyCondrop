# Py Surface Area Calculator - Illya Nayshevsky
# import dependancies
import wx
import cv2
import methods as m
import os
import ntpath
ntpath.basename("a/b/c")

# init params
global fileToOpen
global fileToUpdate
global coordinates
global zeroes
global g_mean
global g_stdev
global g_min
global g_max

def path_leaf(path):
                head, tail = ntpath.split(path)
                return tail or ntpath.basename(head)

# main class - triggers UI and init methods
class MyForm(wx.Frame):

    # Initialize/build all GUI items
    def __init__(self):
        # Constructor
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="Py Surface Area Coverage", size=(1200, 800))
        self.SetBackgroundColour('gray')
        self.panel = wx.Panel(self, wx.ID_ANY)


        # UI Features
        sizer = wx.GridBagSizer(0, 0)

# Name the sample and save the image
        self.Sample_Name = wx.StaticText(self.panel, -1, "Select a standard sample for 0 percent surface area calculation")
        sizer.Add(self.Sample_Name, pos=(0, 0), flag=wx.ALL, border=5)

        btnSize=((200,-1))
# Load Standard button
        self.LoadStandard_btn = wx.Button(self.panel, id=wx.ID_ANY, label="Load Standard", name="Load Standard", size = btnSize)
        sizer.Add(self.LoadStandard_btn, pos=(1,0), flag=wx.ALL, border=5)

# Load file button
        self.LoadFile_btn = wx.Button(self.panel, id=wx.ID_ANY, label="Load File to Process", name="Load", size = btnSize)
        sizer.Add(self.LoadFile_btn, pos=(2,0), flag=wx.ALL, border=5)

        self.FileToProcess_name = wx.StaticText(self.panel, -1, "---")
        sizer.Add(self.FileToProcess_name, pos=(2, 1), flag=wx.ALL, border=5)

# Set blank image parameters
        img = wx.Image(350, 350)
        self.OriginalImage = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(img))
        sizer.Add(self.OriginalImage, pos=(3, 0), flag=wx.ALL, border=15)

        self.AlteredImage = wx.StaticBitmap(self.panel, wx.ID_ANY,wx.Bitmap(img))
        sizer.Add(self.AlteredImage, pos=(3,1), flag=wx.ALL, border=15)

        self.AlteredImage2 = wx.StaticBitmap(self.panel, wx.ID_ANY,wx.Bitmap(img))
        sizer.Add(self.AlteredImage2, pos=(3, 2), flag=wx.ALL, border=15)

# Iterate directory checkbox
        # IterDir = wx.StaticText(self.panel, -1, "Iterate Directory")
        # sizer.Add(IterDir, pos=(4, 0), flag=wx.ALL, border=5)
        # self.IterDir = wx.CheckBox(self.panel)
        # sizer.Add(self.IterDir, pos=(5,0), flag=wx.ALL, border=5)
        # # self.IterDir.Bind(wx.EVT_CHECKBOX, self.AutoProcessImage)

# Slider
        self.Slider = wx.Slider(self.panel, -1, 27, 0, 255,
                             size=(250, -1),
                             style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.Slider.Bind(wx.EVT_SLIDER, self.Process)
        sizer.Add(self.Slider, pos=(6,0), flag=wx.ALL, border=5)

        self.set_slider = wx.TextCtrl(self.panel, -1, size=(50, -1))
        sizer.Add(self.set_slider, pos=(7, 0), flag=wx.ALL, border=5)

        self.Set_slider_button = wx.Button(self.panel, id=wx.ID_ANY, label="Go", name="Go")
        sizer.Add(self.Set_slider_button, pos=(7, 1), flag=wx.ALL, border=5)

# Save Button
       

        SurfaceCoverage_lbl = wx.StaticText(self.panel, -1, "%SAC Mask Size")
        sizer.Add(SurfaceCoverage_lbl, pos=(8, 0), flag=wx.ALL, border=5)
        self.SurfaceCoverage = wx.StaticText(self.panel, -1, "")
        sizer.Add(self.SurfaceCoverage, pos=(9, 0), flag=wx.ALL, border=5)

        SurfaceCoverage_lbl2 = wx.StaticText(self.panel, -1, "%SAC Gradient Autothresh")
        sizer.Add(SurfaceCoverage_lbl2, pos=(10, 0), flag=wx.ALL, border=5)
        self.SurfaceCoverage2 = wx.StaticText(self.panel, -1, "")
        sizer.Add(self.SurfaceCoverage2, pos=(11, 0), flag=wx.ALL, border=5)

        buttons = [self.LoadFile_btn,self.LoadStandard_btn,self.Set_slider_button]

        for button in buttons:
            self.buildButtons(button, sizer)

        self.panel.SetSizerAndFit(sizer)

    # Display all the buttons in GUI
    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)

    global fileToOpen
    global fileToUpdate

    # Load original images in GUI
    def SetImage(self, filepath):
        frame_size = self.GetSize()
        self.PhotoMaxSize = 400

        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)

        self.OriginalImage.SetBitmap(wx.Bitmap(img))
        self.AlteredImage.SetBitmap(wx.Bitmap(img))
        self.AlteredImage2.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()

    # Process image event handler
    def Process(self, event):
        slider_value = self.Slider.GetValue()
        self.ProcessImage(slider_value)
        # self.AutoProcessImage()

    # Set slider value
    def SetSlider(self):
        value = self.set_slider.GetValue()
        self.ProcessImage(int(value))
        # self.AutoProcessImage()

    # Manually process image with a slider set threshold
    def ProcessImage(self, slider_value):
        image, mask, coverage, occupied = m.binaryImage(fileToOpen, slider_value, zeroes)
        cv2.imwrite(fileToUpdate2, image)
        cv2.imwrite(fileToUpdate, mask)
        self.SurfaceCoverage2.SetLabel(str(coverage) + " %")
        self.SurfaceCoverage.SetLabel(str(occupied) + " %")
        self.UpdateImage()

    # Automatically process image with a cv2 threshold
    # def AutoProcessImage(self, event):
    #     auto_thresh = True
    #     slider_value = self.Slider.GetValue()
    #     image, coverage = m.binaryImage(fileToOpen, slider_value, auto_thresh)
    #     cv2.imwrite(fileToUpdate2, image)
    #     print(coverage)
    #     self.SurfaceCoverage2.SetLabel(str(coverage)+" %")
    #     self.UpdateImage()

    # Update processed image
    def UpdateImage(self):
        frame_size = self.GetSize()
        self.PhotoMaxSize = 400
        img = wx.Image(fileToUpdate, wx.BITMAP_TYPE_ANY)
        img2 = wx.Image(fileToUpdate2, wx.BITMAP_TYPE_ANY)
        orig = wx.Image(fileToOpen, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)
        orig = orig.Scale(NewW, NewH)

        W = img2.GetWidth()
        H = img2.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img2 = img2.Scale(NewW, NewH)
        orig = orig.Scale(NewW, NewH)

        self.AlteredImage.SetBitmap(wx.Bitmap(img))
        #self.OriginalImage.SetBitmap(wx.Bitmap(orig))
        self.AlteredImage2.SetBitmap(wx.Bitmap(img2))
        self.panel.Refresh()

    #Action methods
    def onButton(self, event):

        global coordinates
        global fileToOpen
        global fileToUpdate
        global fileToUpdate2
        global zeroes
        global g_mean
        global g_stdev
        global g_min
        global g_max

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
           openFileDialog.Destroy()
           self.SetImage(fileToOpen)
           self.FileToProcess_name.SetLabel("Analyzing: "+str(path_leaf(fileToOpen)))

           fileToUpdate = "temp.jpg"
           temp_img_save = cv2.imread(fileToOpen)
           cv2.imwrite("temp.jpg", temp_img_save)

           fileToUpdate2 = "temp2.jpg"
           temp_img_save = cv2.imread(fileToOpen)
           cv2.imwrite("temp2.jpg", temp_img_save)
           

           self.SetImage(fileToOpen)
           #_min, _max, _mean, _stdev = m.selectBackground(fileToOpen)
           zeroes = int(g_mean + g_stdev)
           print("Mean: ", g_mean, "Stdev: ", g_stdev)
           self.ProcessImage(int(g_max))

           # filelist = m.IterateDirectory(fileToOpen)


        if buttonPressed == "Load Standard":
            openFileDialog = wx.FileDialog(frame, "Open", "", "",
                                      "Bitmap files (*.*)|*.*",
                                      wx.FD_OPEN)
            openFileDialog.ShowModal()
            standatd_fileToOpen = openFileDialog.GetPath()
            LoadButtonName = "Standard: "+str(path_leaf(standatd_fileToOpen))
            self.LoadStandard_btn.SetLabel(LoadButtonName)
            openFileDialog.Destroy()
            _min, _max, _mean, _stdev = m.selectBackground(standatd_fileToOpen)
            # file_name = str(self.sample_name.GetValue())+".jpg"
            # file_to_save = cv2.imread("temp.jpg")
            # cv2.imwrite(file_name, file_to_save)
            g_min, g_max, g_mean, g_stdev = _min, _max, _mean, _stdev

        if buttonPressed == "Go":
            self.SetSlider()

    key = cv2.waitKey(0)
    #if key in [ord('32')]:
    if key in [ord('p'), ord('P')]:
        cv2.destroyAllWindows()


# run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()