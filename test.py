import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

def on_button_clicked():
    print("Hello, World!")

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle('Simple Test')

button = QPushButton('Click Me!', window)
button.clicked.connect(on_button_clicked)
button.move(50, 50)

window.setGeometry(100, 100, 300, 200)
window.show()

sys.exit(app.exec_())