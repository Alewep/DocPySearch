import os

DOCUMENTS = "./Documents/"

files = [f for f in os.listdir(DOCUMENTS) if os.path.join(DOCUMENTS, f)]
for filename in files:
    with open(DOCUMENTS + filename, "r+") as file:
        newcontent = file.read()
        if newcontent.strip()[0:6] != "<DOCS>":
            newcontent = "<DOCS>\n" + newcontent
        if newcontent.strip()[-7:] != "</DOCS>":
            newcontent = newcontent + "\n</DOCS>"
        file.seek(0, 0)
        file.write(newcontent)
