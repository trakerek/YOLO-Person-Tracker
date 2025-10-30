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
