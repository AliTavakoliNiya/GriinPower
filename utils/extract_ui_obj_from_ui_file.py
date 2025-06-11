from bs4 import BeautifulSoup
import pandas as pd



# Load and parse the Qt Designer .ui file
file_path = "D:/GriinPower/ui/project/project_information_tab.ui"
with open(file_path, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "xml")

# Extract all objects with their class and name
widgets = []
for widget in soup.find_all("widget"):
    class_name = widget.get("class")
    name = widget.get("name")
    if class_name and name:
        widgets.append(( "self." + name, class_name))

df = pd.DataFrame(widgets)
df
df.to_csv(file_path.replace(".ui", ".csv"), index=False)




