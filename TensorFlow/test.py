from enum import Enum
from pyllist import dllist

class operation(Enum):
    BUY = 1
    SELL = 2
    MODIFY = 3
    CANCEL = 4
    PRINT = 5
    
class ExchangeSystem():
    
    def __init__(self, line_str): 
        self._input = line_str.split()
        if self._input[0] == operation.BUY.value:
            return 0
            
    def _SetOrderType(self,orderType): 
        self._orderType = orderType
    
    def _SetPrice(self, price): 
        self._price = price
        
    def _SetNewPrice(self, new_price): 
        self._NewPrice = new_price
                
    def _SetQuantity(self,quantity): 
        self._quantity = quantity
        
    def _SetNewQuantity(self,new_quantity): 
        self._NewQuantity = new_quantity
        
    def _SetOrderID(self,orderID): 
        self._orderID = orderID
    
    def _SetModifyOpe(self,newOpe): 
        self._newOperation = newOpe   
           
    def _GetOrderType(self): 
        return self._orderType
    
    def _GetPrice(self): 
        return self._price
    
    def _GetNewPrice(self): 
        return self._NewPrice
        
    def _GetQuantity(self): 
        return self._quantity
    
    def _GetNewQuantity(self): 
        return self._NewQuantity
        
    def _GetOrderID(self): 
        return self._orderID
    
    def _GetModifyOpe(self): 
        return self._newOperation
        
         
    def _IniBUY(self): 
        ls_input = self._input   
        self._SetOrderType(ls_input[0])
        self._SetPrice(ls_input[1])
        self._SetQuantity(ls_input[2])
        self._SetOrderID(ls_input[3])        
    
    def _IniSELL(self):    
        ls_input = self._input   
        self._SetOrderType(ls_input[0])
        self._SetPrice(ls_input[1])
        self._SetQuantity(ls_input[2])
        self._SetOrderID(ls_input[3])         
    
    def _IniModify(self):    
        ls_input = self._input  
        self._SetOrderID(ls_input[0]) 
        self._SetModifyOpe(ls_input[1])
        self._SetNewPrice(ls_input[2])
        self._SetNewQuantity(ls_input[3])
         
    
    def _IniCancel(self):    
        
        return 0 
    
    def _print(self):    
        
        return 0
    def _buy_sell(self):
                    
        

if __name__ == "__main__" :
    msg = "log_msg.txt"
    