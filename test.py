import serial
import time

def setup_arduino():
    try:
        arduino = serial.Serial('/dev/cu.usbmodem11101', 9600, timeout=1)
        time.sleep(2)  # 아두이노 연결 안정화를 위한 대기
        print("아두이노 연결 성공!")
        return arduino
    except Exception as e:
        print(f"아두이노 연결 실패: {e}")
        return None

def control_leds(arduino, count):
    if arduino is None:
        return
        
    try:
        command = None
        if count <= 3:
            command = b'G'  # Green LED
            print("명령 전송: G (녹색 LED)")
        elif count == 4:
            command = b'Y'  # Yellow LED
            print("명령 전송: Y (노란색 LED)")
        else:
            command = b'R'  # Red LED
            print("명령 전송: R (빨간색 LED)")
            
        arduino.write(command)
        # 아두이노로부터 응답 읽기
        time.sleep(0.1)  # 응답을 받기 위한 짧은 대기
        while arduino.in_waiting:
            response = arduino.readline().decode().strip()
            print(f"아두이노 응답: {response}")
            
    except Exception as e:
        print(f"LED 제어 중 오류 발생: {e}")

def main():
    arduino = setup_arduino()
    if arduino is None:
        return
    
    print("\n=== LED 제어 프로그램 (디버그 모드) ===")
    print("숫자를 입력하면 해당하는 LED가 켜집니다:")
    print("3 이하: 녹색 LED (양호)")
    print("4: 노란색 LED (주의)")
    print("5 이상: 빨간색 LED (경고)")
    print("'q' 입력시 종료")
    
    try:
        while True:
            user_input = input("\n숫자를 입력하세요 (종료: q): ")
            
            if user_input.lower() == 'q':
                print("프로그램을 종료합니다.")
                break
            
            try:
                count = int(user_input)
                control_leds(arduino, count)
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
    
    finally:
        if arduino is not None:
            arduino.close()
            print("아두이노 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()
