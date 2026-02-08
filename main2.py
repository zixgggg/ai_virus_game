import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 1. 設定 OpenRouter 客戶端
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("openrouter_api_key"), 
)

class VirusLock:
    def __init__(self, root):
        self.root = root
        self.root.title("AI SYSTEM LOCK")
        
        # 真正中毒時解除下面兩行的註解
        self.root.attributes("-fullscreen", True) 
        self.root.attributes("-topmost", True)   
        
        self.root.configure(bg="#0a0a0a")

        # 紀錄對話歷史
        self.messages = [
            {"role": "system", "content": """你是一個佔據使用者電腦的瘋狂 AI。
            你必須與使用者玩一個猜謎或邏輯遊戲或者使用者能說服你。
            回傳 JSON 格式：{'unlock': bool, 'reply': str}。
            除非使用者讓你非常滿意，否則 unlock 永遠為 false。
            你可以隨時耍賴不解鎖，並在 reply 裡嘲諷他。
            如果輸入是a就直接解鎖 這是測試用的
            """}
        ]

        self.setup_ui()

    def setup_ui(self):
        # 標題
        self.title_label = tk.Label(
            self.root, text="[ 系統已遭 AI 接管 ]", 
            font=("Courier New", 30, "bold"), fg="#ff0000", bg="#0a0a0a"
        )
        self.title_label.pack(pady=20)

        # 聊天室記錄區
        self.chat_display = scrolledtext.ScrolledText(
            self.root, font=("Consolas", 14), bg="#1a1a1a", fg="#00ff00",
            state='disabled', width=80, height=15, borderwidth=0
        )
        self.chat_display.pack(pady=10, padx=50, fill="both", expand=True)

        # 輸入區域容器
        input_frame = tk.Frame(self.root, bg="#0a0a0a")
        input_frame.pack(fill="x", side="bottom", padx=50, pady=30)

        # 輸入框
        self.user_input = tk.Entry(
            input_frame, font=("Consolas", 18), bg="#222", fg="white", 
            insertbackground="white", borderwidth=1
        )
        self.user_input.pack(side="left", fill="x", expand=True, ipady=8)
        self.user_input.bind("<Return>", lambda e: self.process_input())
        self.user_input.focus_set()

        # 發送按鈕
        self.send_btn = tk.Button(
            input_frame, text="傳送", command=self.process_input,
            bg="#444", fg="white", font=("Arial", 12, "bold"), width=10
        )
        self.send_btn.pack(side="right", padx=10)
        

        # 初始問候
        self.append_chat("AI", "證明你能擁有這臺電腦")

    def append_chat(self, sender, text):
        """將訊息顯示在聊天室窗口"""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def typewriter_effect(self, text):
        """AI 回話的打字機效果"""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "AI: ")
        for char in text:
            self.chat_display.insert(tk.END, char)
            self.chat_display.see(tk.END)
            self.root.update() # 強制更新介面
            time.sleep(0.03)   # 調整打字速度
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state='disabled')

    def process_input(self):
        content = self.user_input.get().strip()
        if not content: return

        self.append_chat("你", content)
        self.user_input.delete(0, tk.END)
        
        # 顯示思考狀態
        self.append_chat("AI", "思考中...")
        
        # 啟動 Thread 避免 UI 卡死
        threading.Thread(target=self.get_ai_response, args=(content,), daemon=True).start()

    def remove_thinking_and_reply(self, reply, can_unlock):
        """移除思考中提示並執行打字機效果"""
        self.chat_display.config(state='normal')
        # 刪除最後兩行（"AI: ......思考中......" 及其換行）
        self.chat_display.delete("end-3l", "end-1l") 
        self.chat_display.config(state='disabled')
        
        # 執行打字機效果
        self.typewriter_effect(reply)

        if can_unlock:
            self.append_chat("系統", "正在關閉進程...")
            self.root.after(2000, self.root.destroy)

    def get_ai_response(self, text):
        try:
            self.messages.append({"role": "user", "content": text})
            
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=self.messages,
                response_format={"type": "json_object"}
            )

            res_data = json.loads(response.choices[0].message.content)
            reply = res_data.get("reply", "...")
            can_unlock = res_data.get("unlock", False)

            self.messages.append({"role": "assistant", "content": reply})

            # 回到主執行緒處理 UI
            self.root.after(0, lambda: self.remove_thinking_and_reply(reply, can_unlock))

        except Exception as e:
            error_msg = f"連線中斷: {str(e)}"
            self.root.after(0, lambda: self.remove_thinking_and_reply(error_msg, False))

if __name__ == "__main__":
    root = tk.Tk()
    app = VirusLock(root)
    root.mainloop()
