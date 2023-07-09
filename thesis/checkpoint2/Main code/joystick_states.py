class State:
    def enter(self):
        pass
    
    def run(self,machine):
        pass
    
    def exit(self):
        pass

class NeutralState(State):
    def enter(self):
#         print("Joystick in neutral")
        pass
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
 
class NorthState(State):
    def enter(self):
        print("North")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
 
class SouthState(State):
    def enter(self):
        print("South")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass

class EastState(State):
    def enter(self):
        print("East")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass

class WestState(State):
    def enter(self):
        print("West")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class cam_NeutralState(State):
    def enter(self):
#         print("Joystick in neutral")
        pass        
    def run(self,machine):
        pass
    
    def exit(self):
        pass

class cam_NorthState(State):
    def enter(self):
        print("North")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
 
class cam_SouthState(State):
    def enter(self):
        print("South")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass

class cam_EastState(State):
    def enter(self):
        print("East")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass

class cam_WestState(State):
    def enter(self):
        print("West")
        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
