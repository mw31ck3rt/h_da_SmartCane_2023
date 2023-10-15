class DataProcession():
    #variables
    mode = False #False -> near; True -> far
    #constants
    DISTANCE_NEAR_MODE = 1000
    DISTANCE_FAR_MODE = 2000
    
    def setMode(self):
        self.mode = not(self.mode) 
    
    def getFeedback(self,distance_1,distance_2):
        if self.mode == False: #set max distance depending on modus
            distance_max = self.DISTANCE_NEAR_MODE
        else:
            distance_max = self.DISTANCE_FAR_MODE
    
        if distance_1 > distance_max: #if measured value is outside range
            distance_1 = distance_max
        if distance_2 > distance_max:
            distance_2 = distance_max
        
        if distance_1 < distance_2: #smaller value for feedback
            distance = distance_1
        else:
            distance = distance_2
        #if measured distance is 500, output value is 500 at max. distance of 1000
        #if measured distance is 500, output value is 750 at max. distance of 2000
        #0 -> far, no feedback; 1000 -> close, max feedback
        return distance*(-1000/distance_max)+1000 #return for Marian

if __name__ == "__main__":
    data = DataProcession()
    print(data.mode)
    data.setMode()
    print(data.mode)
    data.setMode()
    print(data.mode)
    feedback = data.getFeedback(500,999)
    print(feedback)
    data.setMode()
    feedback = data.getFeedback(500,999)
    print(feedback)

