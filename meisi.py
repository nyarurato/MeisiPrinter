# -*- coding:utf-8 -*-
import Twitter
import StyleParser
from PIL import Image,ImageDraw,ImageFont
from urllib import urlretrieve
from os import mkdir,path,linesep
from qrcode import QRCode
from urllib2 import urlopen
from sys import stdout
from printer import ThermalPrinter

resource_path = "resource"

#get twitter user info
#return：user info (dict)
def info_get():
    twitter = Twitter.Twitter()
    stdout.write("input Twitter ID :@")
    data = twitter.get_user_info(raw_input())
    return data

#create directory for user
#return：path (str)
def make_user_dir(data):
    if(not path.exists("User")):
        mkdir("User")

    name_dir = path.join("User",data["screen_name"])
    if(not path.exists(name_dir)):
        mkdir(name_dir)
    return name_dir

# making image for print
# return : image path (str)
def make_img_new(user_data,style_path):
    user_dir = make_user_dir(user_data)
    style_parser = StyleParser.Parser(style_path)
    style_list = style_parser.get_list()  
    
    #print(style_list)

    preferences = style_list[0]
    imgs_list = style_list[1]
    strs_list = style_list[2]

    #create canvas
    img = Image.new("1", (int(preferences["width"]),int(preferences["height"])),"white")

    #paste each images
    img = paste_imgs(img,user_data,imgs_list,user_dir)
    
    img = paste_strings(img,user_data,strs_list)
    
    if(int(preferences["rotation"]) != 0):
        rot_img = img.rotate(int(preferences["rotation"]),expand=True)

        if(rot_img.size[0] > 384):
            print("!!!!!Be careful Image width is too large!!!!!")
        
        #making white background canvas
        rotate_canvas = Image.new('RGB', rot_img.size, (255,)*3)
        rotate_canvas.paste(rot_img,(0,0))
        img = rotate_canvas


    final_img_path = path.join(user_dir,"meisi.png")
    img.save(final_img_path,"PNG")

    return final_img_path

def paste_imgs(canvas_img,user_data,img_style_list,user_dir):
    
    #paste each images to canvas
    #if you want to add other images, write elif blocks.
    for elem in img_style_list:
        content = elem["img"]

        #for user icon (twitter)
        if(content["id"] == "user_twitter_icon"):
            icon_url = user_data["profile_image_url"].replace("_normal","")
            ext = path.splitext(icon_url)[1]
            icon_path = path.join(user_dir,"icon" + ext)
            print("get user icon...")
            #Get Twitter Icon
            urlretrieve(icon_url,icon_path)

            icon2_path = path.join(user_dir,"icon2.png")
            orig_icon = Image.open(icon_path).resize( (int(content["width"]), int(content["height"])) ).convert("L")
            dither_icon = orig_icon.convert(mode="1",dither=1)
            dither_icon.save(icon2_path,"PNG")

            canvas_img.paste(dither_icon,(int(content["x"]),int(content["y"])))

        #for qr code (twitter)
        elif(content["id"] == "qr"):
            qr = QRCode(version=1, box_size=6,border=0)
            qr.add_data("http://twitter.com/" + user_data["screen_name"])
            qr.make(fit=True)
            qrimg = qr.make_image().resize( (int(content["width"]), int(content["height"])) )
            qrimg.save(path.join(user_dir,"qr.png"))
            canvas_img.paste(qrimg,(int(content["x"]),int(content["y"])))

        #for small icons (twitter bird)
        elif(content["id"] == "tw_icon"):
            tw_icon_img = Image.open(path.join(resource_path,"twitter.png")).resize( (int(content["width"]), int(content["height"])) )
            canvas_img.paste(tw_icon_img,(int(content["x"]),int(content["y"])))

        #for small icons (web site)
        elif(content["id"] == "web_icon"):
            web_icon_img = Image.open(path.join(resource_path,"web.png")).resize( (int(content["width"]), int(content["height"])) )
            canvas_img.paste(web_icon_img,(int(content["x"]),int(content["y"])))

        #for small icons (location)
        elif(content["id"] == "loca_icon"):
            loca_icon_img = Image.open(path.join(resource_path,"location.png")).resize( (int(content["width"]), int(content["height"])) )
            canvas_img.paste(loca_icon_img,(int(content["x"]),int(content["y"])))
    
    return canvas_img

def paste_strings(canvas_img,user_data,str_style_list):
    draw = ImageDraw.Draw(canvas_img)

    fontpath = path.join(resource_path,"GenShinGothic-P-Light.ttf")
    
    for elem in str_style_list:
        content = elem["string"]
        
        font = ImageFont.truetype(fontpath, int(content["fontsize"]), encoding='unic')

        #paste each strings to canvas
        #if you want to add other words, write elif blocks.

        # overwrite_text is high priority
        if("overwrite_text" in content):
            draw.text((int(content["x"]),int(content["y"])),content["overwrite_text"],font= font)
        
        elif(content["id"] == "name"):
            draw.text((int(content["x"]),int(content["y"])),user_data["name"],font= font)
        
        elif(content["id"] == "screen_name"):
            draw.text((int(content["x"]),int(content["y"])),"@"+user_data["screen_name"],font= font)
        
        elif(content["id"] == "location"):
            draw.text((int(content["x"]),int(content["y"])),user_data["location"],font= font)
        
        elif(content["id"] == "url"):
            if(user_data["url"] != ""):
                web_url = urlopen(user_data["url"]).geturl()

                web_url = txt_boxing(web_url,font, int(content["width"]), int(content["height"]))
                
                draw.text((int(content["x"]),int(content["y"])), web_url, font= font)
            else:
                draw.text((int(content["x"]),int(content["y"])),"No Web Site",font= font)
        
        elif(content["id"] == "description"):
            words = txt_boxing(user_data["description"], font, int(content["width"]),int(content["height"]))
            draw.text((int(content["x"]),int(content["y"])),words,font= font)
        
        else:
            draw.text((int(content["x"]),int(content["y"])),content["overwrite_text"],font= font)

    return canvas_img

def txt_boxing(words,font,width,height):
    linesize = 0
    box = (width,height)
    boxwords = ""
    wordsize = 0
    for word in words:
        wordsize = font.getsize(word)[0]
        if(word == "\n"):
            linesize = 0
            boxwords += word
        elif (linesize + wordsize) >= box[0]:
            linesize = wordsize
            boxwords += "\n" + word
        else:
            linesize += wordsize
            boxwords += word
    return boxwords

#main
def main():
    
    serialport = ThermalPrinter.SERIALPORT
    thprinter = ThermalPrinter(serialport=serialport) 
    
    while(True):
        print(u"\n***Twitter Meisi Print Service***")
        user_data = info_get()
        imgpath = make_img_new(user_data,"style/twitter_meisi.xml")
        #印刷
        
        thprinter.print_img(imgpath)
        thprinter.linefeed()
        thprinter.linefeed()
        thprinter.linefeed()
        

if __name__ == '__main__':
    main()
