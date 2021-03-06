import scipy
from scipy import special
import scipy.optimize as optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import logging

logger = logging.getLogger(__name__)


class GaussianERFFit:
    def __init__(self,data2D,grid):        
        self._data2D = data2D
        self._shape = data2D.shape

        self.grid = grid
       
        self.top,self.bottom,self.left,self.right, self.clipData = self._findRectangle()
        if self.clipData.any():        
            try:
                self.p = self._cacl_para()
                self.sigmaX = abs(self.p[2])
                self.sigmaY = abs(self.p[3])
                #print(self._Imx,self._Imy,self._IsigmaX,self._IsigmaY,self._IA)
                #print(self.p)
                #print("sigmaX is %f, sigmaY is %f"%(self.sigmaX,self.sigmaY))
    
                #===================================================================
                # figure2 = plt.figure()
                # ax = Axes3D(figure2)
                # X = np.arange(self.left,self.right,1)
                # Y = np.arange(self.top,self.bottom,1)
                # X,Y = np.meshgrid(X,Y)
                # ax.plot_surface(X,Y,self.clipData,rstride=1,cstride=1,cmap='rainbow')
                # plt.show()
                #===================================================================
            except Exception,e:
                logger.error('failed: Reason is: {}'.format(str(e)), exc_info=True)
                raise e 
        else:
            self.sigmaX = 0
            self.sigmaY = 0
            logger.info("zero dose case: assign to _IsigmaX and _IsigmaY to 0 for currentl layer")
    def _plot_2D(self):        
        #print(self._shape[0],self._shape[1],np.max(data2D))
        '''
        hIDD = np.zeros((shape[1],2),float)
        for i in range(shape[1]):
            hIDD[i,0] = i
            for j in range(shape[0]):
                for k in range(shape[2]):                    
                    hIDD[i,1] = hIDD[i,1] + data[k,i,j]
                    
        plt.figure(1)
        plt.plot(hIDD[0:shape[1],0], hIDD[0:shape[1],1])
        plt.show()      '''        

        figure2 = plt.figure()
        ax = Axes3D(figure2)
        X = np.arange(0,self._data2D[0],1)
        Y = np.arange(0,self._data2D[1],1)
        X,Y = np.meshgrid(X,Y)
        ax.plot_surface(X,Y,self._data2D,rstride=1,cstride=1,cmap='rainbow')
        plt.show()

        
        

    def _findRectangle(self): # check the edge with dose>0
        [top, bottom, left, right] = [0,self._shape[0]-1,0,self._shape[1]-1]        
        for i in range(0,self._shape[0],1):
            if(sum(self._data2D[i,0:self._shape[1]]) > 0):
                top = i
                break               
             
        for i in range(self._shape[0]-1,0,-1):
            if(sum(self._data2D[i,0:self._shape[1]])> 0):
                bottom = i
                break                
            
        for i in range(0,self._shape[1],1):
            if(sum(self._data2D[0:self._shape[0], i]) > 0):
                left = i
                break            
            
        for i in range(self._shape[1]-1,0,-1):
            if(sum(self._data2D[0:self._shape[0], i]) > 0):
                right = i
                break
        try:
            clippeddata2D = self._data2D[top:bottom, left:right]
            #===================================================================
            # if not [top, bottom, left, right] == [0,self._shape[0]-1,0,self._shape[1]-1]:
            #     clippeddata2D = self._data2D[top:bottom, left:right]
            # else:    
            #     clippeddata2D = self._data2D           
            #     #output = GaussianERFFitException("%s have zero dose!"% "current layer")   
            #     log_msg._write_log_msg("%s have zero dose!"% "current layer")             
            #===================================================================
        except:
            pass
        return top, bottom, left, right, clippeddata2D
    
    
    def _getInitP(self):
        try:
            self._Imx = (self.clipData.shape[1])/2.0
            self._Imy = (self.clipData.shape[0])/2.0
            self._IA = np.amax(self.clipData)*0.25#Martin's equation 0.25*A*erf()
            dataX = self.clipData[int(self._Imy), :]
            dataY = self.clipData[:, int(self._Imx)]
            if(dataX.any()):  # judge whether all the dose in current layer are zero
                self._IsigmaX = scipy.sqrt(scipy.average((scipy.arange(dataX.size) - int(self._Imx))**2, None, dataX)/2.0)
                self._IsigmaY = scipy.sqrt(scipy.average((scipy.arange(dataY.size) - int(self._Imy))**2, None, dataY)/2.0)
            else:
                self._IsigmaX=0
                self._IsigmaY=0
                logger.info("zero dose case: assign to _IsigmaX and _IsigmaY to 0 for currentl layer")
        except Exception,e:
            logger.error('getInitP() failed: Reason is: {}'.format( str(e)), exc_info=True)
            raise e
        return self._Imx, self._Imy,self._IsigmaX,self._IsigmaY,self._IA
     
    def _cacl_para(self):

        def ferf(mx,my,sigmaX,sigmaY,A):
            delta = self.grid
            #return lambda x, y : scipy.longfloat(0.25*A*scipy.exp(-((x-mx)*delta)**2/(2*sigmaX**2) - (((y-my)*delta)**2/(2*sigmaY**2))))
            return lambda x, y : 0.25*A*(special.erf(((x-mx+0.5)*delta)/(scipy.sqrt(2.0)*sigmaX))-special.erf(((x-mx-0.5)*delta)/(scipy.sqrt(2.0)*sigmaX)))*(scipy.special.erf(((y-my+0.5)*delta)/(scipy.sqrt(2.0)*sigmaY))-scipy.special.erf(((y-my-0.5)*delta)/(scipy.sqrt(2.0)*sigmaY)))
        def errorSquare(p):
            cd = self.clipData
            y, x= scipy.indices(cd.shape) # data2D = data[0:shape[2],self.Plane,0:shape[0]], depth,height,width = z,y,x here.
            f = ferf(*p)
            return (f(x,y) - cd).ravel()
        initialP = self._getInitP()
        p, cov, infodict, msg, ier = optimize.leastsq(errorSquare, initialP, full_output = True)
        return p      
        