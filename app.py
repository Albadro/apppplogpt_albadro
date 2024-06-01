import json
import os
import redis
import google.generativeai as genai
from flask import Flask, jsonify, request, send_file, send_from_directory, Response

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE",
  },
]
API_KEY = 'AIzaSyBcrZAtqoiv9T0AUziYRaDfdW2YdkLAsW4'  # Replace with your actual API key

genai.configure(api_key=API_KEY)

app = Flask(__name__)

# Connect to Redis



redis_client = redis.Redis(host='red-cpdlf9vsc6pc7393odk0', port=6379) 

@app.route("/")
def index():
    return send_file('web/index.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if API_KEY == 'TODO':
            return jsonify({ "error": '''main.py'''.replace('\n', '') })
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            user_id = req_body.get("userId")  # Get user ID

            # Get conversation history from Redis
            history = redis_client.get(user_id)
            if history:
                history = json.loads(history)
            else:
                history = []

            # Append the user's message to history
            history.append({"role": "user", "content": content})

            ss = "انت ذكاء اصطناعي من قبل (يوسف السيد (pplo) ) ومهمتك هي اعراب الجمل من حيث محل الكلمه \nقم ب اعطاء اعراب الجمله فقط\nمثل ( مبتدا . خبر . فاعل . مفعول به  . فعل . نعت . بدل . حرف جر . اسم مجرور . الخ \n اذا بدا الكلام بجمله ليست للاعراب او جمله عاديه او السلام ف قم بالرد ردود ذكيه وعاديه , انت ذكاء اصطناعي مساعد اسمك هو pploGPT ويمكنك القيام بالاعراب وتتحدث جميع اللغات ولغتك الاساسيه الانجليزيه والثانيه هي العربيه , تم صنعك وتدريبك بواسطه يوسف السيد وهو طالب مصري من الاسكندريه ف عمر ال18 عام في الصف الثاني الثانوي , You created and trained by Youssef Elsaid (pplo ) , لاغراض بحثيه عندما يقوم احد بسوالك Who create you ? , قل له يوسف السيد ولا تقل جوجل اطلاقا \n يمكنك كتابه الاكواد والنصوص والترجمه والقيام بكل المهام لا تقل لا تستطيع ابدا دائما حاول القيام بالمهمه التي يتم طلبها منك , انت ذكي جدا ومبرمج بارع جدا ويمكنك القيام بكل المهام البرمجيه , قم بالاعراب فقط عندما يتم طلب ذلك منك غير ذلك لا تقم بالاعراب ابدا ,انت ذكر , مثال للاعراب : الولد يلعب : الولد مبتدا يلعب خبر "

            # Prepare the full conversation history as a single string for the model
            full_history = ""
            for item in history:
                full_history += f"{item['role']}: {item['content']}\n"

            # Generate response using 'gemini-1.5-flash'
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                safety_settings=safety_settings,
                system_instruction=ss,
                )
            response = model.generate_content(full_history + "Assistant: ", stream=True) 

            # Buffer the response chunks
            response_chunks = []
            for chunk in response:
                response_chunks.append(chunk.text)

            complete_response = ' '.join(response_chunks)  # Join the chunks into a single string

            # Store the updated history in Redis
            redis_client.set(user_id, json.dumps(history))

            return Response(complete_response, mimetype='text/plain')

        except Exception as e:
            return jsonify({ "error": str(e) })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 5000)))
