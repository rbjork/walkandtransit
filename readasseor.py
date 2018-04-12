import os
import dbf
import shapefile as shp
import subprocess

import xml.etree.ElementTree as ET

def joinShp2Shp(shapetarget,shapejoin,path2files,input_vrt):  # need input_vrt
    path = homepath + path2files
    os.chdir(path2files)
    args = ['ogr2ogr','-sql','SELECT t.*, j.SA_LGL_DSCRPTN from Parcels t, parcelsassessor j WHERE ST_INTERSECTS(t.geometry,n.geometry)','-dialect','SQLITE','output.shp',input_vrt]
    subprocess.check_call(args)
    os.chdir(homedir)

def spatialJoin():
    pass

def correctLongitudeSign(inputfile):
    fp = open(homepath + inputfile,'r')
    fptemp = open(homepath + "temp.txt",'w')
    try:
        i = 0
        for line in fp:
            i = i + 1
            if i < 2:
                fptemp.write("APN_ADDED,LGL_DSCRPT,LOT_SIZE,XCOORD,YCOORD\n")
                continue
            txtlineFields = line.split(',')
            longitude = str(-float(txtlineFields[3]))
            data = txtlineFields[0] + "," + txtlineFields[1] + "," + txtlineFields[2] + "," + longitude + "," + txtlineFields[4]
            fptemp.write(data)
    except Exception as e:
        print e.message
    fp.close()
    fptemp.close()
    os.remove(homepath + inputfile)
    os.rename(homepath + "temp.txt",homepath + inputfile)

def csv2shp(inputfile,state,county,fip):
    print "called csv2shp"
    #os.mkdir("my_dir")
    vrtfiletemplate = "vrt.xml"
    tree = ET.parse(vrtfiletemplate)
    root = tree.getroot()
    layer = root.find('OGRVRTLayer')
    featureName = inputfile.split('.')[0]
    layer.name = featureName
    element = layer.find('SrcDataSource')
    element.text = inputfile
    element2 = layer.find('SrcLayer')
    element2.text = featureName
    os.chdir(fip)
    tree.write(county+".vrt")
    args1 = ['ogr2ogr','-f',"ESRI Shapefile",".", inputfile]
    args2 = ['ogr2ogr','-f',"ESRI Shapefile",'-overwrite',".",county+".vrt"]
    subprocess.check_call(args1)
    subprocess.check_call(args2)
    os.chdir(homedir)

def createPointShapefile(shpfile):  # just like csv2Shape
    fp = open(homepath + "Boundary Solutions_TaxAssessor_008.tab")
    path = homepath
    dbffilename = "samplertdata.dbf"
    w = shp.Writer(shp.POINT)
    tabledbf = dbf.Table(path + dbffilename,'SA_LGL_DSCRPTN C(200);  xcoord N(14,8);  ycoord N(14,8)')
    tabledbf.open()
    attrlist = []
    try:
        for line in fp:
            i = i + 1
            txtlineFields = line.split('\t')
            lat = float(txtlineFields[179])
            long = float(txtlineFields[180])
            w.point(lat,long)
            w.field("xcoord","C","15")
            w.field("ycoord","C","15")
            data = (txtlineFields[67],lat,long)
            tabledbf.append(data)
            #attrlist.append(data)
            if i % 100000  == 0:
                print txtlineFields[179],txtlineFields[180]
        print "Completed ",i
    except:
        print "Failed at ",i
    w.saveShp(path+shpfile)
    print len(attrlist)


def getDataOfInterest(filename, state, county, outfile,append):
    path = homepath
    dbffilename = "samplertdata.dbf"
    fp = open(homepath + filename)
    if append:
        fpout = open(homepath + outfile,'a')
    else:
        fpout = open(homepath + outfile,'w')
        fpout.write("APN_ADDED,LGL_DSCRPT,LOT_SIZE,XCOORD,YCOORD\n")
    #tabledbf = dbf.Table(path + dbffilename,'SA_LGL_DSC C(255); xcoord N(14,8); ycoord N(14,8)')
    #tabledbf.open()
    i = 0
    j = 0
    for line in fp:
        try:
            j = j + 1
            txtlineFields = line.split('\t')
            txtState = txtlineFields[2].lower()
            txtCounty = txtlineFields[6].lower()
            if j % 10000 == 0:
                print txtState,txtCounty
            if txtCounty == state:
                print "have",txtCounty
            if txtState == state and (txtCounty == county or county == 'all'):
                i = i + 1
                lgl = txtlineFields[67].replace(',','|')
                longitude = str(-float(txtlineFields[179]))
                data = txtlineFields[0] + "," + lgl + "," + txtlineFields[146] + "," + longitude + "," + txtlineFields[180]
                fpout.write(data + '\n')
                if i % 100 == 0:
                    print txtState,txtCounty
                    print data
        except Exception as e:
            print "Failed at ",i, e.message
    fpout.close()
    fp.close()


def getsample(filename):
    path = homepath
    dbffilename = "samplertdata.dbf"
    fp = open(homepath + filename)
    fpout = open(homepath + "outputlgldescription.txt",'w')
    #tabledbf = dbf.Table(path + dbffilename,'record C(10);SA_LGL_DSC C(255)')
    #tabledbf.open()
    i = 0
    fpout.write("APN,LGL_DSCRPT,LOT_SIZE,XCOORD,YCOORD")
    for line in fp:
        try:
            i = i + 1
            txtlineFields = line.split('\t')
            lgl = txtlineFields[67].replace(',','|')
            data = txtlineFields[0] + "," + lgl + "," + txtlineFields[146] + "," + txtlineFields[179] + "," + txtlineFields[180]
            if i % 50000 == 0:
                print data
                #tabledbf.append(data)
                fpout.write(data + '\n')
        except Exception as e:
            print "Failed at ",i, e.message
    fpout.close()
    fp.close()

def buildcsv(state,county,outputfile):
    getDataOfInterest("Boundary Solutions_TaxAssessor_001.txt",state,county,outputfile,False)
    getDataOfInterest("Boundary Solutions_TaxAssessor_002.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_003.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_004.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_005.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_006.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_007.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_008.txt",state,county,outputfile,True)
    getDataOfInterest("Boundary Solutions_TaxAssessor_009.txt",state,county,outputfile,True)

if __name__ == '__main__':
    homedir = os.getcwd()
    homepath = homedir + "\\"
    print "Start"
    #getsample("Boundary Solutions_TaxAssessor_008.tab")
    state = "nh"
    county = "all"
    outputfile = county + "_" + state + ".csv"
    fip = "06041"
    buildcsv(state,county,outputfile)
    correctLongitudeSign(outputfile)
    csv2shp(outputfile,state,county,fip)
    #joinShp2Shp("Parcels","parcelsassessor",homepath + fip)






