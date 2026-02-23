import cv2
import os
import numpy as np

# 설정 값
TARGET_SIZE = 200  # 저장될 정사각형 사이즈


class ImageCropper:
    def __init__(self, image_path, save_path):
        self.save_path = save_path
        self.img = cv2.imread(image_path)
        if self.img is None:
            print("이미지를 불러올 수 없습니다.")
            return

        self.original_img = self.img.copy()
        self.img_name = os.path.basename(image_path)
        
        self.scale = 1.0        # 확대/축소 배율
        self.mouse_x, self.mouse_y = 0, 0
        self.window_name = "Image Crop Tool (Wheel: Zoom, s: Save, q: Quit, ESC: Skip, )"

        self.is_dragging = False  # 드래그 상태 체크
        self.img_center_x = 250   # 이미지의 현재 중심 위치 (초기값: 캔버스 중앙)
        self.img_center_y = 250

        self.mouse_offset_x = 0
        self.mouse_offset_y = 0

        self.img_center_x_anchor = 250   # 이미지의 클릭시점 중심 위치 (초기값: 캔버스 중앙)
        self.img_center_y_anchor = 250


    def mouse_callback(self, event, x, y, flags, param):
        # 1. 휠 동작: 확대/축소 (기존과 동일)
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0: self.scale += 0.05
            else: self.scale = max(0.1, self.scale - 0.05)

        # 2. 마우스 왼쪽 버튼 클릭: 드래그 시작
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.is_dragging = True
            self.mouse_offset_x = x
            self.mouse_offset_y = y
            self.img_center_x_anchor = self.img_center_x
            self.img_center_y_anchor = self.img_center_y
            # 클릭한 시점의 마우스 위치 저장 (선택 사항: 더 정교한 이동을 위함)


        # 3. 마우스 이동: 드래그 중일 때만 이미지 중심점 업데이트
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.is_dragging:
                self.img_center_x = self.img_center_x_anchor+x-self.mouse_offset_x
                self.img_center_y = self.img_center_y_anchor+y-self.mouse_offset_y

        # 4. 마우스 왼쪽 버튼 뗌: 드래그 종료 및 저장
        # (원하신다면 여기서 바로 저장하거나, 별도의 키(Enter 등)로 저장하게 할 수 있습니다)
        elif event == cv2.EVENT_LBUTTONUP:
            self.is_dragging = False
            # 만약 "드래그를 멈추는 순간 저장"을 원하시면 여기서 self.save_crop() 호출

    def save_crop(self):
        # 현재 배율에 맞춰 이미지 리사이즈
        h, w = self.original_img.shape[:2]
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        resized = cv2.resize(self.original_img, (new_w, new_h))

        # 크롭 영역 계산 (마우스 중심에서 200x200)
        # 캔버스 좌표(x, y)에서 실제 리사이즈된 이미지의 좌표를 계산해야 함
        # 여기서는 단순화를 위해 현재 화면에 보이는 대로 처리
        x1 = self.mouse_x - TARGET_SIZE // 2
        y1 = self.mouse_y - TARGET_SIZE // 2
        
        # 실제 저장 로직 (화면 밖 예외 처리 생략)
        # 가이드 박스 내부의 픽셀을 추출
        crop = self.canvas[150:350, 150:350] # 가이드 박스 좌표 고정
        
        save_path = os.path.join(self.save_path, f"crop_{self.img_name}")
        cv2.imwrite(save_path, crop)
        print(f"저장 완료: {save_path}")

    def run(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        while True:
            # 500x500 빈 캔버스 생성 (작업 공간)
            self.canvas = np.zeros((500, 500, 3), dtype=np.uint8)
            
            # 1. 이미지 리사이즈
            h, w = self.original_img.shape[:2]
            new_w, new_h = int(w * self.scale), int(h * self.scale)
            resized = cv2.resize(self.original_img, (new_w, new_h))

            # 2. 이미지를 마우스 위치에 배치 (중심점 맞추기)
            # 캔버스 범위 내에 이미지를 얹음
            start_x = self.img_center_x - new_w // 2
            start_y = self.img_center_y - new_h // 2
            
            # 캔버스 영역 계산 (복잡한 슬라이싱 생략을 위해 단순 대입 대신 연산 사용)
            # 여기서는 편의상 전체 이미지를 마우스 따라 캔버스에 투영
            for i in range(new_h):
                for j in range(new_w):
                    target_y, target_x = start_y + i, start_x + j
                    if 0 <= target_y < 500 and 0 <= target_x < 500:
                        self.canvas[target_y, target_x] = resized[i, j]

            # 3. 중앙에 200x200 가이드 박스 그리기 (여기에 맞추면 됨)
            margin = 3
            cv2.rectangle(self.canvas, (150-margin, 150-margin), (350+margin, 350+margin), (0, 255, 0), 2)
            
            cv2.imshow(self.window_name, self.canvas)
            
            key = cv2.waitKey(1) & 0xFF
            # Ctrl+S 처리 (ASCII 19번)
            if key == ord('s'):
                self.save_crop()
            if key == 27: # ESC 누르면 다음 이미지
                break
            elif key == ord('q'): # q 누르면 종료
                return "quit"
        
        cv2.destroyAllWindows()
        return "next"