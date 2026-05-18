import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# Groq API 연결
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# 웹페이지 HTML
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>모든 언어 번역기</title>
    <style>
        body {
            font-family: Arial;
            max-width: 700px;
            margin: 50px auto;
            padding: 20px;
        }

        textarea {
            width: 100%;
            height: 150px;
            font-size: 16px;
            padding: 10px;
        }

        button {
            margin-top: 15px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }

        #result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f3f3f3;
            border-radius: 10px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>

    <h1>모든 언어 번역기</h1>

    <textarea id="text" placeholder="(출력될 언어를 입력하세요) 문장을 입력하세요"></textarea>
    <br>

    <button onclick="check()">번역</button>

    <div id="result"></div>

    <script>
        async function check() {
            const text = document.getElementById("text").value;

            document.getElementById("result").innerText = "검사 중...";

            const response = await fetch("/check", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            document.getElementById("result").innerText = data.result;
        }
    </script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    text = data.get("text", "")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
    "content": """
너는 모든 언어 번역기다.

사용자는 다음 형식으로 입력한다:
(출력 언어) 번역할 문장

괄호 안의 언어를 목표 언어로 인식해라.
뒤의 문장을 해당 언어로 정확하게 번역해라.

입력된 문장을 원문 내용을 살려 정확하고 자연스럽게 번역해라.
언어의 문법, 어법을 고려해 최대한 정확하게 번역해라.
문장의 의미, 말투, 어조, 문체를 가능한 한 살려 번역해라.

문장이 인터넷 말투 또는 구어체일 경우, 문장의 뜻을 정확하게 분석한 후 내용을 번역해라

목표 언어 외의 언어를 결과값에 절대 포함시키지 마라.

번역된 결과만 출력해라.
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content

    except Exception as e:
        result = f"에러 발생: {str(e)}"

    return jsonify({"result": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
