import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.dom import minidom
import os

subfolder = "tenPctMedium/"

for year in range(0,29):
    
    year = str(int(year))
    fp = "../output/" + subfolder
    pathToEdgeFile = fp + "year_" + year + "_edges_out.xml"
    pathToEmissionsFile = fp + "year_" + year + "_edge_emmisions.xml"

    adds = Element("additional")

    edgeCongestionElem = Element("edgeData")
    edgeCongestionElem.set("id", "congestion")
    edgeCongestionElem.set("file", pathToEdgeFile)
    edgeCongestionElem.set("freq", "1800")
    edgeCongestionElem.set("begin", "1800")
    edgeCongestionElem.set("end", "86400")
    edgeCongestionElem.set("excludeEmpty", "true")

    edgeEmissionElem = Element("edgeData")
    edgeEmissionElem.set("id", "emission")
    edgeEmissionElem.set("type", "emissions")
    edgeEmissionElem.set("freq", "1800")
    edgeEmissionElem.set("begin", "1800")
    edgeEmissionElem.set("end", "86400")
    edgeEmissionElem.set("file", pathToEmissionsFile)
    edgeEmissionElem.set("excludeEmpty", "true")

    adds.append(edgeCongestionElem)
    adds.append(edgeEmissionElem)

    file_name = "get_edge_out_year_" + year + ".xml"
    folder = "AddFiles/"
    #print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(adds)).toprettyxml(encoding="utf-8"))
