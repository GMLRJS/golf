from flask import Flask, render_template, request, send_file, make_response
import mediapipe as mp
import cv2
import os
from flask_cors.extension import CORS
from dao_golf import GlfprUseDao


app = Flask(__name__)
CORS(app)


app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MIME_TYPES'] = {'.mp4': 'video/mp4'}
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
dao = GlfprUseDao()




@app.route('/', methods=['GET'])
@app.route('/index')
def index():
    global rcordNo
    rcordNo = request.args["rcordNo"]
    print(rcordNo)
    file_path = dao.select(rcordNo)
    print(file_path)
    if file_path == None:
        return render_template('swingAnalyze.html')
    else:
        print(file_path)
        
        return render_template('swingAnalyze2.html',file_path=file_path)   
    


@app.route('/ajax_upload', methods=['POST'])
def ajax_upload():
    # 업로드된 동영상 파일 저장
    file = request.files['file']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(video_path)

    # 동영상 분석 및 결과 저장
    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=2)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    output_path = 'static/' + file.filename
    #output_path = 'output/' + file.filename.split('.')[0] + '_output.mp4'
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

    is_first = True
    first_center_x, first_center_y, first_radius = None, None, None

    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break

        img_h, img_w, _ = img.shape
        img_result = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img)

        mp_drawing.draw_landmarks(
            img_result,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        if results.pose_landmarks:
            landmark = results.pose_landmarks.landmark

            left_ear_x = landmark[mp_pose.PoseLandmark.LEFT_EAR].x * img_w
            left_ear_y = landmark[mp_pose.PoseLandmark.LEFT_EAR].y * img_h
            
            right_ear_x = landmark[mp_pose.PoseLandmark.RIGHT_EAR].x * img_w
            right_ear_y = landmark[mp_pose.PoseLandmark.RIGHT_EAR].y * img_h
            
            center_x = int((left_ear_x + right_ear_x) / 2)
            center_y = int((left_ear_y + right_ear_y) / 2)
            
            radius = int((left_ear_x - right_ear_x) / 2)
            radius = max(radius, 20)

            if is_first:
                first_center_x = center_x
                first_center_y = center_y
                first_radius = int(radius * 2)
                is_first = False
                
            else:
                cv2.circle(img_result, center=(first_center_x, first_center_y),
                           radius=first_radius, color=(0, 255, 255), thickness=2)
                color = (0, 255, 0)  # 초록색
    
                if center_x - radius < first_center_x - first_radius \
                        or center_x + radius > first_center_x + first_radius:
                    color = (0, 0, 255)  # 빨간색
    
                cv2.circle(img_result, center=(center_x, center_y),
                           radius=radius, color=color, thickness=2)
    
        out.write(img_result)
    
    pose.close()
    cap.release()
    out.release()
    # print(output_path)
    # print(rcordNo)
    cnt = dao.update(rcordNo, output_path)
    print(cnt)
    response = make_response(send_file(output_path, mimetype='video/mp4', as_attachment=True,
                                       attachment_filename=file.filename))
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response


if __name__ == '__main__':
    app.run(debug=True)


