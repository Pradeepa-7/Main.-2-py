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


def capture_image(rfid_code):
    video = cv2.VideoCapture(0)
    while True:
        ret, frame = video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (320, 240))
            image = Image.fromarray(frame)
            image_path = f"{rfid_code}.jpg"  # Use the RFID code as the image name
            # Save the image with the correct file extension
            image.save(image_path, "JPEG")
            # Update the attendance data with the image path
            if rfid_code in attendance_data:
                attendance_data[rfid_code] = (attendance_data[rfid_code][0], image_path)
                image = ImageTk.PhotoImage(image)
                video_label.configure(image=image)
                video_label.image = image
        # Sleep for a short duration to avoid high CPU usage
        time.sleep(0.1)


def login_page():
    home_frame.pack_forget()  # Hide the home page frame
    attendance_frame.pack()  # Show the attendance frame
    # Start the video capture thread
    video_thread = threading.Thread(target=capture_image, args=(rfid_entry.get(),))
    video_thread.start()


def exit_program():
    root.destroy()


def zoom_logo(scale):
    if scale < 1.0:
        logo_label.config(image=zoomed_in_logo)
    else:
        logo_label.config(image=zoomed_out_logo)
    logo_label.image = zoomed_in_logo if scale < 1.0 else zoomed_out_logo
    # Schedule the next zoom animation after 1 second
    root.after(1000, lambda: zoom_logo(1.5 if scale < 1.0 else 0.75))


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
    wages_frame = Frame(root)
    rfid_code = rfid_entry.get()
    wages = calculate_wages(attendance_data[rfid_code][0], datetime.now())
    wages_label = Label(wages_frame, text=f"Wages for RFID code {rfid_code}: ₹{wages:.2f}", font=("Helvetica", 16))
    wages_label.pack(pady=10)
    back_button = Button(wages_frame, text="Back", font=("Helvetica", 16), command=lambda: wages_frame.pack_forget())
    back_button.pack(pady=10)
    wages_frame.pack(pady=50)


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

# Load the company logo images
logo_image = Image.open('picture.jpg')
zoomed_in_logo = ImageTk.PhotoImage(logo_image.resize((200, 200)))
zoomed_out_logo = ImageTk.PhotoImage(logo_image.resize((100, 100)))

# Create a label for the company logo
logo_label = Label(root, image=zoomed_in_logo, bg="blue")
logo_label.place(relx=0.5, rely=0.3, anchor=CENTER)

# Create buttons for different actions
login_button = Button(root, text="Login", font=("Helvetica", 16), command=login_page, width=15, height=2)
login_button.place(relx=0.5, rely=0.5, anchor=CENTER)

exit_button = Button(root, text="Exit", font=("Helvetica", 16), command=exit_program, width=15, height=2)
exit_button.place(relx=0.5, rely=0.59, anchor=CENTER)

wages_button = Button(root, text="Calculate Wages", font=("Helvetica", 16), command=calculate_wages_page, width=15, height=2)
wages_button.place(relx=0.5, rely=0.68, anchor=CENTER)

about_company_button = Button(root, text="About Company", font=("Helvetica", 16), command=show_company_details, width=15, height=2)
about_company_button.place(relx=0.5, rely=0.77, anchor=CENTER)

# Create a frame for the attendance page
attendance_frame = Frame(root, bg="blue")

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

# Stop the logo zoom animation
root.after_cancel(zoom_logo)

# Start the color change animation
change_colors()

# Initialize the attendance data dictionary
attendance_data = {}

# Start the Tkinter event loop
root.mainloop()
