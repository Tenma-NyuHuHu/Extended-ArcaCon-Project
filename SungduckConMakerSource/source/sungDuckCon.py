import os
import configparser
from PIL import Image, ImageDraw, ImageFont

def draw_stretched_text(base_img, text, font, position, fill, outline_color, stretch_ratio):
    """
    stretch_ratio: 1.0보다 작으면 가로로 홀쭉해지고, 크면 뚱뚱해집니다.
    """
    # 1. 텍스트 크기 측정
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # 외곽선 두께(약 2px)를 고려해 넉넉한 임시 이미지 생성 (RGBA)
    temp_txt_img = Image.new("RGBA", (tw + 10, th + 10), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_txt_img)
    
    # 2. 임시 이미지에 텍스트 그리기 (외곽선 포함)
    txt_pos = (5, 5)
    # 흰색 외곽선
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
            temp_draw.text((txt_pos[0]+dx*4, txt_pos[1]+dy*4), text, font=font, fill=outline_color)
    # 본문
    temp_draw.text(txt_pos, text, font=font, fill=fill)
    
    # 3. 가로 비율 조절 (Resize)
    new_width = int(temp_txt_img.width * stretch_ratio)
    resized_txt = temp_txt_img.resize((new_width, temp_txt_img.height), Image.LANCZOS)
    
    # 4. 중앙 정렬을 위한 위치 재계산 및 합성
    # position은 원래 (x, y)인데, 가로가 줄었으므로 중앙을 다시 잡습니다.
    final_x = (200 - new_width) // 2
    base_img.paste(resized_txt, (final_x, position[1]), resized_txt)

def draw_text_with_spacing(draw, position, text, font, fill, tracking=-2):
    """
    tracking: 음수면 자간이 좁아지고, 양수면 넓어집니다.
    """
    x, y = position
    for char in text:
        # 현재 글자 그리기
        draw.text((x, y), char, font=font, fill=fill)
        
        # 다음 글자의 시작 위치 계산
        # font.getlength(char)는 해당 글자의 너비를 반환합니다.
        char_width = font.getlength(char)
        x += (char_width + tracking)  # 너비에 tracking(자간)을 더함

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
    duration_per_frame = conf.getint('duration_per_frame', fallback=550)
    font_size = conf.getint('font_size', fallback=45)
    stretch_ratio = conf.getfloat('stretch_ratio', fallback=0.7)
    bottom_margin = conf.getint('bottom_margin', fallback=55)
    font_path = "./fonts/MaplestoryLight.ttf"
    output_path = "./output/"+display_text+".gif"
    
    frames = []
    # 폴더 내 이미지 파일 목록 가져오기 (정렬 포함)
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.webp', '.PNG'))])

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
        
        # #자간
        # # 글씨를 쓰기 위한 Draw 객체 생성
        # draw = ImageDraw.Draw(img)

        # ascent, descent = font.getmetrics()
        # text_height = ascent + descent
        
        # tracking = -3
        # # 전체 텍스트의 예상 너비를 계산해야 중앙 정렬이 가능합니다.
        # total_width = sum(font.getlength(c) for c in display_text) + (tracking * (len(display_text) - 1))
        # position = ((200 - total_width) // 2, 200 - text_height - 15)


        # # 1. 흰색 외곽선 (함수 호출로 대체)
        # outline_color = "white"
        # for adj_x, adj_y in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
        #         draw_text_with_spacing(draw, (position[0]+adj_x*3, position[1]+adj_y*3), 
        #                             display_text, font, outline_color, tracking=tracking)
        # # 2. 검은색 본문
        # draw_text_with_spacing(draw, position, display_text, font, "black", tracking=tracking)
        draw_stretched_text(img, display_text, font, (0, 200-bottom_margin), "black", "white", stretch_ratio)
        
        
        frames.append(img.convert("RGB"))

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