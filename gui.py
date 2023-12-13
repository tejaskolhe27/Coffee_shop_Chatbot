import tkinter as tk
from tkinter import scrolledtext, END, PhotoImage
import torch
import random
from model import NeuralNet
from nltk_utils import *
import json

with open('intents.json', 'r') as f:
    intents = json.load(f)

class ChatbotGUI:
    def __init__(self, master):
        self.master = master
        master.title("GO-Cafe")

        # Load the trained model
        FILE = 'data.pth'
        data = torch.load(FILE)
        input_size = data['input_size']
        hidden_size = data['hidden_size']
        output_size = data["output_size"]
        self.all_words = data["all_words"]
        model_state = data["model_state"]
        self.tags = data["tags"]  # Make tags an instance variable

        self.model = NeuralNet(input_size, hidden_size, output_size)
        self.model.load_state_dict(model_state)
        self.model.eval()

        self.bot_name = "Tejas"
            
        # Create and configure the chat display
        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=50, height=20, font=("Arial", 12))
        self.chat_display.pack(padx=10, pady=10)

        # Create and configure the user input entry
        self.user_input_entry = tk.Entry(master, width=50, font=("Arial", 12))
        self.user_input_entry.pack(padx=10, pady=10)

        # Load a chatbot icon
        icon = PhotoImage(file="logo.png")  # Replace with the path to your icon image
        master.iconphoto(True, icon)

        # Create the send button with a colorful background
        send_button_color = "#4CAF50"  # Green color
        self.send_button = tk.Button(master, text="Send", command=self.send_message, bg=send_button_color, fg="white", font=("Arial", 12))
        self.send_button.pack(pady=10)

    def send_message(self):
        user_input = self.user_input_entry.get()
        if user_input.lower() == 'quit':
            self.master.destroy()
            return

        sentence = tokenize(user_input)
        X = bag_of_words(sentence, self.all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X)
        output = self.model(X)
        _, predicted = torch.max(output, dim=1)
        tag = self.tags[predicted.item()]  # Use self.tags

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()].item()

        response = ""
        if prob > 0.75:
            for intent in intents['intents']:
                if tag == intent['tag']:
                    response = f"{self.bot_name}: {random.choice(intent['responses'])}"
        else:
            response = f"{self.bot_name}: I do not understand...."

        self.update_chat_display(f"You: {user_input}\n{response}")

    def update_chat_display(self, message):
        self.chat_display.insert(END, message + "\n")
        self.chat_display.yview(END)
        self.user_input_entry.delete(0, 'end')  # Clear the input entry

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatbotGUI(root)
    root.mainloop()
