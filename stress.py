import ollama
import time
import threading
import queue
import tkinter as tk
from tkinter import ttk

def send_question(index, question, result_queue, model_name):
    start_time = time.time()
    try:
        # Send the request with stream=True and specified model
        response_stream = ollama.generate(model=model_name, prompt=question, stream=True)
        # Get the first part of the answer
        first_chunk = next(response_stream)
        end_time = time.time()
        latency = end_time - start_time

        # Put the result in the queue
        result_queue.put((index, latency))
    except Exception as e:
        print(f"Error in thread {index}: {e}")
        # Indicate an error occurred
        result_queue.put((index, None))

def start_threads(questions, result_queue, model_name):
    for index, question in enumerate(questions):
        thread = threading.Thread(target=send_question, args=(index, question, result_queue, model_name))
        thread.start()

def update_gui(root, result_queue, labels):
    try:
        while True:
            # Try to get result without blocking
            index, latency = result_queue.get_nowait()
            if latency is not None:
                labels[index]['text'] = f"Thread {index}: {latency:.4f} seconds"
            else:
                labels[index]['text'] = f"Thread {index}: Error"
            labels[index]['foreground'] = 'green' if latency is not None else 'red'
            labels[index].update()
    except queue.Empty:
        pass
    finally:
        # Schedule the next GUI update
        root.after(100, update_gui, root, result_queue, labels)

def main():
    # Define the model name
    model_name = 'llama3.1:latest'

    # Generate 12 simple questions
    questions = [f"What is {i} times {i}?" for i in range(1, 13)]

    # Queue to get results from threads
    result_queue = queue.Queue()

    # Start the GUI
    root = tk.Tk()
    root.title("Ollama Stress Test")

    # Create a frame for the labels
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    # Create labels to display thread status
    labels = []
    for i in range(12):
        label = ttk.Label(frame, text=f"Thread {i}: Pending", foreground='blue')
        label.grid(row=i, column=0, sticky=(tk.W))
        labels.append(label)

    # Start threads
    threading.Thread(target=start_threads, args=(questions, result_queue, model_name), daemon=True).start()

    # Start GUI update loop
    root.after(100, update_gui, root, result_queue, labels)

    # Run the GUI event loop
    root.mainloop()

if __name__ == '__main__':
    main()
