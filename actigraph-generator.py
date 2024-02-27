import numpy as np 
import datetime
import math
from PIL import Image as im, ImageDraw, ImageFont

#plan is to generate data for 763 days.
#That is 763px wide/tall image. make it in 2x scale...
# another aspect of the image should be 24 hours. I want to have plot lines, so let's make this at 8x scale
# so the image is 1526 x 192

# Globals
log_file = "/home/me/sleep_log_2020.txt"
#log_file = "/home/me/sleep_log.txt"
entry_time_fmt = "%d.%m.%Y %H:%M:%S"
time_scale = 10
day_scale = 4   
act_col = 85
day_pixel_offset = 0
padding_date = 90
padding_time = 60


def parse(log):
    log = log.split('\n')
    entries = []

    for entry in log:
        if len(entry) == 0:
            break
        entry = entry.replace("bedtime: ", "bedtime|")
        entry = entry.replace("wakeup: ", "wakeup|")
        entry = entry.split('|')
        #date = entry[-1].split(' ')
        #entry.pop()
        #entry.extend(date)
        entries.append(entry)

    # Manual data validation - case for unexpected mid-day entries.
    #for i in range(2, len(entries)):
    #    if entries[i][1] == entries[i-2][1]:
    #        print(i, entries[i])

    return entries


def make_img(entries):
    bg_col = 255
    width = 24 * time_scale + padding_date
    num_lines = int(len(entries)/2)
    height = num_lines * day_scale + num_lines * day_pixel_offset + padding_time
    return np.full((width, height), bg_col, np.uint8)


def fill_range(day_offset, hour_start, hour_end, image, col):
        day_pix_start = day_offset * day_scale + padding_time
        day_range = slice(day_pix_start, day_pix_start + day_scale)

        time_pix_start = int(hour_start * time_scale) + padding_date
        time_pix_end = int(hour_end * time_scale) + padding_date
        time_range = slice(time_pix_start, time_pix_end)
        x = np.flip(image.T[day_range])
        x.T[time_range] = col


def draw_grid(image, entries):
    width = image.width
    height = image.height
    draw = ImageDraw.Draw(image)
    day_labels_img = im.new('L', (height, width), 255)
    dl_draw = ImageDraw.Draw(day_labels_img)
    font_size = 10
    font = ImageFont.truetype("FreeMono", size=font_size)
    
    day = datetime.datetime.strptime(entries[0][1], entry_time_fmt).date()
    first = False
    for x in range(padding_time - 1, width, day_scale):
        draw.line([x, 0, x, height - padding_date], 0)

        if day.strftime("%a") == "Sun" or first:
            date = day.strftime("%d.%m.%Y")
            dl_draw.text((20, x), date, font=font, align="center")
            first = False
        day += datetime.timedelta(days=1)

    # Copy day labelt to img.
    day_labels_img = day_labels_img.rotate(90, expand=True)
    day_labels_img = day_labels_img.crop((0, height - padding_date, width, height))
    image.paste(day_labels_img, (0, height - padding_date))
    
    hour = 23
    for y in range(time_scale, height - padding_date + 1 , time_scale):
        draw.line([padding_time, y, width, y], 0)

        # Stoopid!
        alignment = 10
        if hour < 10:
            alignment -= font_size / 2
        draw.text((padding_time-font_size - alignment, y-font_size/2), str(hour), font=font, align="left")
        hour = hour - 1


def make_actigraph(entries):
    array = make_img(entries)
    start_day = datetime.datetime.strptime(entries[0][1], entry_time_fmt).date()

    # Mark sunday columns by different color
    for i in range(0, len(entries) - 1, 2):
        entry_start = datetime.datetime.strptime(entries[i][1], entry_time_fmt)
        if entry_start.date().strftime("%a") == "Sun":
            day_offset = (entry_start.date() - start_day).days
            fill_range(day_offset, 0, 24, array, 200)


    for i in range(0, len(entries) - 1, 2):
        entry_start = datetime.datetime.strptime(entries[i][1], entry_time_fmt)
        entry_end = datetime.datetime.strptime(entries[i+1][1], entry_time_fmt)

        day_offset = (entry_start.date() - start_day).days
        start_time = entry_start.time()
        end_time = entry_end.time()
        start_hour = start_time.hour + start_time.minute / 60
        end_hour = end_time.hour + end_time.minute / 60

        if entry_start.day != entry_end.day:
            fill_range(day_offset, start_hour, 24, array, act_col)
            fill_range(day_offset+1, 0, end_hour, array, act_col)
            print(entry_end, end_hour)

        else:
            fill_range(day_offset, start_hour, end_hour, array, act_col)

    image = im.fromarray(array) 
    draw_grid(image, entries)
    return image

################# 

entries = parse(open(log_file, "r").read())
entries_per_graph = math.ceil(len(entries) / 3) # Note, that days = entries_per_graph / 2
pages = math.ceil(len(entries) / entries_per_graph)

for page in range(0, pages):
    start_index = page * entries_per_graph
    entries_page = entries[start_index: start_index + entries_per_graph]
    image = make_actigraph(entries_page)
    image.show()
    #image.save('/home/me/Desktop/act.png')
