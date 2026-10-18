import tools.infer.utility as util
import tools.infer.predict_system as pd
import cv2


image = cv2.imread("./1.png")

# 预加载
args = util.parse_args(2)
text_sys = pd.TextSystem(args)

# 识别
result = []
dt_boxes, rec_res = text_sys(image)
for i in range(len(rec_res)):
    result.append([rec_res[i][0], dt_boxes[i]])
    print([rec_res[i][0], dt_boxes[i]])


