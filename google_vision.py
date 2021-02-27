# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:22:38 2019

@authors: Gaurav Kumar Das, Monica.Sam
Starter code: https://medium.com/searce/tips-tricks-for-using-google-vision-api-for-text-detection-2d6d1e0c6361
"""
import io
import os
from PIL import Image,ImageDraw
from enum import Enum
from google.cloud import vision
from google.cloud.vision import types
import pdb
import cv2


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="My Project-ac34607d0b08.json"

client = vision.ImageAnnotatorClient()
response = ""
document = ""

        
'''Plotting bounding boxes from the response.'''
class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5
    
    
            
def draw_boxes(image, bounds, color,width=5):

    draw = ImageDraw.Draw(image)
    for bound in bounds:
        draw.line([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y,
            bound.vertices[0].x, bound.vertices[0].y],fill=color, width=width)
     
    return image

def get_document_bounds(document, response, feature):

    bounds=[]
    for i,page in enumerate(document.pages):
        for block in page.blocks:
            if feature==FeatureType.BLOCK:
                bounds.append(block.bounding_box)
            for paragraph in block.paragraphs:
                if feature==FeatureType.PARA:
                    bounds.append(paragraph.bounding_box)
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)
                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)
    return bounds

def get_bounding_boxes(image_file):
    
      
    #print(response)
    #print(document)
        
    bounds = get_document_bounds(document, response, FeatureType.WORD)
    #bounds_img = draw_boxes(Image.open(image_file), bounds, 'yellow')
    
    
    #FOR BLOCKS
    bounds = get_document_bounds(document, response, FeatureType.BLOCK)
    bounds_block_img = draw_boxes(Image.open(image_file), bounds, 'red')

    
    return bounds_block_img


def detect_text(image_file):

    with io.open(image_file,'rb') as image_file1:
        content = image_file1.read()
        
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    txt = response.full_text_annotation.text
    
    return txt


def get_complete_text(image_file, x2, y2):
    
    global document, response 
        
    with io.open(image_file, 'rb') as image_file1:
        content = image_file1.read()
    
    content_image = types.Image(content=content)

    response = client.document_text_detection(image=content_image)
#    response = client.text_detection(
#        image=content_image,
#        image_context={"language_hints": ["en-handwrit"]},  
#    )

    document = response.full_text_annotation
    #print(document)
    
    #print(get_text_within(image_file, 0, 0, x2, y2))
    #print(response)
    text = get_text_within( 0, 0, x2, y2)
    
    return text



def get_text_within(x1,y1,x2,y2):    

    text=""
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                
                for word in paragraph.words:
                    
                    for symbol in word.symbols:
                        #print(symbol)
                        min_x=min(symbol.bounding_box.vertices[0].x,symbol.bounding_box.vertices[1].x,symbol.bounding_box.vertices[2].x,symbol.bounding_box.vertices[3].x)
                        max_x=max(symbol.bounding_box.vertices[0].x,symbol.bounding_box.vertices[1].x,symbol.bounding_box.vertices[2].x,symbol.bounding_box.vertices[3].x)
                        min_y=min(symbol.bounding_box.vertices[0].y,symbol.bounding_box.vertices[1].y,symbol.bounding_box.vertices[2].y,symbol.bounding_box.vertices[3].y)
                        max_y=max(symbol.bounding_box.vertices[0].y,symbol.bounding_box.vertices[1].y,symbol.bounding_box.vertices[2].y,symbol.bounding_box.vertices[3].y)
                        if(min_x >= x1 and max_x <= x2 and min_y >= y1 and max_y <= y2):
                            text+=symbol.text
                        if(symbol.property.detected_break.type==1 or symbol.property.detected_break.type==3):
                            text+=' '
                        if(symbol.property.detected_break.type==2):
                            text+='\t'
                        if(symbol.property.detected_break.type==5):
                            text+='\n'
    if(x1 < 0 or x2 < 0 or y1 < 0 or y2 < 0):
        text = ""
    
    return text

def assemble_word(word):
    assembled_word=""
    for symbol in word.symbols:
        assembled_word+=symbol.text
    return assembled_word

def find_word_location(word_to_find):   

    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    assembled_word=assemble_word(word)
                    if(assembled_word==word_to_find):
                        return word.bounding_box
                    
def find_incomplete_word_location(text):
    loc = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                if(text[0] != "$"):
                    for i in range(len(paragraph.words)-1):
                        two_words = ""
                        for letter in paragraph.words[i].symbols:
                            two_words += letter.text
                        two_words += " "
                        for letter in paragraph.words[i+1].symbols:
                            two_words += letter.text   
                       
                        #print("two_words: {}".format(two_words))
                        
                        if(two_words.find(text) != -1):
                            index_1 = assemble_word(paragraph.words[i]).find(text[0])
                            index_2 = assemble_word(paragraph.words[i+1]).find(text[len(text)-1])
                            loc = [paragraph.words[i].symbols[index_1].bounding_box.vertices[0].x,
                                   paragraph.words[i].symbols[index_1].bounding_box.vertices[0].y,
                                   paragraph.words[i+1].symbols[index_2].bounding_box.vertices[2].x,
                                   paragraph.words[i+1].symbols[index_1].bounding_box.vertices[2].y]
                            return loc
                else:
                    if(paragraph.words[0].symbols[0].text == "$"):
                        found_word = ""
                        for word in paragraph.words[0:4]:
                            for symbol in word.symbols:
                                found_word += symbol.text
                            
                        #print(found_word)
                        if(found_word == text):
                            loc = [paragraph.bounding_box.vertices[0].x,
                               paragraph.bounding_box.vertices[0].y,
                               paragraph.bounding_box.vertices[2].x,
                               paragraph.bounding_box.vertices[2].y]
                            return loc
                    
    return loc

def assemble_paragraph_words(paragraph, index1, index2):
    assembled_word=""
    for i in range(index1, index2):
        assembled_word+=assemble_word(paragraph.words[i])
        assembled_word+=" "
    return assembled_word

def find_word_in_paragraph(paragraph, text):
    found_word = ""
    loc = []
    
    for word in paragraph.words:
        for symbol in word.symbols:
            found_word += symbol.text
            #print(found_word)
            if(found_word == text[0]):
                #print(found_word)
                loc.append(symbol.bounding_box.vertices[0].x)
                loc.append(symbol.bounding_box.vertices[0].y)
            elif(text.find(found_word) < 0 or (len(found_word) == 1 and found_word != text[0])):
                found_word = ""
                loc = []
            elif(found_word == text):
                #print(found_word)
                loc.append(symbol.bounding_box.vertices[2].x)
                loc.append(symbol.bounding_box.vertices[2].y)
                #print(loc)
                return loc
        

def find_all_incomplete_word_location(text):
    #print("Trying to find: {}".format(text))
    #pdb.set_trace()
    locs = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                if(paragraph.words[0].symbols[0].text == "$"):
                    found_word = ""
                    for word in paragraph.words[0:4]:
                        for symbol in word.symbols:
                            found_word += symbol.text
                        
                    #print("Found word: {}".format(found_word))
                    if(found_word == text):
#                            print("text: {}".format(text))
#                            print("Found word: {}".format(found_word))
                        loc = [paragraph.words[0].bounding_box.vertices[0].x,
                           paragraph.words[0].bounding_box.vertices[0].y,
                           paragraph.words[3].bounding_box.vertices[2].x,
                           paragraph.words[3].bounding_box.vertices[2].y]
                        locs.append(loc)
                else:
                    all_words = assemble_all_words_paragraph(paragraph)
                    if(text in all_words):
                        ind = all_words.find(text)
                        chr_width = paragraph.bounding_box.vertices[2].x - paragraph.bounding_box.vertices[0].x
                        chr_width /= len(all_words)
                        loc = [paragraph.bounding_box.vertices[0].x + ind*int(chr_width),
                               paragraph.bounding_box.vertices[0].y,
                               paragraph.bounding_box.vertices[0].x + (ind + len(text))*int(chr_width),
                               paragraph.bounding_box.vertices[2].y]
                        
                        locs.append(loc)
                            
              
    return locs        
                    
def find_all_word_locations(word_to_find):
    
    boxes = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    assembled_word=assemble_word(word)
                    if(assembled_word==word_to_find):
                        loc = [word.bounding_box.vertices[0].x,
                               word.bounding_box.vertices[0].y,
                               word.bounding_box.vertices[2].x,
                               word.bounding_box.vertices[2].y]
                        boxes.append(loc) 
                        
    return boxes
   
def find_two_words(text):

    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for i in range(len(paragraph.words) - 1):
                    assembled_word = assemble_word(paragraph.words[i])
                   
                    if (text.split(" ")[0] == assembled_word):
                        second_word = assemble_word(paragraph.words[i+1])
                        if(second_word == text.split(" ")[1]):
                            loc = [paragraph.words[i].bounding_box.vertices[0].x,
                                   paragraph.words[i].bounding_box.vertices[0].y,
                                   paragraph.words[i].bounding_box.vertices[2].x,
                                   paragraph.words[i].bounding_box.vertices[2].y]
                            return(loc)
 
def assemble_all_words_paragraph(paragraph):

    paragraph_text = ""
    for word in paragraph.words:
        for symbol in word.symbols:
            paragraph_text+= symbol.text
    return paragraph_text
                           
def search_paragraph_words(text):
    locs = []
    
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                p_words = assemble_all_words_paragraph(paragraph) 
                #print(p_words)
                
                if(p_words == text):
                    loc = find_word_in_paragraph(paragraph, text)
                    locs.append(loc)
                
                elif(p_words.find(text) > 0):
                    #print("Found: {}".format(p_words))
                    #print(find_word_in_paragraph(paragraph, text))
                    loc = find_word_in_paragraph(paragraph, text)
                    #print("Found {} at {}".format(text, loc))
                    locs.append(loc) 
                    
    return locs
      

def search_paragraph_disconnected_words(text):
    locs = []
    
    t_words = text.split(" ")
    print("t_words: {}".format(t_words))
    
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                p_words = assemble_all_words_paragraph(paragraph) 
                print(p_words)
                
                if(all(c in p_words for c in t_words)):
                    
                    loc_0 = find_word_in_paragraph(paragraph, t_words[0])
                    loc_1 = find_word_in_paragraph(paragraph, t_words[len(t_words)-1])
                    print("{} found in paragraph at locs: {}, {}".format(text, loc_0, loc_1))
                    loc = [loc_0[0],loc_1[2],loc_0[1],loc_1[3]]
                    locs.append(loc)
                   
    return locs   

def search_block_words(block, text):
    found_word = ""
    locs = []
    p_cnt = 0
    w_cnt = 0
    s_cnt = 0
    for paragraph in block.paragraphs: 
        p_cnt+= 1
        w_cnt = 0
        s_cnt = 0
        for word in paragraph.words:
            s_cnt = 0
            w_cnt += 1
            for symbol in word.symbols:
                s_cnt += 1
                found_word += symbol.text
                #print(found_word)
                if(found_word == text[0]):
                    loc = []
                    loc.append(symbol.bounding_box.vertices[0].x)
                    loc.append(symbol.bounding_box.vertices[0].y)
                    start_p_cnt = p_cnt
                    start_w_cnt = w_cnt
                    start_s_cnt = s_cnt
                elif(text.find(found_word) < 0 or (len(found_word) == 1 and found_word != text[0])):
                    found_word = ""
                    loc = []
                    start_p_cnt = -1
                    start_w_cnt = -1
                    start_s_cnt = -1
                elif(found_word == text):
                    #print(found_word)
                    loc.append(symbol.bounding_box.vertices[2].x)
                    loc.append(symbol.bounding_box.vertices[2].y)
                    #print(loc)
                    locs.append(loc)
    return locs

def search_all_blocks_word(text):
    all_locs = []
    
    for page in document.pages:
        for block in page.blocks:
            all_locs.extend(search_block_words(block, text))
            
    return all_locs


def blockwiseTextExract(image_file):

    img = cv2.imread(image_file)
    text_Gv = get_complete_text(image_file,img.shape[1], img.shape[0])
    #print(output_Gv)

    blockText_Gv = text_Gv.split('\n')
    #print(blockText_Gv) # same like block wise text extraction !!
    return text_Gv, blockText_Gv


fileName = r'sample_1.png'
img = cv2.imread(fileName)
print(get_complete_text(fileName, img.shape[0], img.shape[1]))
