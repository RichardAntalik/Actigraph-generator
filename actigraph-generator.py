import PIL.ImageColor
import numpy as np 
import datetime
import math
from PIL import Image as im, ImageDraw, ImageFont, ImageColor as imCol

# Globals
log_file = "/home/me/sleep_log.txt"
entry_time_fmt = "%d.%m.%Y %H:%M:%S"
time_scale = 10
day_scale = 4
activity_color = [85, 85, 85]
padding_date = 90
padding_time = 60
special_grid_color=(70, 120, 0)
special_text_color=(0, 200, 0)

def parse(log):
    log = log.split('\n')
    entries = []

    for entry in log:
        if len(entry) == 0:
            break
        entry = entry.replace("bedtime: ", "bedtime|")
        entry = entry.replace("wakeup: ", "wakeup|")
        entry = entry.replace(" #", "|")
        entry = entry.replace("#", "|")
        entry = entry.split('|')
        date = datetime.datetime.strptime(entry[1], entry_time_fmt)
        entries.append([entry[0], date])
        
    # Manual data validation - case for unexpected mid-day entries.
    #for i in range(2, len(entries)):
    #    if entries[i][1] == entries[i-2][1]:
    #        print(i, entries[i])

    return entries


def make_img(entries):
    bg_col = [255, 255, 255]
    width = 24 * time_scale + padding_date
    start_date = entries[0][1]
    end_date = entries[len(entries)-1][1]
    num_lines = (end_date - start_date).days + 1
    height = num_lines * day_scale + padding_time
    return np.full((width, height, 3), bg_col, np.uint8)


def fill_range(day_offset, hour_start, hour_end, image, col):
    day_pix_start = day_offset * day_scale + padding_time
    day_range = slice(day_pix_start, day_pix_start + day_scale)

    time_pix_start = int(hour_start * time_scale) + padding_date
    time_pix_end = int(hour_end * time_scale) + padding_date
    time_range = slice(time_pix_start, time_pix_end)

    img_rot = np.rot90(np.flip(image))
    day_column = img_rot[day_range]
    np.rot90(day_column, k=-1)[time_range] = col


def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def draw_grid(image, entries):
    width = image.width
    height = image.height
    draw = ImageDraw.Draw(image)
    day_labels_img = im.new('RGB', (height, width), imCol.getrgb("#FFFFFF"))
    dl_draw = ImageDraw.Draw(day_labels_img, mode='RGB')
    font_size = 10
    font = ImageFont.truetype("FreeMono", size=font_size)
    
    day = entries[0][1].date()
    first = False
    for x in range(padding_time - 1, width, day_scale):
        draw.line([x, 0, x, height - padding_date], 0)

        if day.strftime("%a") == "Sun" or first:
            date = day.strftime("%d.%m.%Y")
            dl_draw.text((20, x), date, font=font, align="center", fill=0)
            first = False
        day += datetime.timedelta(days=1)

    # Copy day labelt to img.
    day_labels_img = day_labels_img.rotate(90, expand=True)
    day_labels_img = day_labels_img.crop((0, height - padding_date, width, height))
    image.paste(day_labels_img, (0, height - padding_date))
    
    for hour in range(0, 24):
        y = int(remap(hour, 0, 23, height - padding_date , time_scale))

        if hour % 4 == 0:
            grid_color = special_grid_color
            text_color = special_text_color
        else:
            grid_color = (0,0,0)
            text_color = (0,0,0)

        draw.line([padding_time, y, width, y], fill=grid_color)

        # Stoopid!
        alignment = 10
        if hour < 10:
            alignment -= font_size / 2

        draw.text((padding_time-font_size - alignment, y-font_size/2), str(hour), font=font, align="left", fill=text_color)
        hour = hour - 1


def make_actigraph(entries):
    array = make_img(entries)
    start_day = entries[0][1].date()

    # Mark sunday columns by different color
    for i in range(0, len(entries), 2):
        entry_start = entries[i][1]
        if entry_start.date().strftime("%a") == "Sun":
            day_offset = (entry_start.date() - start_day).days
            fill_range(day_offset, 0, 24, array, [200, 200, 200])


    for i in range(0, len(entries) - 1, 2):
        entry_start = entries[i][1]
        entry_end = entries[i+1][1]

        day_offset = (entry_start.date() - start_day).days
        start_time = entry_start.time()
        end_time = entry_end.time()
        start_hour = start_time.hour + start_time.minute / 60
        end_hour = end_time.hour + end_time.minute / 60

        if entry_start.day != entry_end.day:
            fill_range(day_offset, start_hour, 24, array, activity_color)
            fill_range(day_offset+1, 0, end_hour, array, activity_color)

        else:
            fill_range(day_offset, start_hour, end_hour, array, activity_color)

    image = im.fromarray(array) 
    draw_grid(image, entries)
    return image

################# 

entries = parse(open(log_file, "r").read())
entries.append(["bedtime: ", datetime.datetime.now()]) # Needed to show current day.
entries_per_graph = math.ceil(len(entries)) # Note, that days = entries_per_graph / 2.
pages = math.ceil(len(entries) / entries_per_graph)

for page in range(0, pages):
    start_index = page * entries_per_graph
    entries_page = entries[start_index: start_index + entries_per_graph]
    image = make_actigraph(entries_page)

    image.show()
    image.save('cur.png')
