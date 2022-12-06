# ###########################
# ###  GROUP MEMBERS  ###
# # 19i_2199 Syed Abu Bakr
# # 19i_0545 Ahmed Ali
# # 19i_2194 Faiez Malik
# ###########################

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import imread, imshow
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk

def getpoints(c):
  peri = cv2.arcLength(c,True)
  return cv2.approxPolyDP(c,0.02*peri,True)

def rectangle_Counter(c):
  rectCont=[]
  for i in c:
    area= cv2.contourArea(i)
    if area>50:
      approx = getpoints(i)
      #print(len(approx))
      if(len(approx)==4):
        rectCont.append(i)
  rectCont = sorted(rectCont,key=cv2.contourArea,reverse=True)
  return rectCont

def reorder(p):
  p = p.reshape((4,2))
  arranged = np.zeros((4,1,2),np.int32) # aeeay of arranged points
  add= p.sum(1)
  arranged[0] = p[np.argmin(add)] #top left point [0,0]
  arranged[3] = p[np.argmax(add)] #bottom right point [w,h]

  diff=np.diff(p,axis=1)
  arranged[1] = p[np.argmin(diff)] #top right point [w,0]
  arranged[2] = p[np.argmax(diff)] #bottom left point [0,h]
  return arranged

def preprocessing(img):
  grayscale= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 
  blur = cv2.GaussianBlur(grayscale,(5,5),1)
  canny = cv2.Canny(blur,10,50) 
  """# Contours"""
  contour, hierarchy = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  imgC = img.copy()
  imgContour = cv2.drawContours(imgC,contour,-1,(0,255,0),2)

  """# Finding Rectangle Contours of all the MCQ's"""
  rectCont = rectangle_Counter(contour)
  pane1 = getpoints(rectCont[0])
  pane2 = getpoints(rectCont[1])
  #print(pane1)

  imgPanes=img.copy()
  if pane1.size != 0 and pane2.size != 0:
      cv2.drawContours(imgPanes,pane1,-1,(0,255,0),20)
      cv2.drawContours(imgPanes,pane2,-1,(0,255,255),20)
      pane1 = reorder(pane1)
      pane2 = reorder(pane2)
    
      x=img.shape[1]
      y=img.shape[0]
      pt1 = np.float32(pane1)
      pt2 = np.float32([[0,0],[x,0],[0,y],[x,y]])
      imgWarp = cv2.warpPerspective(img,cv2.getPerspectiveTransform(pt1,pt2),(x,y))

      pt11 = np.float32(pane2)
      pt22 = np.float32([[0,0],[x,0],[0,y],[x,y]])
      imgWarp2 = cv2.warpPerspective(img,cv2.getPerspectiveTransform(pt11,pt22),(x,y))
  """# Applying threshold on the MCQ Panes to obtain a  binary image"""
  if len(imgWarp.shape)==3: 
    imgWarp = cv2.cvtColor(imgWarp, cv2.COLOR_BGR2GRAY)
  if len(imgWarp2.shape)==3: 
    imgWarp2 = cv2.cvtColor(imgWarp2, cv2.COLOR_BGR2GRAY)
  threshold_pane1= cv2.adaptiveThreshold(imgWarp,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,127,2)
  threshold_pane2= cv2.adaptiveThreshold(imgWarp2,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,127,2)

  return threshold_pane1,threshold_pane2
"""# Detecting choices of the user by counting black pixels in a single checkbox for **PANE 1**"""

##########################################
# 1st arg is the img
# 2nd arg is the number of rows to be split in the img
# 3rd arg is the threshold of black pixels that determines a valid choice
##########################################
def detectchoice(binary_img,split,pthres): 
  cols = np.hsplit(binary_img,5)

  #cropping the vertical black error lines at the start and end 
  cols[0] = cols[0][:,10:]
  cols[4] = cols[4][:,:178]

  #addition is the number of pixels that are incremented in each iteration
  addition = int(binary_img.shape[0]/split)
  boxs = []
  for c in cols:
    row_increment = 0
    for i in range(split):
      #horizontally splitting to get each choice
      box= c[row_increment:row_increment+addition,:]
      row_increment= row_increment+addition
      boxs.append(box)

  choices = []
  for i in range(1,split):
    choice = ""
    #boxA
    pixels = boxs[i].shape[0] * boxs[i].shape[1]
    white = cv2.countNonZero(boxs[i])
    black = pixels - white
    if (black >= pthres):
      choice = "a"
    #boxB
    pixels = boxs[i+split].shape[0] * boxs[i+split].shape[1]
    white = cv2.countNonZero(boxs[i+split])
    black = pixels - white
    if (black >= pthres):
      if(choice != ""):
        choices.append("M")#Multiple Selections
        continue
      choice = "b"
    #boxC
    pixels = boxs[i+(2*split)].shape[0] * boxs[i+(2*split)].shape[1]
    white = cv2.countNonZero(boxs[i+(2*split)])
    black = pixels - white
    if (black >= pthres):
      if(choice != ""):
        choices.append("M")#Multiple Selections
        continue
      choice = "c"
    #boxD
    pixels = boxs[i+(3*split)].shape[0] * boxs[i+(3*split)].shape[1]
    white = cv2.countNonZero(boxs[i+(3*split)])
    black = pixels - white
    if (black >= pthres):
      if(choice != ""):
        choices.append("M")#Multiple Selections
        continue
      choice = "d"
    #boxE
    pixels = boxs[i+(4*split)].shape[0] * boxs[i+(4*split)].shape[1]
    white = cv2.countNonZero(boxs[i+(4*split)])
    black = pixels - white
    if (black >= pthres):
      if(choice != ""):
        choices.append("M")#Multiple Selections
        continue
      choice = "e"
    choices.append(choice)
  return choices

def upload_file1():
    filename = tk.filedialog.askopenfilename(multiple=False)
    img=Image.open(filename) # read the image file
    global filename1
    filename1=filename
    img=img.resize((150,200)) # new width & height
    img=ImageTk.PhotoImage(img)
    e1 =tk.Label(my_w)
    e1.grid(row=4,column=0)
    e1.image = img
    e1['image']=img # garbage collection 

def upload_file2():
    filename = tk.filedialog.askopenfilename(multiple=False)
    global filename2
    filename2=filename
    img=Image.open(filename) # read the image file
    img=img.resize((150,200)) # new width & height
    img=ImageTk.PhotoImage(img)
    e1 =tk.Label(my_w)
    e1.grid(row=6,column=0)
    e1.image = img
    e1['image']=img # garbage collection 
def getscore(img_path,key_path):
  #for choices
  img = imread(img_path)
  threshold_pane1,threshold_pane2 = preprocessing(img)
  mychoice1 = detectchoice(threshold_pane1,26,3000)
  mychoice2 = detectchoice(threshold_pane2,16,3800)

  #for key
  imgk = imread(key_path)
  threshold_pane1k,threshold_pane2k = preprocessing(imgk)
  key1 = detectchoice(threshold_pane1k,26,3000)
  key2 = detectchoice(threshold_pane2k,16,3800)
  key = key1+key2
  mychoices = mychoice1 + mychoice2
  print(key)
  print(mychoices)
  marks = 0
  mselection =0
  eselection =0
  for i in range(40):
    if(mychoices[i]=="M"):
      mselection=mselection+1
    if(mychoices[i]==""):
      eselection=eselection+1
    if (key[i]==mychoices[i] and mychoices[i] != "M" and mychoices[i] != ""):
      marks=marks+1
  
  l1 = tk.Label(my_w,text="Marks: "+str(marks),font=('times', 13))  
  l1.grid(row=8,column=0,padx=40,pady=1)
  l1 = tk.Label(my_w,text="Multiple Seletions: "+str(mselection),font=('times', 13))  
  l1.grid(row=9,column=0,padx=40,pady=1)
  l1 = tk.Label(my_w,text="Empty MCQ's: "+str(eselection),font=('times', 13))  
  l1.grid(row=10,column=0,padx=40,pady=1)


#driver code (GUI)
my_w = tk.Tk()
my_w.title('Optical Mark Recgonition ')
l1 = tk.Label(my_w,text='Optica',font=('times', 18, 'bold'))  
l1.grid(row=0,column=0)

l1 = tk.Label(my_w,text='How to use?',anchor=W,font=('times', 15,'underline'))  
l1.grid(row=1,column=0,sticky=W+E,padx=10)

l1 = tk.Label(my_w,text='Upload the paper that is to be checked.Then upload the solution image. Press Get Score to get analytics',font=('calibri', 12))  
l1.grid(row=2,column=0,padx=10)

loc = "C:\\Users\\dell\\Desktop\\Dip project\\A4_images\\bgf.png"
img=Image.open(loc) # read the image file
img=img.resize((450,240)) # new width & height
img=ImageTk.PhotoImage(img)
e1 =tk.Label(my_w)
e1.grid(row=4,column=0)
e1.image = img
e1['image']=img 

l1 = tk.Label(my_w,text='Step 1:',anchor=W,font=('times', 14))  
l1.grid(row=3,column=0,sticky=W+E,padx=40,pady=10)

b1 = Button(my_w, text='Upload image',command = lambda:upload_file1())
b1.grid(row=3,column=0,columnspan=3)

loc = "C:\\Users\\dell\\Desktop\\Dip project\\A4_images\\bgf.png"
img=Image.open(loc) # read the image file
img=img.resize((450,240)) # new width & height
img=ImageTk.PhotoImage(img)
e1 =tk.Label(my_w)
e1.grid(row=6,column=0)
e1.image = img
e1['image']=img 

l1 = tk.Label(my_w,text='Step 2:',anchor=W,font=('times', 14))  
l1.grid(row=5,column=0,sticky=W+E,padx=40,pady=10)

b2 = Button(my_w, text='Upload Solution',command = lambda:upload_file2())
b2.grid(row=5,column=0)

l1 = tk.Label(my_w,text='Step 3:',anchor=W,font=('times', 14))  
l1.grid(row=7,column=0,sticky=W+E,padx=40,pady=10)

b2 = Button(my_w, text='Get Score',command = lambda:getscore(filename1,filename2))
b2.grid(row=7,column=0)
               
my_w.mainloop()  # Keep the window open