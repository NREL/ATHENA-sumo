import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.dom import minidom
import os


frequency = 300   # how often to generate simulation outputs

beg = 0           # Simulation second when simulation outputs will start being enerated
end_t = 43200     # # Simulation second when simulation outputs will start being enerated 
prefix = ""

# Generate output additonal files for years specified in for loop range() command
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

    # name of output additonal file
    file_name = prefix + "get_edge_out_year_" + year + ".xml"
    # Folder where to save the output additional files
    folder = "../AddFiles/"
    #print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(adds)).toprettyxml(encoding="utf-8"))
