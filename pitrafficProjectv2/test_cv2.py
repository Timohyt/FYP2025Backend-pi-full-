import cv2
import numpy as np

img = np.zeros((300, 300, 3), dtype=np.uint8)
cv2.putText(img, "Press Q", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

while True:
    cv2.imshow("Test Window", img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("You pressed Q")
        cv2.destroyWindow("Test Window")
        break
