from PyQt5.QtWidgets import QProgressBar, QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen, QCursor, QMouseEvent
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
import sys
import httpx  # Asegúrate de importar httpx
from io import BytesIO
import time


htb_user_api = 'https://www.hackthebox.com/api/v4/user/info'
htb_api_token = ''  # Reemplaza con tu token
filename = 'pos.txt'

# Abrir el archivo y leer su contenido
try:
    with open(filename, 'r') as file:
        # Leer el contenido del archivo
        contenido = file.read().strip()  # Eliminar espacios en blanco
        # Dividir la cadena por la coma y convertir a enteros
        x_str, y_str = contenido.split(',')  # Sin espacios
        x = int(x_str)
        y = int(y_str)
        print(x)
        print(y)

except FileNotFoundError:
            print(f"El archivo {filename} no fue encontrado.")
except ValueError:
            print("Error al procesar las coordenadas. Asegúrate de que estén en el formato correcto.")

# Mostrar el contenido
print(contenido)

with httpx.Client() as client:
    # Configurar los headers para la petición HTTP
    headers = {
        "User-Agent": "HTB Info Script",
        "Authorization": f"Bearer {htb_api_token}"
    }

    # Realizar la petición para obtener la información del usuario
    response_user = client.get(htb_user_api, headers=headers)

    # Comprobar si la respuesta es correcta (HTTP 200)
    if response_user.status_code == 200:
        data = response_user.json()
        user_id = data ['info']['id']
        user_name = data['info']['name']
        user_avatar = data['info']['avatar']
        user_team_name = data['info']['team']['name'] if data['info']['team'] else "No team"
        user_avatar_url = f"https://www.hackthebox.com{user_avatar}"

        print(f"URL del avatar: {user_avatar_url}")  # Mensaje de depuración

        # Descargar la imagen del avatar con encabezados de autenticación
        avatar_response = client.get(user_avatar_url, headers=headers)
        if avatar_response.status_code == 200:
            # Guardar la imagen localmente como 'avatar.png'
            with open("avatar.png", "wb") as f:
                f.write(avatar_response.content)
        else:
            print(f"Error al descargar la imagen del avatar. Código de estado: {avatar_response.status_code}")
    else:
            print(f"Error al descargar la imagen del avatar. Código de estado: {avatar_response.status_code}")
    htb_user_profile = f"https://www.hackthebox.com/api/v4/profile/{user_id}"
    response_user_profile = client.get(htb_user_profile, headers=headers)
    print(response_user_profile)

    if response_user_profile.status_code == 200:
        data = response_user_profile.json()
        
        user_rank = data['profile']['rank']
        user_points = data['profile']['points']
        user_system_owns = data['profile']['system_owns']
        user_user_owns = data['profile']['user_owns']
        user_rank_progress = data['profile']['current_rank_progress']
        user_team = data['profile']['team']['id']
        user_ranking = data['profile']['ranking']

    else:
            print(f"Error.")

    # Active Machine Info
    htb_active_machine = f"https://www.hackthebox.com/api/v4/machine/active"
    response_active_machine = client.get(htb_active_machine, headers=headers)

    if response_active_machine.status_code == 200:
        data = response_active_machine.json()
        if data['info'] is None:
            machine_name = "Disconnected"
        else:
            machine_name = data['info']['name']
    else:
            print(f"Error al descargar la imagen del avatar. Código de estado: {avatar_response.status_code}")                              
    
    # Team Info
    htb_team_info = f"https://www.hackthebox.com/api/v4/team/info/{user_team}"

class RoundImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap()
        self.image_size = 40  # Cambiar el tamaño de la imagen si es necesario
        self.border_color = Qt.green
        self.border_width = 1

    def setPixmap(self, pixmap):
        self.pixmap = pixmap.scaled(self.image_size, self.image_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.setBrush(QBrush(self.pixmap))
        painter.drawEllipse(rect)
        pen = QPen(self.border_color, self.border_width)
        painter.setPen(pen)
        painter.drawEllipse(rect)

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(380, 280)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Hace que el fondo del diálogo sea transparente
        # Efecto de opacidad para la ventana
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Inicialmente, la ventana será completamente invisible
        self.opacity_effect.setOpacity(0)
        # Configurar el fondo con una imagen de banner
        self.banner_label = QLabel(self)
        self.banner_label.setPixmap(QPixmap(""))  # Cambia el nombre de archivo por tu imagen de banner
        self.banner_label.setScaledContents(False)  # Asegura que la imagen escale
        self.banner_label.setGeometry(0, 0, self.width(), 110)  # Ajusta el tamaño del banner
        self.banner_label.setStyleSheet("background-color: transparent;borders-radius:10px; height:10px;border: white;")


        # Configurar el fondo con una imagen
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap("background.png"))  # Cambia el nombre de archivo por tu imagen de fondo
        self.background_label.setScaledContents(True)  # Asegura que la imagen escale
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.banner_label.raise_()
        # Estilo del contenedor
        self.setStyleSheet("background-color: rgba(0, 27, 46, 0.5); border: none;")  # Fondo transparente

        self.image_label = RoundImageLabel(self)
        self.image_label.setPixmap(QPixmap("avatar.png"))  # Cambia el nombre de archivo por tu imagen de perfil
        self.image_label.setFixedSize(40, 40)  # Asegúrate de que el tamaño sea el mismo que image_size en RoundImageLabel
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent;font-size: 14px; color: #fff; margin-top: 10px;")


        self.name_label = QLabel(f"{user_name}", self)
        self.name_label.setStyleSheet("background-color: transparent;font-size: 15px; font-weight: bold; color: #6ADF04;")  # Cambié el color a blanco para que resalte en el banner
        self.location_label = QLabel(f"{user_team_name}  |  {user_rank}", self)
        self.location_label.setStyleSheet("background-color: transparent;font-size: 12px; color: #fff;")  # Cambié el color a blanco para que resalte en el banner

        self.bio_label = QLabel(f"""
            <div style="text-align: center; margin-right: 20px;background-color: transparent">
            <b style="color:#6ADF04;font-size: 12px;text-shadow: 1px 1px 2px black;"> System Owns</b><br>
            <span style="color: white; font-size: 12px;">{user_system_owns}</span>
            </div>
        """, self)
        self.bio_label.setWordWrap(True)
        self.bio_label.setStyleSheet("background-color: transparent;font-size: 14px; color: #fff; margin-top: 10px;")
        
        self.bio2_label = QLabel(f"""
            <div style="text-align: center; margin-right: 20px;">
            <b style="color:#6ADF04;font-size: 12px;"> User Owns</b><br>
            <span style="color: white; font-size: 12px;">{user_user_owns}</span>
            </div>
        """, self)
        self.bio2_label.setWordWrap(True)
        self.bio2_label.setStyleSheet("background-color: transparent;font-size: 14px; color: #fff; margin-top: 10px;")

        self.bio3_label = QLabel(f"""
            <div style="text-align: center; margin-right: 20px;">
            <b style="color:#6ADF04;font-size: 12px;text-shadow: 1px 1px 2px black;">󰮊 User Points</b><br>
            <span style="color: white; font-size: 12px;">{user_points}</span>
            </div>
        """, self)
        self.bio3_label.setWordWrap(True)
        self.bio3_label.setStyleSheet("background-color: transparent;font-size: 14px; color: #fff; margin-top: 10px;")

        self.bio4_label = QLabel(f"""
            <div style="text-align: center; margin-right: 20px;">
            <b style="color:#6ADF04;font-size: 12px;text-shadow: 1px 1px 2px black;">󰔸.Ranking</b><br>
            <span style="color: white; font-size: 12px;">{user_ranking}</span>
            </div>
        """, self)
        self.bio4_label.setWordWrap(True)
        self.bio4_label.setStyleSheet("background-color: transparent;font-size: 14px; color: #fff; margin-top: 10px;")


        self.machine_label = QLabel(f"""
            <div style="text-align: center; margin-right: 20px;">
            <b style="color:#6ADF04;font-size: 12px;text-shadow: 1px 1px 2px black;"> Active Machine</b><br>
            <span style="color: white; font-size: 12px;">{machine_name}</span>
            </div>
        """, self)
        self.machine_label.setWordWrap(True)
        self.machine_label.setStyleSheet("background-color:transparent;font-size: 14px; color: #fff; margin-top: 10px;")
    
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 150, 280, 30)  # Ajusta la posición y tamaño según sea necesario
        self.progress_bar.setRange(0, 100)  # Rango de 0 a 100
        self.progress_bar.setValue(0)  # Valor inicial

        self.follow_button = QPushButton("CLOSE", self)
        self.follow_button.setStyleSheet("margin-top:10px;width:40px;height:10px;background-color: #6ADF04; color: #265E00; font-size: 10px; border: none; border-radius: 5px; padding: 5px;")
        self.follow_button.clicked.connect(self.close)
        # Layouts
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.name_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.location_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)


                # Crear un QHBoxLayout para las bio_labels
        bio_layout = QHBoxLayout()
        bio_layout.addWidget(self.bio_label, alignment=Qt.AlignCenter)
        bio_layout.addWidget(self.machine_label, alignment=Qt.AlignCenter)
        bio_layout.addWidget(self.bio2_label, alignment=Qt.AlignCenter)
        

        main_layout.addLayout(bio_layout)
        layout = QVBoxLayout(self)
        layout.addWidget(self.follow_button)
        # Segundo QHBoxLayout para la nueva fila de widgets
        second_bio_layout = QHBoxLayout()
        second_bio_layout.addWidget(self.bio3_label, alignment=Qt.AlignCenter)  # Añade aquí tus widgets
        second_bio_layout.addWidget(self.bio4_label, alignment=Qt.AlignCenter)  # Añade aquí tus widgets

        # Agregar el segundo QHBoxLayout al QVBoxLayout principal
        main_layout.addLayout(second_bio_layout)
        main_layout.addWidget(self.follow_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)

        print("test")
                # Temporizador para mover el diálogo
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_dialog)

        # Iniciar el temporizador para que se ejecute cada 100 ms
        self.timer.start(100)

        # Crear otro temporizador para detener el movimiento después de 1 segundo
        self.stop_timer = QTimer()
        self.stop_timer.setSingleShot(True)  # Solo se ejecuta una vez
        self.stop_timer.timeout.connect(self.stop_moving)

        # Iniciar el temporizador que detiene el movimiento después de 1 segundo
        self.stop_timer.start(500)  # Detener después de 1 segundos
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #6ADF04;  /* Color del borde */
                border-radius: 5px;         /* Bordes redondeados */
                background-color: rgba(255, 255, 255, 0.2);  /* Color de fondo de la barra */
                height:10px;text-align:center;width:200px;font-size:10px;
            }
            QProgressBar::chunk {
                background-color: #6ADF04;   /* Color del progreso */
                border-radius: 3px;          /* Bordes redondeados para la parte de progreso */
            }
        """)
        self.update_progress(user_rank_progress)

    def update_progress(self, percentage):

        self.progress_bar.setValue(int(percentage))

    def move_dialog(self):
        # Obtener la posición actual del cursor
        cursor_pos = QCursor.pos()
        print("Posicion actual de cursor:")
        print(cursor_pos)
        # Mover el diálogo a la nueva posición del cursor
        self.move(x - 180,y + 30)
        time.sleep(0.2)
                # Animación de opacidad (de 0 a 1 en 2 segundos)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)  # Duración de 2 segundos

        self.animation.setEndValue(1)
        self.animation.start()
    def stop_moving(self):
        # Detener el temporizador de movimiento
        self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = CustomDialog()
    print("1")
    # Ejecutar el diálogo
    dialog.exec_()

