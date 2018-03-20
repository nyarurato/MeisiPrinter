# -*- coding:utf-8 -*-
import xml.etree.ElementTree as ET

class Parser:
    """
     this class parse style xml files.
     xml -> dict in list

     * all arguments and text is string. not int. you need to convert it yourself.

     like this xml
     
     <?xml version="1.0"?>
     <style>
         <width>635</width>
         <height>384</height>
         <img id="user_twitter_icon" 
           width="128" 
           height="128" 
           x="15"
           y="15"
           rotation="0"/>
         <string id="description"
           x="150"
           y="230"
           width="570"
           height="300"
           rotation="0">
         </string>
     </style>

     to [{"width":635,"height":384},
         [{'img': {'width': '25', 'y': '70', 'x': '170', 'rotation': '0', 'id': 'tw_icon', 'height': '25'}}],
         [{'string': {'y': '60','x': '200', 'rotation': '0', 'id': 'name'}}]]
    
    it means
        [{preferencesd(dict)}, [img tags(dict in list)], [string tags(dict in list)]]

    """


    def create_style_list(self,style_path):
        #reading style file
        style_tree = ET.parse(style_path)
        root = style_tree.getroot()
        
        #checking root tag is style
        if(root.tag == "style"):
            self.root = root
        else:
            raise ValueError("no style tag in stylesheet xml file")

        #style xml -> dict in list
        self.style_list = []
        preferences = {}
        imgs = []
        strs = []

        for elem in self.root:
            #img tag
            if(elem.tag == "img"):
                img_dict = {elem.tag : elem.attrib}
                imgs.append(img_dict)
            #string tag
            elif(elem.tag == "string"):
                overwrite_text = elem.text
                attributes = elem.attrib
                #checking blank
                if(overwrite_text.strip() != ""):
                    attributes.update({"overwrite_text":overwrite_text.strip()})
                str_dict = {elem.tag : attributes}
                strs.append(str_dict)
            #other tag (pick up only text)
            else:
                tmp_dict={elem.tag : elem.text}
                preferences.update(tmp_dict)

        self.style_list.append(preferences)
        self.style_list.append(imgs)
        self.style_list.append(strs)

    def get_list(self):
        return self.style_list

    def __init__(self,style_path):
        self.create_style_list(style_path)
