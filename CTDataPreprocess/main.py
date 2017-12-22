import os
import dicom
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage
from skimage import measure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


bs_path = "D:/Python_data/sample_images"
l_patientName = np.sort(os.listdir(bs_path))

#load_dicom: only load one patient data, also save the sliceThkiness
def load_dicom(patient_name):
    cr_path = bs_path + '/'+ patient_name  #consider only one patient data
    image = []
    dicom_slice_data = []
    
    for cr_sliceImage in os.listdir(cr_path):
        path_sliceImage =  cr_path + '/'+ cr_sliceImage
        dicom_file = dicom.read_file(path_sliceImage)
               
        #image = np.append(image,dicom_file.pixel_array,axis=0)
        dicom_slice_data.append(dicom_file)
    dicom_slice_data.sort(key = lambda x: float(x.SliceLocation)) 
    
    #3.for loop slice data to get volume
    for i in dicom_slice_data:
        image.append(i.pixel_array)
    image_volume=np.stack(image)     
                   
    if dicom_slice_data[0].__contains__("ImagePositionPatient"):
        st_0 = dicom_slice_data[0].data_element("ImagePositionPatient").value
        st_1 = dicom_slice_data[1].data_element("ImagePositionPatient").value
        sliceThickness =  np.abs(np.float(st_0[2])-np.float(st_1[2]))
    elif dicom_slice_data[0].__contains__('SliceLocation'):
        st_0 = np.float(dicom_slice_data[0].data_element("SliceLocation").value)
        st_1 = np.float(dicom_slice_data[1].data_element("SliceLocation").value)
        sliceThickness =  np.abs(st_0-st_1)
        
    for i in dicom_slice_data:
        i.slice_thickness =  sliceThickness   
              
    return image_volume, dicom_slice_data

'''
outside of these bounds get the fixed value -2000. 
The first step is setting these values to 0, which currently corresponds to air. 
Next, let's go back to HU units, by multiplying with the rescale slope and adding the intercept 
(which are conveniently stored in the metadata of the scans!).Some scanners have cylindrical scanning bounds, but the output image is square. 
The pixels that fall 
'''
# get HU unit
def Get_pixel_HU(image,dicom_slice_data):
    for index in range(len(dicom_slice_data)):
        rescaleIntercept = np.float(dicom_slice_data[index].RescaleIntercept)
        rescaleSlope = np.float(dicom_slice_data[index].RescaleSlope)
           
        shape_image = image[index].shape
        for i in range(shape_image[0]):
            for j in range(shape_image[1]):
                if image[index][i,j]==-2000:
                    image[index][i,j]=0                
                image[index][i,j] = rescaleIntercept + rescaleSlope*image[index][i,j]           
            
    return image

def plot_2DSlice_image(slice_image):
    plt.figure()
    plt.imshow(slice_image,cmap=plt.get_cmap('gray'))
    plt.show()
    
#resample image from ununiform to get the uniform image
def resample(image_3D,dicom_slice_data,new_voxel_size):
    volume_number = image_3D.shape    #134/512/512
    # 0.2, 0.6,0.6
    voxel_size = np.array([dicom_slice_data[0].slice_thickness] + dicom_slice_data[0].PixelSpacing, dtype=np.float32)
    scale_size =  new_voxel_size/voxel_size   # 5/1.7/1.7
    volume_number_actual = volume_number / scale_size   # 26.7/256.3/256.3
    volume_number_round = np.round(volume_number_actual)    #27/256/256
    new_rescale_size = volume_number_round/volume_number
    new_rescale_voxel_size = voxel_size / new_rescale_size
        
    image = scipy.ndimage.interpolation.zoom(image_3D, zoom=new_rescale_size, mode='nearest')
    return image,new_rescale_voxel_size          
         
#plot_3D
def plot_3D_image(3D_image,threshold=-300):
    p = 3D_image.transpose(2,1,0)
    verts, faces,normals, values = measure.marching_cubes(p, threshold, spacing=(0.1, 0.1, 0.1))
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')    
    ax.plot_trisurf(verts[:, 0], verts[:,1], faces, verts[:, 2],cmap='Spectral', lw=1)
    plt.show()
    
#segmentation

if __name__ == '__main__':
    image_volume,dicom_slice_data = load_dicom(l_patientName[0])
    image = np.array(image_volume)
    image_HU = Get_pixel_HU(image,dicom_slice_data)
    plot_2DSlice_image(image_HU[80])
    image,new_pixel_size = resample(image_HU,dicom_slice_data,[1,1,1])