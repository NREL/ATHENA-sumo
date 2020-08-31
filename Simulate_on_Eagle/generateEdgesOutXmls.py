import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.dom import minidom
import os


frequency = 300

beg = 0
end_t = 43200
prefix = str(end_t)+'_'

for year in range(27,28):
    
    year = str(int(year))
    fp = "../output/"
    pathToEdgeFile = fp + prefix + "year_" + year + "_edges_out.xml"
    pathToEmissionsFile = fp + prefix +  "year_" + year + "_edge_emmisions.xml"

    adds = Element("additional")

    edgeCongestionElem = Element("edgeData")
    edgeCongestionElem.set("id", "congestion")
    edgeCongestionElem.set("file", pathToEdgeFile)
    edgeCongestionElem.set("freq", str(frequency))
    edgeCongestionElem.set("begin", str(beg))
    edgeCongestionElem.set("end",str(end_t))
    edgeCongestionElem.set("excludeEmpty", "true")

    edgeEmissionElem = Element("edgeData")
    edgeEmissionElem.set("id", "emission")
    edgeEmissionElem.set("type", "emissions")
    edgeEmissionElem.set("freq", str(frequency))
    edgeEmissionElem.set("begin", str(beg))
    edgeEmissionElem.set("end", str(end_t))
    edgeEmissionElem.set("file", pathToEmissionsFile)
    edgeEmissionElem.set("excludeEmpty", "true")

    adds.append(edgeCongestionElem)
    adds.append(edgeEmissionElem)

    file_name = prefix + "get_edge_out_year_" + year + ".xml"
    folder = "../AddFiles/"
    #print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(adds)).toprettyxml(encoding="utf-8"))
