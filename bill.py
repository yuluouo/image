import cv2  # 用於影像處理的 OpenCV 函式庫。
import os   # 用於操作檔案與資料夾。
import pytesseract  # 用於進行文字識別（OCR）。
from PIL import Image   # 來自 Pillow，用於處理圖像文件。
import re   # 用於正則表達式處理。

# 讓使用者輸入當期的中獎號碼，使用正則表達式 r'^\d{3}$' 檢查是否為正確格式（僅限3個數字），如果輸入錯誤，程式結束，提示使用者重新輸入。
winning_last_3_digits = input("請輸入當期的中獎號碼（3碼數字）：")
if not re.match(r'^\d{3}$', winning_last_3_digits): 
    print("請輸入正確的3碼數字！")  
    exit()

# process_images 函式，負責處理給定資料夾內的所有圖片，並用迴圈跑遍資料夾中的圖片
def process_images(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('jpg', 'jpeg', 'png'))]

    for filename in image_files:
        print(f"Processing file: {filename}")
        file_path = os.path.join(folder_path, filename)

        # 讀取圖片，若讀取失敗則跳過。
        image = cv2.imread(file_path)
        if image is None:
            print(f"無法讀取圖片: {filename}")
            continue
        
        # 將圖片轉為灰階、使用高斯模糊減少雜訊、使用 Canny 邊緣檢測找出圖片中的輪廓。
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 0) 
        edges = cv2.Canny(blurred, 50, 300) 

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

        # 將符合條件的輪廓用綠色方框標註。
        result_image = image.copy()
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 20:
                cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 透過使用 Tesseract OCR 提取圖片中的文字
        text = pytesseract.image_to_string(Image.open(file_path), lang='eng')
        #print("偵測到的完整文字內容：")
        #print(text)

        # 定義發票號碼的規則（以英文開頭，後接8位數字，中間可有空格或連字符），確保偵測到的是發票號碼
        pattern = r'[A-Z]+[-\s]*\d{8}'

        # 用re.findall 匹配所有可能的發票號碼。
        matches = re.findall(pattern, text)

        #使用 re.sub 清除不必要的勿偵測、空格與連字符。
        cleaned_matches = [re.sub(r'[-\s]+', '', match) for match in matches]

        # 顯示發票號碼並判斷是否中獎，判斷最後3位是否與中獎號碼相同，輸出【中獎】或【沒中獎】
        if cleaned_matches:
            print("偵測到的發票號碼：")
            for match in cleaned_matches:
                print(match)
                # 判斷是否中獎
                if match[-3:] == winning_last_3_digits:
                    print("【中獎】")
                else:
                    print("【沒中獎】")
        else:
            print("未能找到發票號碼。")

        # 顯示處理結果
        #cv2.imshow("Processed Image", result_image)
        #cv2.waitKey(0)
        cv2.destroyAllWindows()

#主程式的入口，提示使用者輸入資料夾路徑，檢查路徑是否有效，若有效則執行圖片處理。
if __name__ == "__main__":
    folder_path = input("請輸入圖片資料夾的路徑：")
    if os.path.isdir(folder_path):
        process_images(folder_path)
    else:
        print("無效的資料夾路徑。")
