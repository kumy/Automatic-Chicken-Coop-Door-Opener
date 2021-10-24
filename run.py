from app import create_app
import RPi.GPIO as GPIO

if __name__ == "__main__":
    app = create_app()
    app.run(host='::', port='80', debug=True)

    GPIO.cleanup()
    exit()
