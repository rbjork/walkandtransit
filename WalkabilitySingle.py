import arcpy,os,sys

def selectDestinations(destinations,outputName,workspace):
    print "selectDestinations"
    #arcpy.env.workspace = arcpy.GetParameterAsText(0)

    expression1 = 'NOT "STD_LAND_U" = \'RAPT\' AND NOT "STD_LAND_U" = \'RSFR\' AND NOT "STD_LAND_U" = \'RCON\' AND NOT "STD_LAND_U" = \'RCOO\' AND NOT "STD_LAND_U" = \'RDUP\' AND NOT "STD_LAND_U" = \'RMOB\' AND NOT "STD_LAND_U" = \'RMSC\' AND NOT "STD_LAND_U" = \'RQUA\' AND NOT "STD_LAND_U" = \'RSFR\' AND NOT "STD_LAND_U" = \'RTIM\' AND NOT "STD_LAND_U" = \'RTRI\' AND NOT "STD_LAND_U" = \'RMFD\''
    expression2 = '"IMPR_VALUE" > \'0\''
    expression3 = '"OWNER" LIKE \'%PARK%\' OR "OWNER" LIKE \'%RECREATION%\'  OR "OWNER" LIKE \'%TOWN%\'  OR "OWNER" LIKE \'%COUNTY%\'  OR "OWNER" LIKE \'%STATE%\'  OR "OWNER" LIKE \'%DISTRICT%\' OR "OWNER" LIKE \'%SCHOOL%\'  OR "OWNER" LIKE \'%ELEMENTARY%\'  OR "OWNER" LIKE \'%MIDDLE%\'  OR "OWNER" LIKE \'%LIBRARY%\'  OR "OWNER" LIKE \'%K8 K12%\'  OR "OWNER" LIKE \'%HOSPITAL%\' OR "OWNER" LIKE \'%CIVIC%\'  OR "OWNER" LIKE \'%CLINIC%\'  OR "OWNER" LIKE \'%FACILITY%\' OR "OWNER" LIKE \'%COMMUNITY%\'  OR "OWNER" LIKE \'%PLAYGROUND%\' OR "OWNER" LIKE \'%CHURCH%\'  OR "OWNER" LIKE \'%TEMPLE%\'  OR "OWNER" LIKE \'%MOSQUE%\' OR "OWNER" LIKE \'%FOREST%\'  OR "OWNER" LIKE \'%MUNICIPAL%\' OR "OWNER" LIKE \'%UNIVERSITY%\'  OR "OWNER" LIKE \'%DAYCARE%\''

    # Within selected features, further select based on a SQL query within the script tool
    arcpy.MakeFeatureLayer_management(destinations, "destLyr")
    arcpy.SelectLayerByAttribute_management("destLyr", "NEW_SELECTION", expression1)
    arcpy.SelectLayerByAttribute_management("destLyr", "SUBSET_SELECTION", expression2)
    arcpy.SelectLayerByAttribute_management("destLyr", "ADD_TO_SELECTION", expression3)

    # Write the selected features to a new featureclass
    arcpy.CopyFeatures_management("destLyr", workspace + "\\" + str(outputName))

#arcpy.Buffer_analysis("C:/Users/dev/Documents/boundarysolutions/marin/commercial.shp", "C:/Users/dev/Documents/boundarysolutions/marin/commercialBufferedHalf.shp","2640 Feet")

def features2gdb(inWorkspace,outWorkspace):
    arcpy.env.workspace = inWorkspace
    print "features2gdb"
    for fc in arcpy.ListFeatureClasses():
        print "fc", fc
        arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)

def bufferDestinations(destinations,bufferedName, geoDataBaseName):
    print "bufferDestinations"
    arcpy.Buffer_analysis(homedir + "\\" + geoDataBaseName + "\\" + destinations, homedir + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")

def scoreParcels(targetFeature,nearFeature, outputName, geoDataBaseName):
    print "scoreParcels"
    in_file1 = homedir + "\\" + geoDataBaseName + "\\" + targetFeature
    in_file2 = homedir + "\\" + geoDataBaseName + "\\" +nearFeature
    output_file = homedir + "\\" + geoDataBaseName + "\\" +"targetFeatureScored"
    arcpy.SpatialJoin_analysis(in_file1, in_file2, output_file, "JOIN_ONE_TO_ONE", "KEEP_COMMON",None, "INTERSECT", "", "")
    #arcpy.SpatialJoin_analysis(homedir + "\\" + geoDataBaseName + "\\" + targetFeature, homedir + "\\" + geoDataBaseName + "\\" +nearFeature, homedir + "\\" + geoDataBaseName + "\\" +"targetFeatureScored")
    arcpy.AddField_management(homedir + "\\" +geoDataBaseName + "\\" + "targetFeatureScored", "walkability", "SHORT")
    expression = "getScore(int(!Join_Count!))"
    codeblock = """def getScore(cnt):
    if cnt <= 30:
        return 1
    if cnt > 31 and cnt <= 70:
        return 2
    if cnt > 71 and cnt <= 110:
        return 3
    if cnt > 111 and cnt <= 135:
        return 4
    if cnt > 135:
        return 5
    else:
        return 0"""
    arcpy.CalculateField_management(homedir + "\\" +geoDataBaseName + "\\" + "targetFeatureScored", "walkability", expression,"PYTHON_9.3",codeblock)

def scoreParcelsDW(targetFeature,nearFeature, outputName, geoDataBaseName):
    print "scoreParcels"
    in_file1 = homedir + "\\" + geoDataBaseName + "\\" + targetFeature
    in_file2 = homedir + "\\" + geoDataBaseName + "\\" +nearFeature
    output_file = homedir + "\\" + geoDataBaseName + "\\" +"targetFeatureScored"
    arcpy.SpatialJoin_analysis(in_file1, in_file2, output_file, "JOIN_ONE_TO_ONE", "KEEP_COMMON",None, "WITHIN_A_DISTANCE", "2640 Feet", "")
        #arcpy.SpatialJoin_analysis(homedir + "\\" + geoDataBaseName + "\\" + targetFeature, homedir + "\\" + geoDataBaseName + "\\" +nearFeature, homedir + "\\" + geoDataBaseName + "\\" +"targetFeatureScored")
    arcpy.AddField_management(homedir + "\\" +geoDataBaseName + "\\" + "targetFeatureScored", "walkability", "SHORT")
    expression = "getScore(int(!Join_Count!))"
    codeblock = """def getScore(cnt):
    if cnt <= 30:
        return 1
    if cnt > 31 and cnt <= 70:
        return 2
    if cnt > 71 and cnt <= 110:
        return 3
    if cnt > 111 and cnt <= 135:
        return 4
    if cnt > 135:
        return 5
    else:
        return 0"""
    arcpy.CalculateField_management(homedir + "\\" +geoDataBaseName + "\\" + "targetFeatureScored", "walkability", expression,"PYTHON_9.3",codeblock)


def removeFields(fc,workspace):
    print "removeFields called"
    try:
        arcpy.env.workspace = workspace
        arcpy.DeleteField_management(fc, "APN2;STATE;COUNTY;FIPS;SIT_HSE_NU;SIT_DIR;SIT_STR_NA;SIT_STR_SF;SIT_FULL_S;SIT_CITY;SIT_STATE;SIT_ZIP;SIT_ZIP4;SIT_POST;LAND_VALUE;TOT_VALUE;ASSMT_YEAR;MKT_LAND_V;MKT_IMPR_V;TOT_MKT_VA;MKT_VAL_YR;REC_DATE;SALES_PRIC;SALES_CODE;YEAR_BUILT;CONST_TYPE;BEDROOMS;BATHROOMS;OWNADDRES2;OWNCTYSTZP")
    except:
        print "Remove done already for county "

def removeFields2(county,parcelsFC):
    print "removeFields2 called"
    arcpy.env.workspace = homedir + "\\walk2.gdb"
    try:
        fc = parcelsFC
        arcpy.DeleteField_management(fc, "IMPR_VALUE;STD_LAND_U;BLDG_AREA;OWNER;OWNER2;OWNADDRESS;")
    except:
        print "Remove done already for county ",county

def generateLayers(targetFeatureClass,targetFeature):
    print "generateLayers"
    # arcpy.Split_analysis("Habitat_Analysis.gdb/vegtype", "climate.shp", "Zone","C:/output/Output.gdb", "1 Meters")
    arcpy.Split_analysis(homedir + "\\" +geoDataBaseName +  "/" + "targetFeatureScored", homedir + "\\" +geoDataBaseName +  "/" + "targetFeatureScored", "walkability", geoDataBasePath)


if __name__ == '__main__':

    homedir = os.getcwd() #"C:/2Maps"
    outdir = homedir
    geoDataBaseName = "walk2.gdb"
    workspace = homedir #+ "/" + geoDataBaseName #"C:/Users/dev/Documents/boundarysolutions/marin/Marin.gdb"
    geoDataBasePath = homedir + "/" + geoDataBaseName



    if len(sys.argv) > 1:   # Command line invocation
        nearFeatures = sys.argv[1]
        targetFeatures = sys.argv[2]
        #homedir = sys.argv[3]
    else:
        nearFeatures = arcpy.GetParameterAsText(0)  # destinations
        targetFeatures = arcpy.GetParameterAsText(1) # parcels
        homedir = arcpy.GetParameterAsText(2)

    targetFeatureClass = targetFeatures.split('.')[0] #+ '_shp'


    creategdb = False
    outputName = "walkability"

    # TEST
    #scoreParcels(targetFeatureClass,"destinationsCommercialBufferedHalf", outputName, geoDataBaseName)
    # End TEST

    if creategdb:
        arcpy.CreateFileGDB_management(outdir, geoDataBaseName)



    workspace = homedir + "\\data\\06085"
    arcpy.env.workspace = workspace
    '''
    removeFields("Parcels.shp",workspace)
    selectDestinations(nearFeatures,"destinations",workspace)
    removeFields2("destinations",workspace)
    removeFields2("Parcels",workspace)
    features2gdb(homedir + "\\data\\06085" ,homedir + "\\" + geoDataBaseName)
    '''
    #bufferDestinations("destinations","destinationsCommercialBufferedHalf",geoDataBaseName)
    #scoreParcels(targetFeatureClass,"destinationsCommercialBufferedHalf", outputName, geoDataBaseName)
    scoreParcelsDW(targetFeatureClass,"destinations", outputName, geoDataBaseName)
    #generateLayers(targetFeatureClass)
