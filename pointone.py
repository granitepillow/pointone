from PIL import Image, ImageDraw
import os
import re

def parse_data(path):
    f = open(path, "r")
    data = []
    l = f.readline()
    keys = l.strip().split(',')
    l = f.readline()
    while l:
        din = {}
        row = l.strip().split(",")
        for i, k in enumerate(keys):
            din[k] = float(row[i])
        data.append(din)
        l = f.readline()
    return keys, data

def enumerate_images(dir):
    l = []
    exp = r"^\d+_(\d+\.\d+)\.png"
    #create [[<filename1>, <imageTime1>], [<filename2>, <imageTime2>], ...]
    for f in os.listdir(dir):
        try:
            l.append([f, float(re.match(exp, f).group(1))])
        except:
            continue
    return l

def linear_interp(y0, y1, t0, t1, tint):
    return (y1-y0)/(t1-t0) * (tint-t0) + y0

def find_data_for_image(image_time, data, key):
    #binary search on ~3000 rows of static data analysis is for overoptimizing silly-willies
    for i, row in enumerate(data):
        if row["imageTime"] > image_time:
            if i == 0:
                i = 1
            break
    i = min(i, len(data) - 1)
    data1 = data[i][key]
    data0 = data[i-1][key]
    t1 = data[i]["imageTime"]
    t0 = data[i-1]["imageTime"]

    return linear_interp(data0, data1, t0, t1, image_time)

def draw_data_to_image(row,idx):
    img = Image.new("RGBA", (200,1000))
    draw = ImageDraw.Draw(img)

    data_str = ""
    for k in row:
        if k =="image_path":
            continue
        data_str += "%s: %s\n" % (k, row[k])
    draw.text((0,0), data_str, (255,255,0))
    draw = ImageDraw.Draw(img)
    mod_path = "over_" + str(idx) +".png"
    img.save(mod_path)
    bg = Image.open(row["image_path"])
    fg = Image.open(mod_path)
    bg.paste(fg, (0,0), fg)
    bg.save(mod_path)

def draw_data_to_images(img_dir_path, data, keys):
    print("Drawing data to images...")
    img_data_map = []
    ignore_keys = ["imageTime", "pctime"]
    os.chdir(img_dir_path)
    for img in imgs:
        entry = {}
        entry["image_path"] = img[0]
        for k in (set(keys) - set(ignore_keys)):
            entry[k] = find_data_for_image(img[1], data, k)
        img_data_map.append(entry)
    for i, r in enumerate(img_data_map):
        draw_data_to_image(r,i)

csv_path = "./saturday_session_2.csv"
img_dir_path = "./saturday_session_2"

keys, data = parse_data(csv_path)
imgs = enumerate_images(img_dir_path)
draw_data_to_images(img_dir_path, data, keys)
