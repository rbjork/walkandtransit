__author__ = 'dev'
# This version merges all the counties in the metro, filters out the destinations in the metro.
# Then it bufferes all the destinations
# Then takes then
import arcpy,os,sys
import time
from Tkinter import Tk
from tkFileDialog import askdirectory

# Note that if the attribute 'destination' in parcels exist (from maybe RTJoinFor2Maps) that the lengthy
# queuies in 'selectDestination' can be replaced by simple check of destination attribute
def selectDestinations(destinations,outputName):
    print "selectDestinations"
    #arcpy.env.workspace = arcpy.GetParameterAsText(0)
    Dir = arcpy.env.workspace

    expression1 = 'NOT "STD_LAND_U" = \'RAPT\' AND NOT "STD_LAND_U" = \'RSFR\' AND NOT "STD_LAND_U" = \'RCON\' AND NOT "STD_LAND_U" = \'RCOO\' AND NOT "STD_LAND_U" = \'RDUP\' AND NOT "STD_LAND_U" = \'RMOB\' AND NOT "STD_LAND_U" = \'RMSC\' AND NOT "STD_LAND_U" = \'RQUA\' AND NOT "STD_LAND_U" = \'RSFR\' AND NOT "STD_LAND_U" = \'RTIM\' AND NOT "STD_LAND_U" = \'RTRI\' AND NOT "STD_LAND_U" = \'RMFD\''
    expression2 = '"IMPR_VALUE" > \'0\''
    expression3 = '"OWNER" LIKE \'%PARK%\' OR "OWNER" LIKE \'%RECREATION%\'  OR "OWNER" LIKE \'%TOWN%\'  OR "OWNER" LIKE \'%COUNTY%\'  OR "OWNER" LIKE \'%STATE%\'  OR "OWNER" LIKE \'%DISTRICT%\' OR "OWNER" LIKE \'%SCHOOL%\'  OR "OWNER" LIKE \'%ELEMENTARY%\'  OR "OWNER" LIKE \'%MIDDLE%\'  OR "OWNER" LIKE \'%LIBRARY%\'  OR "OWNER" LIKE \'%K8 K12%\'  OR "OWNER" LIKE \'%HOSPITAL%\' OR "OWNER" LIKE \'%CIVIC%\'  OR "OWNER" LIKE \'%CLINIC%\'  OR "OWNER" LIKE \'%FACILITY%\' OR "OWNER" LIKE \'%COMMUNITY%\'  OR "OWNER" LIKE \'%PLAYGROUND%\' OR "OWNER" LIKE \'%CHURCH%\'  OR "OWNER" LIKE \'%TEMPLE%\'  OR "OWNER" LIKE \'%MOSQUE%\' OR "OWNER" LIKE \'%FOREST%\'  OR "OWNER" LIKE \'%MUNICIPAL%\' OR "OWNER" LIKE \'%UNIVERSITY%\'  OR "OWNER" LIKE \'%DAYCARE%\''

    # Within selected features, further select based on a SQL query within the script tool
    arcpy.MakeFeatureLayer_management(destinations, "destLyr")
    arcpy.SelectLayerByAttribute_management("destLyr", "NEW_SELECTION", expression1)
    arcpy.SelectLayerByAttribute_management("destLyr", "SUBSET_SELECTION", expression2)
    arcpy.SelectLayerByAttribute_management("destLyr", "ADD_TO_SELECTION", expression3)

    # Write the selected features to a new featureclass
    arcpy.CopyFeatures_management("destLyr", Dir + "\\" + str(outputName))

# OR

def selectDestinationsByDestinationAttribute(destinations,ouputName):
    Dir = arcpy.env.workspace
    arcpy.MakeFeatureLayer_management(destinations, "destLyr")
    expression = '"destination" > \'0\''
    arcpy.SelectLayerByAttribute_management("destLyr", "NEW_SELECTION", expression)
    arcpy.CopyFeatures_management("destLyr", Dir + "\\" + str(outputName))

#arcpy.Buffer_analysis("C:/Users/dev/Documents/boundarysolutions/marin/commercial.shp", "C:/Users/dev/Documents/boundarysolutions/marin/commercialBufferedHalf.shp","2640 Feet")

def createWalkabilityLayer(featureScored,walklayer):
    logout.write('calling createWalkabilityLayer'+ '\n')
    print "createWalkabilityLayer"
    expression = '"walkable" = \'' + walklayer + '\''
    Dir = arcpy.env.workspace
    arcpy.MakeFeatureLayer_management(featureScored, "walkLyr")
    arcpy.SelectLayerByAttribute_management("walkLyr", "NEW_SELECTION", expression)
    arcpy.CopyFeatures_management("walkLyr", Dir + "\\" + str(walklayer))

def shapeFileRename(srcfile,dstfile):
    src = srcfile.split('.')[0]
    dst = dstfile.split('.')[0]
    for typ in ['.shp','.dbf','.shx','.sbn','.sbx','.prj']:
        srcfile = src + typ
        dstfile = dst + typ
        os.rename(srcfile,dstfile)

def features2gdb(countyfoldersList,outdir,geodbname):
    print "features2gdb"
    outWorkspace = outdir + "\\" + geodbname
    newfilelist = []
    n = 0
    for countyfolder in countyfoldersList:
        arcpy.env.workspace = homedir + "\\data\\" + str(countyfolder)
        for fc in arcpy.ListFeatureClasses():
            '''
            print "fc", fc, type(fc)
            fcname = str(countyfolder) + "_" + fc
            print "fcname",type(fcname)
            srcfile = homedir + "\\data\\" + str(countyfolder) + "\\" + fc
            dstfile = homedir + "\\data\\" + str(countyfolder) + "\\" + fcname
            shapeFileRename(srcfile,dstfile)
            newfilelist.append(dstfile)
            '''
            arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)
            if n > 0:
                filename = fc.split('.')[0]
                typ = fc.split('.')[1]
                newfilelist.append(filename + "_" + str(n) + "." + typ)
            else:
                newfilelist.append(fc)
        n = n + 1
    return newfilelist

def bufferDestinations(destinations,bufferedName, geoDataBaseName):
    print "bufferDestinations"
    arcpy.Buffer_analysis( homedir + "\\" + geoDataBaseName + "\\" + destinations, homedir + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")

def scoreParcelsShape(targetFeature,nearFeature, outputName, geoDataBaseName):
    fcnear = nearFeature + "_shp" #'c:/data/base.gdb/well'
    fctarget = targetFeature + "_shp"
    arcpy.env.workspace = homedir + "\\" + geoDataBaseName
    arcpy.MakeFeatureLayer_management(targetFeature, 'parcels_lyr')
    fields = ['owner_1', 'std_landuse', 'SHAPE@XY']
    with arcpy.da.SearchCursor(fcnear, fields) as cursor1:
        for row1 in cursor1:
            # Make a layer and select cities which overlap the chihuahua polygon
            arcpy.SelectLayerByLocation_management('parcels_lyr', 'intersect', fctarget)
            # Within the previous selection sub-select cities which have population > 10,000
            arcpy.SelectLayerByAttribute_management('parcels_lyr','SUBSET_SELECTION', '"intersect_count" > 1')

#If features matched criteria write them to a new feature class
#matchcount = int(arcpy.GetCount_management('cities_lyr').getOutput(0))

def scoreParcels(targetFeature,nearFeature, outputName, geoDataBaseName):
    targetFeature = targetFeature + "_shp"
    nearFeature = nearFeature
    print "scoreParcels"
    #arcpy.SpatialJoin_analysis("multiresidence", "commercialBufferedHalf", "multiresdencescore")
    arcpy.SpatialJoin_analysis(homedir + "\\" + geoDataBaseName + "\\" + targetFeature, homedir + "\\" + geoDataBaseName + "\\" +nearFeature, "targetFeatureScored")
    arcpy.FeatureClassToGeodatabase_conversion(homedir + "\\" +"targetFeatureScored.shp", geoDataBaseName)
    arcpy.AddField_management(homedir + "\\" + geoDataBaseName + "\\targetFeatureScored", "walkable", "TEXT")
    expression = "getScore(!Join_Count!)"
    codeblock = """def getScore(cnt):
    cnt = int(cnt)
    if cnt <= 30:
        return 'walk1'
    if cnt > 31 and cnt <= 70:
        return 'walk2'
    if cnt > 71 and cnt <= 110:
        return 'walk3'
    if cnt > 111 and cnt <= 135:
        return 'walk4'
    if cnt > 135:
        return 'walk5'
    else:
        return 'walk0'"""
    arcpy.CalculateField_management(homedir + "\\" + geoDataBaseName + "\\targetFeatureScored", "walkable", expression,"PYTHON_9.3",codeblock)


# NEW and needs integration
def loadAndMergeCountiesInMetro(targetParcels,metroCountyParcels):  # These are from county shape files - not parcel shapefiles
    fieldMappings = None
    metro = targetParcels
    merge_cnt = 0
    for county in metroCountyParcels:
        metroOut = homedir + "\\data\\walk.gdb\\meroOut" + str(merge_cnt)
        countypath = homedir + "\\data\\walk.gdb\\" + county
        arcpy.Merge_management([metro, countypath], metroOut, fieldMappings)
        metro = metroOut
        merge_cnt = merge_cnt + 1
    return metro

# NEW and needs integration
def promptForFoldersForMetro():
    print("Please select the directory containing the metro .ZIP files to be processed:")
    Tk().withdraw() #prevents Tk window from showing up unnecessarily
    file_directory = askdirectory() #opens directory selection dialog
    os.chdir(homedir)
    arcpy.env.workspace = homedir
    metro_counties = os.listdir(file_directory)
    return metro_counties

def promptWhetherMulticounty():
    multicounty = False
    while True:
       ans = raw_input('"Are you using multiple county? Enter Y for yes, or N for no: ')
       yes = 'y'
       no = 'n'
       if ans.lower() == yes :
            multicounty = True
            break
       elif ans.lower() == no:
            multicounty = False
            break
    return multicounty

multicounty2maps = False
logout = None
geoDataBaseName = "2mapsgdb"

if __name__ == '__main__':
    today = str(time.time()).split('.')[0]
    filefilename= "logfile_" + today + ".txt"
    logout = open(filefilename,'w')
    logout.write('main'+ '\n')
    homedir = "C:/2Maps"
    ouputdir = homedir + "\\output"
    arcpy.env.workspace = ouputdir + "\\" + geoDataBaseName

    nearParcelsList = None
    if len(sys.argv) > 1:   # Command line invocation
        nearParcelsList = [] #[sys.argv[1]]
        localParcels = sys.argv[1]
        targetdir = sys.argv[2]
    else:
        nearParcelsList = [arcpy.GetParameterAsText(0)]  # destinations
        localParcels = arcpy.GetParameterAsText(1) # parcels
        targetdir = arcpy.GetParameterAsText(2)

    targetCounty_shp = targetdir + "\\county.shp"
    targetFeatureClass = localParcels.split('.')[0]

    targetParcels = targetdir + "\\parcels.shp"

    outdir = targetdir
    geoDataBaseName = "walk.gdb"
    geoDataBaseOutput = "walkability.gdb"
    creategdb = True
    outputName = "walkability"

    # SETUP
    if creategdb:
        if os.path.isdir(outdir + "\\walk.gdb"):
            gdbfiles = os.listdir(outdir + "\\walk.gdb")
            for gf in gdbfiles:
                os.remove(outdir + "\\walk.gdb\\" + gf)
            gdbfiles2 = os.listdir(outdir + "\\walkability.gdb")
            for gf in gdbfiles:
                os.remove(outdir + "\\walkability.gdb\\" + gf)
            os.remove(outdir + "\\walk.gdb")
            os.remove(outdir + "\\walkability.gdb")
            if os.isfile(outdir + "\\destination.prj"):
                os.remove(outdir + "\\destination.prj")
            if os.isfile(outdir + "\\destination.dbf"):
                os.remove(outdir + "\\destination.dbf")
            if os.isfile(outdir + "\\destination.sbn"):
                os.remove(outdir + "\\destination.sbn")
            if os.isfile(outdir + "\\destination.shp"):
                os.remove(outdir + "\\destination.shp")
            if os.isfile(outdir + "\\destination.shx"):
                os.remove(outdir + "\\destination.shx")
        arcpy.CreateFileGDB_management(outdir, geoDataBaseName)
        arcpy.CreateFileGDB_management(outdir, geoDataBaseOutput)


    workspace = targetdir #+ "/" + geoDataBaseName #"C:/Users/dev/Documents/boundarysolutions/marin/Marin.gdb"
    geoDataBasePath = targetdir + "/" + geoDataBaseName
    geoDataBaseOutputPath = targetdir + "\\" + geoDataBaseOutput
    arcpy.env.workspace = workspace
    logout.write('calling selectDestinations'+ '\n')
    multicounty2maps = promptWhetherMulticounty()

    outCS = arcpy.SpatialReference()
    outCS.factoryCode = 26911
    outCS.create()

    if multicounty2maps:
        countyFolderList = promptForFoldersForMetro()
        for countyfolder in countyFolderList:
            if targetdir.find(countyfolder) == -1:
                nearParcelsList.append(countyfolder + "\\parcels.shp") # might want to rename to parcels_[fip].shp
        newgdbfiles = features2gdb(countyFolderList,outdir,geoDataBaseName)
        merged = loadAndMergeCountiesInMetro(targetParcels,newgdbfiles)
        distinationParcels = selectDestinations(loadAndMergeCountiesInMetro,"distinationParcels") # may not be needed
        #features2gdb(countyFolderList,geoDataBaseName) # may not be needd
        bufferDestinations("distinationParcels","destinationsCommercialBufferedHalf",geoDataBaseName)
        scoreParcels(targetFeatureClass,"destinationsCommercialBufferedHalf", outputName, geoDataBaseName)
    else:
        selectDestinations(nearParcelsList,"distinationParcels")
        logout.write('calling features2gdb'+ '\n')
        features2gdb(geoDataBaseName)
        logout.write('calling bufferDestinations'+ '\n')
        bufferDestinations("distinationParcels","destinationsCommercialBufferedHalf",geoDataBaseName)
        logout.write('calling scoreParcels'+ '\n')
        scoreParcels(targetFeatureClass,"destinationsCommercialBufferedHalf", outputName, geoDataBaseName)

    #logout.write('calling generateLayers'+ '\n')
    #scoreParcelsShape(targetFeatures,nearFeatures, outputName, geoDataBaseName)
    #generateLayers(targetFeatureClass,targetFeatures)