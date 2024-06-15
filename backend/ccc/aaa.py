import jpype
import asposecells
jpype.startJVM()
from asposecells.api import Workbook

# Create an instance of the Workbook class.
workbook = Workbook()

# Insert the words Hello World! into a cell accessed.
workbook.getWorksheets().get(0).getCells().get("A1").putValue("Hello World")

# Save as XLSX file
workbook.save("output.xlsx")


jpype.shutdownJVM()