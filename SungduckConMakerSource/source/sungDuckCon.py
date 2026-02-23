import os
import configparser
from PIL import Image, ImageDraw, ImageFont


def load_config(config_path):
    """config.txt 파일을 읽어 딕셔너리로 반환"""
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return config['SETTINGS']

def create_gif_with_text(image_folder):
    """
    image_folder: 원본 이미지들+config.txt가 들어있는 폴더 경로
    output_path: 저장될 GIF 파일명
    display_text: 이미지 하단에 고정될 한글 문자열
    """
    conf = load_config(image_folder+"/config.txt")
    display_text = conf.get('display_text', fallback="null")
    duration_per_frame = conf.getint('duration_per_frame', fallback=500)
    font_size = conf.getint('font_size', fallback=30)
    font_path = "./fonts/MaplestoryLight.ttf"
    output_path = "./output/"+display_text+".gif"
    
    frames = []
    # 폴더 내 이미지 파일 목록 가져오기 (정렬 포함)
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])

    if not image_files:
        print("이미지 파일을 찾을 수 없습니다.")
        return
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("폰트 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    durations = [duration_per_frame] * (len(image_files)+1)
    durations[-1] = duration_per_frame/5

    for filename in image_files:
        img = Image.open(os.path.join(image_folder, filename)).convert("RGBA")
        
        # 200x200 사이즈 확인 및 조정
        img = img.resize((200, 200))
        
        # 글씨를 쓰기 위한 Draw 객체 생성
        draw = ImageDraw.Draw(img)
        
        # 텍스트 위치 계산 (하단 중앙)
        text_bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((200 - text_width) // 2, 200 - text_height - 15) # 하단 여유 공간

        # 흰색 외곽선 그리기 (상하좌우 대각선으로 1픽셀씩 오프셋)
        outline_color = "white"
        for adj in range(-1, 2):
            for j in range(-1, 2):
                draw.text((position[0]+adj*2, position[1]+j*2), display_text, font=font, fill=outline_color)

        # 검은색 본문 글씨 그리기
        draw.text(position, display_text, font=font, fill="black")
        
        frames.append(img.convert("RGB"))

    # #처음꺼만 한번 더하기
    # for filename in image_files:
    #     img = Image.open(os.path.join(image_folder, filename)).convert("RGBA")
        
    #     # 200x200 사이즈 확인 및 조정
    #     img = img.resize((200, 200))
        
    #     # 글씨를 쓰기 위한 Draw 객체 생성
    #     draw = ImageDraw.Draw(img)
        
    #     # 텍스트 위치 계산 (하단 중앙)
    #     text_bbox = draw.textbbox((0, 0), display_text, font=font)
    #     text_width = text_bbox[2] - text_bbox[0]
    #     text_height = text_bbox[3] - text_bbox[1]
    #     position = ((200 - text_width) // 2, 200 - text_height - 15) # 하단 여유 공간

    #     # 흰색 외곽선 그리기 (상하좌우 대각선으로 1픽셀씩 오프셋)
    #     outline_color = "white"
    #     for adj in range(-1, 2):
    #         for j in range(-1, 2):
    #             draw.text((position[0]+adj*2, position[1]+j*2), display_text, font=font, fill=outline_color)

    #     # 검은색 본문 글씨 그리기
    #     draw.text(position, display_text, font=font, fill="black")

    #     #오른쪽 아래 미세한 점 찍기
    #     draw.point((199, 199), fill=(0, 0, 0))
        
    #     frames.append(img.convert("RGB"))
    #     break #처음꺼만 한번 더하기


    # GIF 저장
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=durations,
        loop=0 # 0은 무한 반복
    )
    print(f"GIF 생성 완료: {output_path}")

# --- 사용 예시 ---
# image_folder = "my_images"       # 이미지가 들어있는 폴더명
# font_path = "NanumGothic.ttf"    # 사용하고 싶은 폰트 경로
# create_gif_with_text(image_folder, "result.gif", "안녕 파이썬!", font_path)