# Optical-Mark-Recognition
This project conatains a OMR program using openCV and matplotlib. Main concepts of Image processing that were used are canny egde detection, adaptive thresholding and image contouring. All of these functionalities are present in the openCV library of python.

#File Structure
The repo contains an image folder that are the dataset for the program. The program works on the mentioned dataset only. There is a .py, .ipynb that gives the same output. The difference is just in extension and that the py file contains tkinter for GUI and py file conatins a driver function. 
There is also an executable file in the 'Executable-app' folder. **Note: ** The exe file contains path for the background image that is located in the root directory of the folder.

#how to use (.ipynb)
Place an image in the same directory of the code. Give the path of the image in the second bloq and start the process.Run the code using Visual Studio Code with a openCV and a python interpreter installed.

#how to use (.py)
The py file contains the tkinter library and has a GUI. Hence running the code simple with VS code would be self-explanatory

#how to use (.exe)
The exe file is converted from the py file through pyinstaller. The output should be same. **Note:** The exe will give an error if the bgf.jpg img is not placed in the said directory.
