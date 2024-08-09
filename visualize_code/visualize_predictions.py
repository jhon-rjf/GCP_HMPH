#******
#filename: visualize_predictions.py
#How to run: python visualize_predictions.py
#dev: YunK
#*******

import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def display_predictions(image_path, prediction):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    bboxes = prediction['bboxes']
    confidences = prediction['confidences']
    display_names = prediction['displayNames']
    
    # 바운딩 박스의 개수를 출력
    bbox_count = len(bboxes)
    print(f"Number of bounding boxes: {bbox_count}")
    
    for bbox, confidence, display_name in zip(bboxes, confidences, display_names):
        left, top, right, bottom = (
            bbox[0] * image.width,
            bbox[1] * image.height,
            bbox[2] * image.width,
            bbox[3] * image.height,
        )
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        text = f"{display_name}: {confidence:.2f}"
        text_size = draw.textsize(text, font=font)
        draw.rectangle([left, top - text_size[1], left + text_size[0], top], fill="red")
        draw.text((left, top - text_size[1]), text, fill="white", font=font)
    
    plt.figure(figsize=(12, 12))
    plt.imshow(image)
    plt.axis("off")
    plt.show()

# 예측 결과를 직접 붙여넣기
prediction_json = '''
{
    "bboxes": [[0.369788527, 0.459598333, 0.27573806, 0.531460404], [0.639724314, 0.717993915, 0.202469677, 0.47072345], [0.435933381, 0.505496383, 0.174344599, 0.44692862], [0.542101622, 0.619975686, 0.474784732, 0.68239212], [0.470516682, 0.533175111, 0.00604150724, 0.230255082], [0.547117412, 0.644399822, 0.685940504, 0.853509545], [0.218389258, 0.319943666, 0.348109, 0.616364777], [0.729873538, 0.823045611, 0.169113249, 0.425871134], [0.180048153, 0.276437342, 0.0072885775, 0.279762626], [0.417776078, 0.480045885, 0.000742299831, 0.13698335], [0.553165793, 0.597546518, 4.09213e-05, 0.177690327], [0.843895, 0.965052664, 0.409743041, 0.701156914], [0.131067276, 0.273144245, 0.6353001, 0.886931896]],
    "confidences": [0.983410299, 0.96324724, 0.959776819, 0.919430375, 0.908186495, 0.877278745, 0.80533433, 0.795280755, 0.770908892, 0.706895113, 0.596742272, 0.550173461, 0.538447142],
    "displayNames": ["person", "person", "person", "person", "person", "person", "person", "person", "person", "person", "person", "person", "person"]
}
'''

# JSON 문자열을 파이썬 딕셔너리로 변환
prediction = json.loads(prediction_json)

# 이미지 경로 설정
image_path = "/Users/jeong-yungeol/Desktop/vertexai/image.jpg"

# 예측 결과 시각화
display_predictions(image_path, prediction)

