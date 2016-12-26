import remi.gui as gui
from remi.gui import to_pix
from remi import start, App
from threading import Timer

class LCDApp(App):
    def __init__(self, *args):
        super(LCDApp, self).__init__(*args, static_paths=('./res/',))

    def main(self):
        mainContainerWidth = 400 #will use this later to arrange buttons position
        self.mainContainer = gui.VBox(width=mainContainerWidth, height=600)
        
        self.imageRoom = gui.Image('./res/room.png', height=300)
        #suggestion: in order to change the displayed image you can do 
        #self.imageRoom.attributes['src'] = './res/new_image.png'
        self.mainContainer.append(self.imageRoom)
        
        #here we builds info labels and container
        labelsContainer = gui.Widget(width="100%", height=50) #the container is of type Widget, allowing to define custom position for each contained item
        self.mainContainer.append(labelsContainer)
        labelsContainer.style['position'] = 'relative' #this is important in order to obtain an aboslute positioning

        w=75
        h=25
        lblRoomName = gui.Label('Room:', width=w, height=h)
        self.lblRoomNameValue = gui.Label('living', width=w, height=h)
        
        lblCurrentTemperature = gui.Label('Current:', width=w, height=h)
        self.lblCurrentTemperatureValue = gui.Label('21 C', width=w, height=h)
        
        lblTargetTemperature = gui.Label('Target:', width=w, height=h)
        self.lblTargetTemperatureValue = gui.Label('22.5 C', width=w, height=h)
        
        #setup of the labels position
        lblRoomName.style['left'] = '5px'
        lblRoomName.style['top'] = '0px'
        lblRoomName.style['position'] = 'absolute'
        self.lblRoomNameValue.style['left'] = '80px'
        self.lblRoomNameValue.style['top'] = '0px'
        self.lblRoomNameValue.style['position'] = 'absolute'
        self.lblRoomNameValue.style['font-weight'] = 'bold'
        
        lblCurrentTemperature.style['left'] = '255px'
        lblCurrentTemperature.style['top'] = '0px'
        lblCurrentTemperature.style['position'] = 'absolute'
        self.lblCurrentTemperatureValue.style['left'] = '330px'
        self.lblCurrentTemperatureValue.style['top'] = '0px'
        self.lblCurrentTemperatureValue.style['position'] = 'absolute'
        self.lblCurrentTemperatureValue.style['font-weight'] = 'bold'
        
        lblTargetTemperature.style['left'] = '255px'
        lblTargetTemperature.style['top'] = '25px'
        lblTargetTemperature.style['position'] = 'absolute'
        self.lblTargetTemperatureValue.style['left'] = '330px'
        self.lblTargetTemperatureValue.style['top'] = '25px'
        self.lblTargetTemperatureValue.style['position'] = 'absolute'
        self.lblTargetTemperatureValue.style['font-weight'] = 'bold'
        
        #inserting the labels in their container
        labelsContainer.append(lblRoomName)
        labelsContainer.append(self.lblRoomNameValue)
        labelsContainer.append(lblCurrentTemperature)
        labelsContainer.append(self.lblCurrentTemperatureValue)
        labelsContainer.append(lblTargetTemperature)
        labelsContainer.append(self.lblTargetTemperatureValue)
        
        
        #here we build buttons and container
        buttonsContainer = gui.Widget(width="100%", height=150)
        self.mainContainer.append(buttonsContainer)
        buttonsContainer.style['position'] = 'relative' #this is important in order to obtain an aboslute positioning
        btWidth = 50
        btHeight = 50
        self.btUp = gui.Button('+', width=btWidth, height=btHeight)
        self.btDown = gui.Button('-', width=btWidth, height=btHeight)
        self.btRight = gui.Button('>', width=btWidth, height=btHeight)
        self.btLeft = gui.Button('<', width=btWidth, height=btHeight)
        
        self.btUp.set_on_click_listener(self, "on_click_up")
        self.btDown.set_on_click_listener(self, "on_click_down")
        self.btRight.set_on_click_listener(self, "on_click_right")
        self.btLeft.set_on_click_listener(self, "on_click_left")
        
        self.btUp.style['left']=to_pix(mainContainerWidth/2-btWidth/2)
        self.btUp.style['top']=to_pix(0)
        self.btUp.style['position'] = 'absolute'
        
        self.btDown.style['left']=to_pix(mainContainerWidth/2-btWidth/2)
        self.btDown.style['top']=to_pix(btHeight*2)
        self.btDown.style['position'] = 'absolute'
        
        self.btRight.style['left']=to_pix(mainContainerWidth/2+btWidth/2)
        self.btRight.style['top']=to_pix(btHeight)
        self.btRight.style['position'] = 'absolute'
        
        self.btLeft.style['left']=to_pix(mainContainerWidth/2-btWidth*3/2)
        self.btLeft.style['top']=to_pix(btHeight)
        self.btLeft.style['position'] = 'absolute'
        
        buttonsContainer.append(self.btUp)
        buttonsContainer.append(self.btDown)
        buttonsContainer.append(self.btRight)
        buttonsContainer.append(self.btLeft)

        #here we start a timer
        Timer(1, self.update).start()
        
        # returning the root widget
        return self.mainContainer

    # listener function
    def on_click_up(self):
        pass
        
    # listener function
    def on_click_down(self):
        pass
    
    # listener function
    def on_click_right(self):
        pass
        
    # listener function
    def on_click_left(self):
        pass
       
    def update(self):
        #the code written here is executed each second
        pass


if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(LCDApp, address='0.0.0.0', debug=True)
