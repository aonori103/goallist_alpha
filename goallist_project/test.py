import cv2

image_file = '../static/cat.png'
img = cv2.imread(image_file)
# img = cv2.resize(img, (579, 800))
cv2.imshow('image', img)
        
cv2.waitKey(0)
cv2.destroyAllWindows()
