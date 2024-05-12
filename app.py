import threading
import tkinter as tk
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    WebDriverException, 
    NoSuchWindowException
)

from utils import open_chrome_window, start_tracking



class ArticleApp:
    """Tkinter app that runs the selenium program in a separate thread which it can be killed at any point by quitting the driver and cleaning up resources."""

    def __init__(self, master):
        self.master = master
        master.title("Article Change")
        master.geometry("400x150")

        # Input label and field
        self.input_label = tk.Label(master, text="Enter URL:")
        self.input_label.pack(pady=5)
        self.input_field = tk.Entry(master, width=50)
        self.input_field.pack(pady=5)

        # Frame for start and stop buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack()
        
        # Start and stop buttons
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_app)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_app)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        # App status label
        self.app_status = tk.Label(master, text="")
        self.app_status.pack(pady=5)

        self.driver = None
        self.selenium_thread = None
        self.stop_event = threading.Event()

        master.protocol("WM_DELETE_WINDOW", self.on_close)


    def start_app(self):
        """Function to start the application"""

        self.start_button.config(state=tk.DISABLED)

        self.selenium_thread = threading.Thread(target=self.main_tracker)
        self.selenium_thread.start()
        self.stop_button.config(state=tk.NORMAL)
        
        self.app_status.config(text="Tracking changes...")


    def stop_app(self):
        """Function to stop the application"""

        self.stop_event.set()

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.app_status.config(text="")

        self.stop_event.clear()


    def on_close(self):
        """Function to handle window close event"""

        self.stop_event.set()
        self.master.destroy()


    def main_tracker(self):
        """Main procedure, call this after clicking the GUI start button upon entering the site URL"""

        # CREATE THE WEB DRIVER INSTANCE
        self.driver = open_chrome_window()

        try:
            # LAUNCH ARTICLE PAGE
            url = self.input_field.get()
            self.driver.get(url)

            # ORIGINAL HTML CONTENT
            original_html = self.driver.page_source
            original_text = self.driver.find_element(By.TAG_NAME, "body").text.strip()

            # SAVE ORIGINAL HTML CONTENT
            with open('original.html', 'w', encoding='utf-8') as file:
                file.write(original_html)

            # START TRACKING CHANGES
            start_tracking(self.driver, original_text, self.stop_event)
            self.stop_app()
            print('-> Tracking stopped.')

        except NoSuchWindowException:
            print("-> The web driver window was closed.")

        except WebDriverException as e:
            err_message = ''.join(e.msg.split('(')).split(':')[3]
            message = err_message.split('\n')[0]
            print(f"=> A web driver error has occcured: {message}")

        finally:
            if self.driver:
                self.driver.quit()
            print('-> Driver quit.')


root = tk.Tk()
app = ArticleApp(root)
root.mainloop()
