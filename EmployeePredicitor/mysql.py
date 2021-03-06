import MySQLdb

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import dicom
import os
import scipy.ndimage
import matplotlib.pyplot as plt


# Some constants 
INPUT_FOLDER = 'D:/Python_data/sample_images/'
patients = os.listdir(INPUT_FOLDER)
patients.sort()

# Load the scans in given folder path
def load_scan(path):
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
        
    for s in slices:
        s.SliceThickness = slice_thickness
        
    return slices

    
def query_with_fetchone(slices):
    try:
        conn = MySQLdb.connect( host="127.0.0.1", port=3306, user="root", passwd="111111", db="awesome" )
        cursor = conn.cursor()
        
        cursor.execute("USE mydatabase") # select the database
        cursor.execute("SHOW TABLES")    # execute 'SHOW TABLES' (but data is not returned)
        tables = cursor.fetchall() # return tuple
        if tables.__contains__(("users",)):
            cursor.execute("SELECT * FROM users")
 
        row = cursor.fetchone()
 
        while row is not None:
            print(row)
            row = cursor.fetchone()
 
    finally:
        cursor.close()
        conn.close()
 
 
if __name__ == '__main__':
    first_patient = load_scan(INPUT_FOLDER + patients[0])
    query_with_fetchone(first_patient)