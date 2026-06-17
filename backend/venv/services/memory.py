class Memory:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})
    def add_assistant_message(self, message):
            self.conversation_history.append({"role": "assistant", "content": message})
    def get_conversation_history(self):
        return self.conversation_history
# m=Memory()
# print(m.get_conversation_history())