import csv
from datetime import datetime
from tkinter import *
from tkinter import messagebox  # Import messagebox for displaying company details
from PIL import ImageTk, Image
import cv2
import threading
import os
import random
import time

def calculate_wages(in_time, out_time):
    if in_time is None or out_time is None:
        return 0
    else:
        # Calculate the working hours
        hours = (out_time - in_time).total_seconds() / 3600
        # Assuming the hourly wage is ₹100
        wage_rate = 100
        wages = hours * wage_rate
        return wages

def record_attendance(rfid_code):
    # Get the current timestamp
    current_time = datetime.now()
    # Check if the worker is clocking in or out
    if rfid_code in attendance_data:
        # Clocking out
        in_time, image_path = attendance_data[rfid_code]
        out_time = current_time
        # Calculate the wages
        wages = calculate_wages(in_time, out_time)
        # Remove the worker's attendance record
        del attendance_data[rfid_code]
        # Save the attendance and wages in the CSV file
        with open('attendance.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([rfid_code, in_time, out_time, wages])
        output_label.config(text=f"Worker with RFID code {rfid_code} has clocked out.\nWages calculated: ₹{wages:.2f}")
        # Display the captured image
        if image_path:
            image = Image.open(image_path)
            image = ImageTk.PhotoImage(image)
            image_label.config(image=image)
            image_label.image = image
    else:
        # Clocking in
        attendance_data[rfid_code] = (current_time, None)
        output_label.config(text=f"Worker with RFID code {rfid_code} has clocked in.")

def scan_rfid():
    rfid = rfid_entry.get()
    if rfid:
        record_attendance(rfid)
    rfid_entry.delete(0, 'end')

def capture_image(rfid_code, video_label_login):
    def update_image():
        ret, frame = video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (320, 240))
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            video_label_login.config(image=photo)
            video_label_login.image = photo
            root.after(30, update_image)  # Schedule the update after 30 milliseconds

    video = cv2.VideoCapture(0)
    update_image()

def login_page():
    # Hide the home page frame
    home_frame.pack_forget()

    # Show the attendance frame
    attendance_frame.pack()

    # Get the RFID code entered by the user
    rfid_code = rfid_entry.get()

    # Create a label for displaying the video feed
    video_label_login = Label(attendance_frame, bg="blue")
    video_label_login.pack(side=LEFT, padx=10, pady=10)

    # Start the video capture thread with RFID code as argument
    video_thread = threading.Thread(target=capture_image, args=(rfid_code, video_label_login))
    video_thread.start()

    # Check if the back button already exists
    if not attendance_frame.children.get("back_button"):
        # Create a back button to return to the home page
        back_button = Button(attendance_frame, text="Back", font=("Helvetica", 16), command=back_to_home, name="back_button")
        back_button.pack(side=BOTTOM, pady=10)

def back_to_home():
    # Unhide the home page frame
    attendance_frame.pack_forget()
    home_frame.pack()

    # Remove the back button if it exists
    if attendance_frame.children.get("back_button"):
        attendance_frame.children["back_button"].destroy()
def login_page():
    # Hide the home page frame
    home_frame.pack_forget()

    # Show the attendance frame
    attendance_frame.pack()

    # Get the RFID code entered by the user
    rfid_code = rfid_entry.get()

    # Create a label for displaying the video feed if it doesn't exist
    if not attendance_frame.children.get("video_label_login"):
        video_label_login = Label(attendance_frame, bg="blue", name="video_label_login")
        video_label_login.pack(side=LEFT, padx=10, pady=10)

        # Start the video capture thread with RFID code as argument
        video_thread = threading.Thread(target=capture_image, args=(rfid_code, video_label_login))
        video_thread.start()

    # Check if the back button already exists
    if not attendance_frame.children.get("back_button"):
        # Create a back button to return to the home page
        back_button = Button(attendance_frame, text="Back", font=("Helvetica", 16), command=back_to_home, name="back_button")
        back_button.pack(side=BOTTOM, pady=10)

def back_to_home():
    # Unhide the home page frame
    attendance_frame.pack_forget()
    home_frame.pack()

def exit_program():
    root.destroy()

def change_colors():
    # Generate random RGB color values
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    # Convert RGB values to hexadecimal color code
    bg_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    text_color = '#{:02x}{:02x}{:02x}'.format(255 - r, 255 - g, 255 - b)
    # Configure the company name label with the new color
    company_name_label.config(fg=text_color)
    # Change the background color of the attendance frame
    attendance_frame.config(bg=bg_color)
    # Schedule the next color change after 5 seconds
    root.after(5000, change_colors)

def calculate_wages_page():
    # Create a new window for entering the RFID code
    calculate_wages_window = Toplevel(root)
    calculate_wages_window.title("Calculate Wages")
    calculate_wages_window.geometry("300x150")

    # Function to calculate wages when the user presses the "Calculate" button
    def calculate_wages():
        rfid_code = rfid_entry.get()
        if rfid_code:
            # Check if the provided RFID code exists in the attendance data
            if rfid_code in attendance_data:
                # Get the clock-in and clock-out times for the provided RFID code
                in_time, out_time = attendance_data[rfid_code]
                # Check if both clock-in and clock-out times are available
                if in_time and out_time:
                    # Calculate wages based on the difference between clock-in and clock-out times
                    wages = calculate_wages(in_time, out_time)
                    # Display the calculated wages
                    messagebox.showinfo("Wages Calculation", f"Wages for RFID code {rfid_code}: ₹{wages:.2f}")
                else:
                    messagebox.showerror("Error", f"Clock-in or clock-out time missing for RFID code {rfid_code}.")
            else:
                messagebox.showerror("Error", "RFID code not found in attendance records.")
        else:
            messagebox.showerror("Error", "Please enter a valid RFID code.")

    # Label and entry field for entering RFID code
    rfid_label = Label(calculate_wages_window, text="Enter RFID code:")
    rfid_label.pack(pady=5)
    rfid_entry = Entry(calculate_wages_window, width=20)
    rfid_entry.pack(pady=5)

    # Button to calculate wages
    calculate_button = Button(calculate_wages_window, text="Calculate", command=calculate_wages)
    calculate_button.pack(pady=10)

def show_company_details():
    company_details = """
    Company Details:
    - Name: Sabari printers
    - Address: KSC school Road, Tirupur
    - Products: Printing services
    - Contact: 1234567890
    """
    messagebox.showinfo("About Company", company_details)

# Create the main window
root = Tk()
root.title("Worker Attendance System by RB")
root.attributes('-fullscreen', True)  # Set the window to fullscreen
root.config(bg="blue")  # Set background color

# Create a frame for the home page
home_frame = Frame(root, bg="blue")
home_frame.pack(pady=50)

# Create a frame for the attendance page
attendance_frame = Frame(root, bg="blue")

# Load the company logo images
logo_image = Image.open('picture.jpg')
zoomed_in_logo = ImageTk.PhotoImage(logo_image.resize((200, 200)))
zoomed_out_logo = ImageTk.PhotoImage(logo_image.resize((100, 100)))

# Create a label for the company logo
logo_label = Label(home_frame, image=zoomed_in_logo, bg="blue")
logo_label.grid(row=0, column=0, pady=20)

# Create buttons for different actions
login_button = Button(home_frame, text="Login", font=("Helvetica", 16), command=login_page, width=15, height=2)
login_button.grid(row=1, column=0, pady=10)

exit_button = Button(home_frame, text="Exit", font=("Helvetica", 16), command=exit_program, width=15, height=2)
exit_button.grid(row=2, column=0, pady=10)

wages_button = Button(home_frame, text="Calculate Wages", font=("Helvetica", 16), command=calculate_wages_page,
                      width=15, height=2)
wages_button.grid(row=3, column=0, pady=10)

about_company_button = Button(home_frame, text="About Company", font=("Helvetica", 16), command=show_company_details,
                              width=15, height=2)
about_company_button.grid(row=4, column=0, pady=10)

# Create a label for the company name
company_name_label = Label(attendance_frame, text="Sabari printers, KSC school Road, Tirupur", font=("Helvetica", 20),
                           bg="blue", fg="white")
company_name_label.pack(pady=10)

# Create a frame for the buttons
button_frame = Frame(attendance_frame, bg="blue")
button_frame.pack(pady=10)

# Create buttons for different actions
clock_in_out_button = Button(button_frame, text="Scan RFID", font=("Helvetica", 16), command=scan_rfid)
clock_in_out_button.grid(row=0, column=0, padx=10, pady=10)

exit_button = Button(button_frame, text="Exit", font=("Helvetica", 16), command=exit_program)
exit_button.grid(row=0, column=1, padx=10, pady=10)

# Create the output label
output_label = Label(attendance_frame, font=("Helvetica", 16), bg="blue", fg="white")
output_label.pack(pady=10)

# Create the input field for RFID code
rfid_entry = Entry(attendance_frame, font=("Helvetica", 16))
rfid_entry.pack()

# Create a label for displaying the video
video_label = Label(attendance_frame, bg="blue")
video_label.pack(side=LEFT, padx=10, pady=10)

# Create a label for displaying the captured image
image_label = Label(attendance_frame, bg="blue")
image_label.pack(side=RIGHT, padx=10, pady=10)

# Start the color change animation
change_colors()

# Initialize the attendance data dictionary
attendance_data = {}

# Start the Tkinter event loop
root.mainloop()
