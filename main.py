import sys
from PySide6.QtWidgets import QApplication
from pet import Pet

app = QApplication(sys.argv)

pet = Pet()
pet.show()

sys.exit(app.exec())