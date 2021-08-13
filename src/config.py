import os

small_font_family = "Sans-serif"
small_font_size = 8

telemetry = {
    "Alt (m)": (0, 2, 10),
    "Basınç (Pa)": (0, 3, 3),
    "Yükseklik (m)": (1, 3, 4),
    "Sıcaklık (°C)": (2, 3, 6),
    "İniş Hızı (m/s)": (3, 3, 5),
    "Statü": (4, 3, 15),
    "Pil Gerilimi (V)": (0, 1, 7),
    "Pitch (°)": (5, 3, 12),
    "Roll (°)": (5, 2, 13),
    "Yaw (°)": (5, 1, 14),
}
status = [
    "Başlangıç",
    "Yükseliş",
    "Ayrılma",
    "Alçalış",
    "Yere İniş",
    "Kurtarma",
    "Veri Toplama",
    "PFR",
    "Test"
]
telemetry_names = [
    "Takım",
    "No",
    "Zaman (s)",
    "Basınç (Pa)",
    "Yükseklik (m)",
    "İniş Hızı (m/s)",
    "Sıcaklık (°C)",
    "Pil (V)",
    "Lat",
    "Long",
    "Alt",
    "Statü",
    "Pitch (°)",
    "Yaw (°)",
    "Roll (°)",
    "Dönüş",
    "Aktarım"
]

PATH_TELEMETRY = "telemetry"
PATH_VIDEOS = "videos"
PATH_ASSETS = "assets"
PATH_TELEMETRY_LATEST = os.path.join(PATH_TELEMETRY, "latest.csv")
PATH_VIDEOS_RLATEST = os.path.join(PATH_VIDEOS, "rlatest.avi")
PATH_VIDEOS_LATEST = os.path.join(PATH_VIDEOS, "latest.avi")
