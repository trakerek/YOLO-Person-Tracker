🧠 Nazwa projektu

YOLO Person Tracker — System Śledzenia Osób z Sterowaniem Serwomechanizmów

📄 Opis projektu

Ten projekt łączy sztuczną inteligencję (YOLOv11) z mikrokontrolerem Arduino, aby stworzyć inteligentny system śledzenia osób w czasie rzeczywistym.
Za pomocą kamery (lub zestawu dwóch kamer) oraz modelu YOLO system wykrywa ludzi w obrazie, określa ich pozycję, a następnie przesyła współrzędne do Arduino przez port serial, gdzie dwa serwomechanizmy fizycznie podążają za wykrytą osobą.

Projekt ma dwa główne warianty:

🧩 1️⃣ YOLO Stereo Tracker (dwie kamery)

Plik: stereo_tracker.py

Wykorzystuje dwie kamery (obraz łączony poziomo) do estymacji odległości osoby od kamery.

Oblicza dysparację (różnicę pozycji między kamerami), aby przybliżyć dystans w metrach.

Śledzi wykrytą osobę w przestrzeni 2D oraz oblicza odległość w 3D.

Wysyła współrzędne (x, y) do Arduino, które steruje serwomechanizmami — np. obracając głowicę kamery w kierunku osoby.

Dodatkowo zawiera wygładzanie ruchu i ograniczenie częstotliwości wysyłania danych przez port szeregowy.

Główne funkcje:

Detekcja ludzi przez model YOLOv11n

Estymacja głębi (odległość w metrach)

Resetowanie trackera w określonych interwałach

Serial komunikacja z Arduino

Płynne śledzenie pozycji celu

🧩 2️⃣ YOLO Single-Cam Tracker (jedna kamera)

Plik: single_cam_tracker.py

Używa pojedynczej kamery USB (np. /dev/video4).

Wykrywa ludzi w czasie rzeczywistym i śledzi ich przy pomocy algorytmu SORT.

Określa współrzędne środka sylwetki i przesyła je do Arduino.

Dodatkowo szacuje odległość na podstawie wysokości obiektu w pikselach.

System może działać nawet bez drugiej kamery (prostsza konfiguracja).

Główne funkcje:

Wykrywanie i śledzenie osób

Wygładzanie pozycji (filtr eksponencjalny)

Obliczanie przybliżonej odległości

Komunikacja przez port szeregowy

Stabilne sterowanie serwami

⚙️ Arduino — sterowanie serwomechanizmami

Plik: servo_controller.ino

Arduino odbiera współrzędne (x, y) przesyłane przez Python i zamienia je na ruch dwóch serw:

Oś X — obrót poziomy (lewo/prawo)

Oś Y — obrót pionowy (góra/dół)

Dodatkowo:

Obsługuje joystick (manualna korekta i reset pozycji),

Zawiera płynny ruch serw (bez gwałtownych skoków),

Ogranicza zakres ruchu (0–180°),

Automatycznie mapuje współrzędne z przestrzeni pikselowej (np. 1920×1080) na kąt serwa.

🔌 Wymagania
🖥️ PC / Jetson / Raspberry Pi:

Python 3.8+

CUDA (jeśli używasz GPU)

Zainstalowane biblioteki:
    pip install ultralytics opencv-python pyserial filterpy numpy

⚡ Arduino:

    Arduino UNO / Nano / Mega

    Biblioteka Servo.h (wbudowana)

    Dwa serwomechanizmy (np. SG90)

    Joystick (2 analogowe + przycisk)

🧭 Sposób uruchomienia
1️⃣ Wersja z jedną kamerą:

python3 single_cam_tracker.py

2️⃣ Wersja stereo:

python3 stereo_tracker.py

3️⃣ Po stronie Arduino:

    Otwórz servo_controller.ino w Arduino IDE.

    Wgraj kod na płytkę.

    Połącz Arduino z komputerem przez USB (np. /dev/ttyACM0).

    Upewnij się, że port COM jest ten sam co w skryptach Python.

📊 Zasada działania

    YOLO wykrywa osobę w kadrze.

    Skrypt wylicza środek wykrytego obiektu (lub jego średnią z wielu detekcji).

    Wynikowe współrzędne (x, y) są wysyłane do Arduino przez port szeregowy.

    Arduino przelicza wartości na kąty serw i obraca je w odpowiednim kierunku.

    Jeśli w wersji stereo — system dodatkowo oblicza odległość w metrach.

🎥 Efekt działania

    Kamera lub głowica porusza się automatycznie, podążając za osobą w czasie rzeczywistym.

    W wersji stereo kamera może reagować również na przybliżanie/oddalanie obiektu.

🧠 Możliwe rozszerzenia

    Wykrywanie twarzy lub konkretnych obiektów (np. classes=[0, 67]).

    Zastosowanie lepszego modelu YOLO (np. yolov11s.pt).

    Automatyczne sterowanie zoomem kamery.

    Wysyłanie danych o odległości na ekran LCD.

    Zapis ścieżki ruchu obiektu.

📸 Autor

Twój Nick / Imię i Nazwisko
(dopisz swój kontakt, jeśli chcesz)
