

import cv2
import ultralytics
ultralytics.checks()
z
from ultralytics import YOLO


url = 'C:\\Users\\Mohamad MostafaHAREB\\PycharmProjects\\pythonProject2\\fyp\\artemis\\ml_models'
yolo_babies = YOLO(f"{url}/baby.pt")
res = yolo_babies('baby-test.jpg')
print(f"res: {res}")
res_plotted = res[0].plot()
cv2.imshow("result", res_plotted)