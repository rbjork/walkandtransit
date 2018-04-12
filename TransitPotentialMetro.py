import arcpy
import os
from Tkinter import Tk
from tkFileDialog import askdirectory

def doesFieldExist(fc, fname):
  lst = arcpy.ListFields(fc)
  exists = False
  for f in lst:
    if f.name == fname:
      exists = True
      break
  return exists

def addTransitAccess(transitdir,countydir,transitdata,geoDataBaseName, addfield, transitstops_lyr):
    countypath = dataPath + countydir + "\\"
    arcpy.FeatureClassToGeodatabase_conversion(transitdir + "\\" + countydir + "\\" + transitdata, countypath + geoDataBaseName)
    featureclass= transitdata.split(".")[0]
    accessExists = doesFieldExist(countypath + geoDataBaseName + "\\" + featureclass, "access")
    if not accessExists:
        arcpy.AddField_management(countypath + geoDataBaseName + "\\" + transitdata, "access", "TEXT")
    '''
    expression = "getJobAccessScore(!X_Coord!)"
    codeblock = """def getJobAccessScore(lng):
    v = int(lng)
    if v <= 5975000:
        return '1'
    if v > 5975000 and v <= 5979000:
        return '2'
    if v > 5979000:
        return '3'"""

    #arcpy.CalculateField_management(countypath + "\\" + geoDataBaseName + "\\" + featureclass, "access", expression,"PYTHON_9.3",codeblock)
    '''
    arcpy.MakeFeatureLayer_management(countypath + "\\" + geoDataBaseName + "\\" + featureclass, transitstops_lyr)

def addTransitPotential(countydir,geoDataBaseName):
    countyPath = dataPath + countydir + "\\"
    expression = "setDefaultScore()"
    codeblock = """def setDefaultScore():
    return '0'"""
    arcpy.AddField_management(countyPath + geoDataBaseName + "\\parcels" , "potential", "TEXT")
    arcpy.CalculateField_management(countyPath + geoDataBaseName + "\\parcels" , "potential", expression,"PYTHON_9.3",codeblock)

def bufferTransitStops_QUARTER(transitstops, bufferedName, geoDataBaseName):
    print "bufferDestinations"
    transitpath = homePath + "transit\\"
    arcpy.Buffer_analysis( transitpath  + geoDataBaseName + "\\" + transitstops, transitpath + "\\" + geoDataBaseName + "\\" + bufferedName, "1320 Feet")
    arcpy.MakeFeatureLayer_management(transitpath + "\\" + geoDataBaseName + "\\" + bufferedName, bufferedName)

def bufferTransitStops_HALF(transitstops, bufferedName, geoDataBaseName):
    print "bufferDestinations"
    transitpath = homePath + "transit\\"
    arcpy.Buffer_analysis( transitpath  + geoDataBaseName + "\\" + transitstops, transitpath + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")
    arcpy.MakeFeatureLayer_management(transitpath + "\\" + geoDataBaseName + "\\" + bufferedName, bufferedName)

def scoreparcels(targetFeature,bufferedTransitStop,geoDataBaseName, halfMile, access, layerCount):
    layerCount = layerCount + 1
    parcel_layer = 'parcels_lyr' + str(layerCount)
    fcnear = bufferedTransitStop  #'c:/data/base.gdb/well'
    fctarget = targetFeature
    countyPath = dataPath + countydir + "\\"
    arcpy.env.workspace = countyPath + "\\" + geoDataBaseName

    arcpy.MakeFeatureLayer_management(targetFeature, parcel_layer)
    #arcpy.SelectLayerByAttribute_management(fcnear, "SUBSET_SELECTION", "access > 10000")
    arcpy.SelectLayerByLocation_management(parcel_layer, 'intersect', fcnear)
    #arcpy.CopyFeatures_management('parcels_lyr', countyPath + "\\" + geoDataBaseName + "\\?")
    expression = "setScore('"+str(access)+"')"
    if halfMile:     # Quarter Mile
        codeblock = """def setScore(access):
        if access == 'LOW':
            return '1'
        if access == 'MEDIUM':
            return '3'
        if access == 'HIGH':
            return '5'"""
    else:               # Half Mile
        codeblock = """def setScore(access):
        if access == 'LOW':
            return '2'
        if access == 'MEDIUM':
            return '4'
        if access == 'HIGH':
            return '6'"""

    countypath = dataPath +  countydir + "\\"
    arcpy.CalculateField_management(parcel_layer, "potential", expression,"PYTHON_9.3",codeblock)


'''
There are two groups of datasets: Parcels and TransitStops.
Within TransitStops datasets there are three smaller datasets: transitStopsAccessLow,transitStopsAccessMedium and transitStopsAccessHigh
'''

def promptForFoldersForMetro():
    print("Please select the directory containing the metro counties to be processed:")
    Tk().withdraw() #prevents Tk window from showing up unnecessarily
    file_directory = askdirectory() #opens directory selection dialog
    os.chdir(homedir)
    arcpy.env.workspace = homedir
    metro_counties = os.listdir(file_directory)
    return metro_counties

# def createTransitStops(countyFolderList):
#      for countydir in countyFolderList:
#         addTransitAccess(transitdir,countydir,transitdata,geoDataBaseName,True,transitLayer)
#         newgdbfiles = features2gdb(countyFolderList, dataPath + countydir, geoDataBaseName)
#         addTransitPotential(countydir,newgdbfiles,geoDataBaseName) # sets all parcel TransitPotential values to default value of 0
#         method1 = True
#         if method1:
#             splitTransitStopsData(transitdata,transitLayer,countydir)
#

# 12/9/2015 Builds parcels for county geo database
def countyParcels2gdb(countyfolder,geodbname):
    outWorkspace = homedir + "\\data\\" + str(countyfolder) + "\\" + geodbname
    arcpy.env.workspace = homedir + "\\data\\" + str(countyfolder) # + "\\" + str(countyfolder)
    for fc in arcpy.ListFeatureClasses():
        if str(fc) == "Parcels.shp":
            # Process: Delete Field
            arcpy.DeleteField_management(fc, "APN2;STATE;COUNTY;FIPS;SIT_HSE_NU;SIT_DIR;SIT_STR_NA;SIT_STR_SF;SIT_FULL_S;SIT_CITY;SIT_STATE;SIT_ZIP;SIT_ZIP4;SIT_POST;LAND_VALUE;TOT_VALUE;ASSMT_YEAR;MKT_LAND_V;MKT_IMPR_V;TOT_MKT_VA;MKT_VAL_YR;REC_DATE;SALES_PRIC;SALES_CODE;YEAR_BUILT;CONST_TYPE;LOT_SIZE;NO_OF_STOR;BEDROOMS;BATHROOMS;OWNADDRES2;OWNCTYSTZP")
            arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)
    return


# Alternative approach which may not be needed - creates seperate features for each set of transit stops distinquished by access
def splitTransitStopsData(transitDataLayer,metroTransitStops,geoTransitdbname):
    for transitStops in metroTransitStops:
        arcpy.MakeFeatureLayer_management(homePath + "transit\\" + geoTransitdbname + "\\" + transitStops, transitDataLayer)
    arcpy.SelectLayerByAttribute_management(transitDataLayer, "CLEAR_SELECTION")
    for transitStops in metroTransitStops:
        arcpy.SelectLayerByAttribute_management(transitDataLayer, "ADD_TO_SELECTION", "\"access\" = 1")
    arcpy.CopyFeatures_management(transitDataLayer, homePath  + "transit\\" + geoTransitdbname + "\\transitStopsAccessLow")
    arcpy.SelectLayerByAttribute_management(transitDataLayer, "CLEAR_SELECTION")
    for transitStops in metroTransitStops:
        arcpy.SelectLayerByAttribute_management(transitDataLayer, "ADD_TO_SELECTION", "\"access\" = 2")
    arcpy.CopyFeatures_management(transitDataLayer, homePath  + "transit\\" + geoTransitdbname + "\\transitStopsAccessMedium")
    arcpy.SelectLayerByAttribute_management(transitDataLayer, "CLEAR_SELECTION")
    for transitStops in metroTransitStops:
        arcpy.SelectLayerByAttribute_management(transitDataLayer, "ADD_TO_SELECTION", "\"access\" = 3")
    arcpy.CopyFeatures_management(transitDataLayer, homePath  + "transit\\" + geoTransitdbname + "\\transitStopsAccessHigh")


def metroTransitStops2gdb(countyFolderList,geoTransitdbname):
    geoTransitdbWorkspace = homePath + "transit\\" + geoTransitdbname
    metroTransitStops = []
    #for countydir in countyFolderList:
    arcpy.env.workspace = homePath + "transit" #\\"  + str(countydir)
    for fc in arcpy.ListFeatureClasses():
        if str(fc).lower().find("transit") != -1:
            print fc
            arcpy.FeatureClassToGeodatabase_conversion(fc, geoTransitdbWorkspace)
            metroTransitStops.append(fc.split('.')[0])
    return metroTransitStops


if __name__ == '__main__':

    homedir =  os.getcwd()
    homePath = homedir + "\\"
    dataPath = homePath + "data\\"
    transitdir = homedir + "\\transit"
    transitdata = "TRANSIT.shp"
    transitLayer = "transitstops_lyr"
    countyFolderList = promptForFoldersForMetro()
    geoTransitdbname = "transitStops.gdb"
    layerCount = 0

    arcpy.CreateFileGDB_management(transitdir, geoTransitdbname)
    metroTransitStops = metroTransitStops2gdb(countyFolderList, geoTransitdbname)
    #addTransitAccess(transitdir,countydir,transitdata,geoDataBaseName,True,transitLayer)
    #transitDataLayer,metroTransitStops,geoTransitdbname
    splitTransitStopsData(transitLayer,metroTransitStops, geoTransitdbname)

    for countydir in countyFolderList:
        #countydir = "06041" #countyFolderList[0] # single county test
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        arcpy.CreateFileGDB_management(dataPath + countydir, geoDataBaseName)
        countyParcels2gdb(countydir, geoDataBaseName)
        #newgdbfiles = features2gdb(countyFolderList, dataPath + countydir, geoDataBaseName)
        addTransitPotential(countydir,geoDataBaseName) # sets all parcel TransitPotential values to default value of 0
        layerCount = 0

    # Low Access
    bufferTransitStops_HALF("transitStopsAccessLow","transitbufferedLow1", geoTransitdbname)
    for countydir in countyFolderList:
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        scoreparcels("parcels","transitbufferedLow1",  geoDataBaseName,True,'LOW', layerCount) # Give overlaps parcels score 1

    bufferTransitStops_QUARTER("transitStopsAccessLow","transitbufferedLow2", geoTransitdbname)
    for countydir in countyFolderList:
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        scoreparcels("parcels","transitbufferedLow2",  geoDataBaseName,False,'LOW', layerCount) # Give overlaps parcels score 2

    # Medium Access
    bufferTransitStops_HALF("transitStopsAccessMedium","transitbufferedMedium1", geoTransitdbname)
    for countydir in countyFolderList:
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        scoreparcels("parcels","transitbufferedMedium1",  geoDataBaseName,True,'MEDIUM', layerCount) # Give overlaps parcels score 3

    bufferTransitStops_QUARTER("transitStopsAccessMedium","transitbufferedMedium2", geoTransitdbname)
    for countydir in countyFolderList:
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        scoreparcels("parcels","transitbufferedMedium2",  geoDataBaseName,False,'MEDIUM', layerCount) # Give overlaps parcels score 4

    # High  Access
    bufferTransitStops_HALF("transitStopsAccessHigh","transitbufferedHigh1", geoTransitdbname)
    for countydir in countyFolderList:
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        scoreparcels("parcels","transitbufferedHigh1",  geoDataBaseName,True,'HIGH',layerCount) # Give overlaps parcels score 5

    bufferTransitStops_QUARTER("transitStopsAccessHigh","transitbufferedHigh2", geoTransitdbname)
    for countydir in countyFolderList:
        geoDataBaseName = "transitdb"  + countydir + ".gdb"
        scoreparcels("parcels","transitbufferedHigh2",  geoDataBaseName,False,'HIGH',layerCount) # Give overlaps parcels score 6


    print "COMPLETE"
