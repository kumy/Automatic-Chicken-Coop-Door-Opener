from app import create_app
import RPi.GPIO as GPIO

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', debug=False)

    GPIO.cleanup()
    exit()
