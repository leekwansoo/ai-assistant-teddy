# 함수화

import time
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
print(api_key)
# OpenAI API를 사용하기 위한 클라이언트 객체를 생성합니다.
client = OpenAI(api_key=api_key)

# 이전에 설정한 Assistant ID 를 기입합니다.
#ASSISTANT_ID = assistant.id ,create-thread_and_run function 변수로 가져오도록 바꿈

# 새로운 스레드를 생성하고 메시지를 제출하는 함수를 정의합니다.
def create_thread_and_run(user_input, assistant_id):
    # 사용자 입력을 받아 새로운 스레드를 생성하고, Assistant 에게 메시지를 제출합니다.
    thread = client.beta.threads.create()
    run = submit_message(assistant_id, thread, user_input)
    return thread, run

# 스레드를 새롭게 생성합니다.
def create_new_thread():
    # 새로운 스레드를 생성합니다.
    thread = client.beta.threads.create()
    return thread

def submit_message(assistant_id, thread, user_message):
    # 사용자 입력 메시지를 스레드에 추가합니다.
    client.beta.threads.messages.create(
        # Thread ID가 필요합니다.
        # 사용자 입력 메시지 이므로 role은 "user"로 설정합니다.
        # 사용자 입력 메시지를 content에 지정합니다.
        thread_id=thread.id,
        role="user",
        content=user_message,
    )
    # 스레드에 메시지가 입력이 완료되었다면,
    # Assistant ID와 Thread ID를 사용하여 실행을 준비합니다.
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    return run


def wait_on_run(run, thread):
    # 주어진 실행(run)이 완료될 때까지 대기합니다.
    # status 가 "queued" 또는 "in_progress" 인 경우에는 계속 polling 하며 대기합니다.
    while run.status == "queued" or run.status == "in_progress":
        # run.status 를 업데이트합니다.
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        # API 요청 사이에 잠깐의 대기 시간을 두어 서버 부하를 줄입니다.
        time.sleep(0.5)
    return run


def get_response(thread):
    # 스레드에서 메시지 목록을 가져옵니다.
    # 메시지를 오름차순으로 정렬할 수 있습니다. order="asc"로 지정합니다.
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

# 메시지 출력용 함수
def print_message(response):
    for res in response:
        print(f"[{res.role.upper()}]\n{res.content[0].text.value}\n")
        
def ask(assistant_id, thread_id, user_message):
    run = submit_message(
        assistant_id,
        thread_id,
        user_message,
    )
    # 실행이 완료될 때까지 대기합니다.
    run = wait_on_run(run, thread_id)
    print_message(get_response(thread_id).data[-2:])
    return run

import json
# 인자로 받은 객체의 모델을 JSON 형태로 변환하여 출력합니다.
# Assistant 가 응답한 결과를 분석할 때 답변을 출력(print)할 목적으로 활용하는 함수입니다.

def show_json(obj):
    # obj의 모델을 JSON 형태로 변환한 후 출력합니다.
    print(json.loads(obj.model_dump_json()))
    
# File_Uploader for Assistant API

# 파일 업로드를 위한 함수를 정의합니다.
def upload_files(files):
    uploaded_files = []
    for filepath in files:
        file = client.files.create(
            file=open(
                # 업로드할 파일의 경로를 지정합니다.
                filepath,  # 파일경로. (예시) data/sample.pdf
                "rb",
            ),
            purpose="assistants",
        )
        uploaded_files.append(file)
        print(f"[업로드한 파일 ID]\n{file.id}")
    return uploaded_files

# list files in Assistant Storage
# 업로드한 모든 파일 ID 와 파일명을 출력합니다.
def list_files():
  file_ids = []
  for file in client.files.list():
    file_ids.append(file)
    print(f"[파일 ID] {file.id} [파일명] {file.filename}")
  return file_ids

# Abstract file element and create file in json format
def abstract_file_element(file):
    id = file.id 
    bytes = file.bytes 
    created_at = file.created_at 
    filename = file.filename
    object = file.object 
    purpose = file.purpose
    status = file.status 
    status_details = file.status_details
    
    file_json = {"id": id, "bytes": bytes, "created_at":created_at, "filename": filename, "object": object, "purpose": purpose, "status": status, "status_details": status_details}
    return file_json



# create display_quiz function
def display_quiz(title, questions, show_numeric=False):
    print(f"제목: {title}\n")
    responses = []

    for q in questions:
        # 질문을 출력합니다.
        print(q["question_text"])
        response = ""

        # 각 선택지를 출력합니다.
        for i, choice in enumerate(q["choices"]):
            if show_numeric:
                print(f"{i+1} {choice}")
            else:
                print(f"{choice}")

        response = input("정답을 선택해 주세요: ")
        responses.append(response)
        print()

    return responses