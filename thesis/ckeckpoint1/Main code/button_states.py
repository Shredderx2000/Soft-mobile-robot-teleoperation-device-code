class State:
    def enter(self):
        pass
    
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class OffState(State):
    def enter(self):
        print("system is off")
    
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class OnState(State):
    def enter(self):
        print("system is on")

        
    def run(self,machine):
        pass
            
    def exit(self):
        GPIO.output(machine.led_pin, GPIO.LOW)

class GaitState(State):
    def __init__(self, num_gaits=3, current_gait=1):
        self.num_gaits = num_gaits
        self.current_gait = current_gait
    
    def enter(self):
        print(f"Gait state {self.current_gait}")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
    def increment(self,machine):
        self.current_gait += 1
        if self.current_gait > self.num_gaits:
            self.current_gait = 1
        machine.current_state.gait_state = GaitState(self.num_gaits, self.current_gait)
        machine.current_state.gait_state.enter()
        
    def decrement(self,machine):
        self.current_gait -= 1
        if self.current_gait < 1:
            self.current_gait = self.num_gaits
        machine.current_state.gait_state = GaitState(self.num_gaits, self.current_gait)
        machine.current_state.gait_state.enter()
            
class func1_OnState(State):
    def enter(self):
        print("function 1 on")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class func1_OffState(State):
    def enter(self):
        print("function 1 off")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class func2_OnState(State):
    def enter(self):
        print("function 2 on")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class func2_OffState(State):
    def enter(self):
        print("function 2 off")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class ButtonStates:
    def __init__(self):
        self.gait_state = None
        self.function1_state = None
        self.function2_state = None
        self.gait_num = 1

    def reset(self):
        self.gait_state = GaitState1()
        self.function1_state = func1_OffState()
        self.function2_state = func2_OffState()