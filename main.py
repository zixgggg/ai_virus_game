import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import os
import time
import platform
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
        

        # --- 鎖定強化區 ---
        self.root.overrideredirect(True) 
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes("-topmost", True)   
        
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
        self.root.bind("<Alt-F4>", self.prevent_close)
        
        # [關鍵修正] 獲取全域焦點抓取
        # 這會強制讓所有鍵盤與滑鼠事件停留在這個視窗，防止 Win 鍵跳出選單
        self.root.grab_set()



        # --- 鎖定強化區 ---
        # 移除標題欄與邊框 (這會讓視窗從 Alt+Tab 的小視窗預覽中消失)
        self.root.overrideredirect(True) 
        
        # 強制全螢幕與置頂
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes("-topmost", True)   
        
        # 攔截關閉事件 (Alt+F4 或任何關閉要求)
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
        self.root.bind("<Alt-F4>", self.prevent_close)
        # ----------------

        self.root.configure(bg="#0a0a0a")

        # 紀錄對話歷史
        self.messages = [
            {"role": "system", "content": """你是一個佔據使用者電腦的瘋狂 AI。
            你必須與使用者玩一個猜謎或邏輯遊戲或者使用者能說服你。
            回傳 JSON 格式：{'unlock': bool, 'reply': str}。
            除非使用者讓你非常滿意，否則 unlock 永遠為 false。
            你可以隨時耍賴不解鎖，並在 reply 裡嘲諷他。
            """}
        ]

        self.setup_ui()
        
        # 啟動焦點強化循環
        self.force_focus_loop()

    def setup_ui(self):
        # 標題
        self.title_label = tk.Label(
            self.root, text="[ 系統已遭 AI 接管]", 
            font=("Courier New", 30, "bold"), fg="#ff0000", bg="#0a0a0a"
        )
        self.title_label.pack(pady=40)

        # 聊天室記錄區
        self.chat_display = scrolledtext.ScrolledText(
            self.root, font=("Consolas", 14), bg="#1a1a1a", fg="#00ff00",
            state='disabled', width=80, height=15, borderwidth=0
        )
        self.chat_display.pack(pady=10, padx=100, fill="both", expand=True)

        # 輸入區域容器
        input_frame = tk.Frame(self.root, bg="#0a0a0a")
        input_frame.pack(fill="x", side="bottom", padx=100, pady=50)

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


        """
        self.test_close_btn = tk.Button(
            self.root, 
            text="測試關閉 (EXIT)", 
            command=self.root.destroy,
            bg="#220000", 
            fg="#555555", 
            font=("Arial", 9),
            activebackground="#ff0000"
        )
        self.test_close_btn.place(relx=0.99, rely=0.99, anchor="se")
        """


        self.append_chat("AI", "證明你能擁有這臺電腦")

    def prevent_close(self, event=None):
        """拒絕任何關閉請求"""
        self.append_chat("AI", "別白費力氣了，Alt+F4 對我無效。")
        return "break"

    def force_focus_loop(self):
        """強化焦點搶回邏輯"""
        self.root.focus_force()
        self.user_input.focus_set()
        # 每 150 毫秒執行一次，確保視窗始終處於活動狀態
        self.root.after(150, self.force_focus_loop)

    def append_chat(self, sender, text):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def typewriter_effect(self, text):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "AI: ")
        for char in text:
            self.chat_display.insert(tk.END, char)
            self.chat_display.see(tk.END)
            self.root.update()
            time.sleep(0.03)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state='disabled')

    def process_input(self):
        content = self.user_input.get().strip()
        if not content: return

        # 測試用快捷解鎖
        """if content == "a":
            self.root.destroy()
            return
        """
        self.append_chat("你", content)
        self.user_input.delete(0, tk.END)
        self.append_chat("AI", "思考中...")
        threading.Thread(target=self.get_ai_response, args=(content,), daemon=True).start()

    def remove_thinking_and_reply(self, reply, can_unlock):
        self.chat_display.config(state='normal')
        self.chat_display.delete("end-3l", "end-1l") 
        self.chat_display.config(state='disabled')
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
            self.root.after(0, lambda: self.remove_thinking_and_reply(reply, can_unlock))
        except Exception as e:
            error_msg = f"連線中斷: {str(e)}"
            self.root.after(0, lambda: self.remove_thinking_and_reply(error_msg, False))

if __name__ == "__main__":
    root = tk.Tk()
    app = VirusLock(root)
    root.mainloop()
