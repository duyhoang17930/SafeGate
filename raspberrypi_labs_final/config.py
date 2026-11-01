from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "users.db"
LOG_PATH = BASE_DIR / "logs" / "access.csv"

YUNET_MODEL = BASE_DIR / "models" / "face_detection_yunet.onnx"
SFACE_MODEL = BASE_DIR / "models" / "face_recognition_sface.onnx"
PPE_MODEL = BASE_DIR / "models" / "ppe_best.onnx"

# Use an integer camera index such as 0, or a stable Linux device path.
CAMERA_DEVICE = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_BACKEND = "v4l2"

PREVIEW_ENABLED = True
PREVIEW_HOST = "0.0.0.0"
PREVIEW_PORT = 8080
PREVIEW_AUTO_OPEN = True
PREVIEW_JPEG_QUALITY = 80

YUNET_SCORE_THRESHOLD = 0.8
YUNET_NMS_THRESHOLD = 0.3
YUNET_TOP_K = 5000
FACE_MATCH_THRESHOLD = 0.40

REGISTER_SAMPLES = 10
ACCESS_SAMPLES = 5
SAMPLE_INTERVAL_SECONDS = 0.20
ACCESS_COOLDOWN_SECONDS = 3.0
DENIED_COOLDOWN_SECONDS = 2.0

GREEN_LED_PIN = 17
YELLOW_LED_PIN = 23
RED_LED_PIN = 27
SERVO_PIN = 18
BUZZER_PIN = 22

SERVO_LOCK_ANGLE = 0
SERVO_OPEN_ANGLE = 90
DOOR_OPEN_SECONDS = 3.0
GREEN_LIGHT_SECONDS = 3.0
YELLOW_LIGHT_SECONDS = 2.0
DENIED_BUZZ_SECONDS = 1.5

# Display mode:
# - "lcd_i2c" for common 16x2/20x4 I2C LCD backpacks.
# - "console" for testing without display hardware.
DISPLAY_MODE = "lcd_i2c"
LCD_I2C_ADDRESS = 0x27
LCD_COLUMNS = 16
LCD_ROWS = 2

# Both labs require a known face AND required PPE.
ENABLE_PPE_STATUS = True
PPE_IMAGE_SIZE = 320
PPE_CONFIDENCE = 0.35
