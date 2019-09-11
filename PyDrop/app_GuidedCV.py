import videos_manual as vid
import database as db
import data_dict

Dict = data_dict.pass_Dict("DropJumpingPublicationData")

def countDrops(val):
    temp = val
    name = Dict[temp][0]
    csv_dir = Dict[temp][1]
    dir = Dict[temp][1]+name+".mp4"
    vid.CountDrops(dir,csv_dir,name,Dict[temp][1])

def makeVideo_byDict(keys): # make video from a dictionary
    for i in keys:
        for k, v in Dict.items():
            if k == i:
                dir = v[1]
                dir_image =v[1]
                dir_csv = ""
                video_name = v[0]
                fpm = 1
                #make_video_with_caption(dir,video_name, ".mp4", dir_csv, dir_image)
                vid.MakeVideo(dir,video_name, ".mp4", dir_csv, dir_image, fpm, True)

def make_Video(val, set_bounds, fpm, angle): # make video from one file
    v = Dict[val]                
    dir = v[1]
    dir_image = v[1]
    dir_csv = ""
    video_name = v[0]
    # make_video_with_caption(dir,video_name, ".mp4", dir_csv, dir_image)
    vid.MakeVideo(dir, video_name, ".mp4", dir_csv, dir_image, fpm, set_bounds, angle)

def makeVideo_withCaption_byDict(keys): # make video from a dictionary
    for i in keys:
        for k, v in Dict.items():
            if k == i:
                dir = v[1]+"Refined Images/"
                dir_image =v[1]+"Refined Images/"
                dir_csv = v[1]+v[0]+".csv"
                video_name = v[0]+"_PlottedSlideOffs_"
                fpm = 0.5
                location_ofTags = v[2]
                vid.MakeVideo_withCaption(dir,video_name, ".mp4", dir_csv, dir_image, location_ofTags)

def makeVideo_withCaption():
    v = "/Users/illyanayshevskyy/Dropbox/3-Ph.D. Research/0.Hybrid Surfaces/Abrasive Method(restored)/180505-HS2mm4mm3row-T3/Timeline Images/"
    dir = v + "Refined Images/"
    dir_image = v + "Refined Images/"
    dir_csv = v + "180505-HS2mm4mm3row-T3.csv"
    video_name = "PlottedSlideOffs"
    fpm = 1
    location_ofTags = [(560,500)]
    vid.MakeVideo_withCaption(dir, video_name, ".mp4", dir_csv, dir_image, location_ofTags)

keys = [
    # "170CA-5dT",
    # "170CA-15dT",
    # "170CA-24dT",
    # "170CA-26dT",
    # "170CA-5dT",
    # "170CA-7dT",
    # "170CA-9dT",
    # "170CA-11dT",
    # "170CA-20dT"

    # "179CA-5dT",
    # "179CA-11dT",
    # "179CA-14dT",
    # "179CA-19dT",
    # "179CA-26dT",
    # "179CA-31dT",
    # "179CA-38dT",
    # "179CA-46dT",
    # "179CA-49dT",
    # "179CA-56dT",
    # "179CA-64dT",
    # "179CA-66dT",
    # "179CA-69dT"

    # "180CA-5dT",
    # "180CA-10dT",
    # "180CA-15dT",
    # "180CA-18dT",
    "180CA-26dT",
    # "180CA-31dT",
    "180CA-39dT",
    # "180CA-45dT",
    # "180CA-52dT",
    # "180CA-54dT",
    # "180CA-68dT",
    # "180CA-73dT"

]


countDrops("179CA-38dT")