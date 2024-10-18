from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

def apply_dithering(image):
    # Convert image to numpy array
    img_array = np.array(image, dtype=np.float32)
    
    # Get image dimensions
    height, width = img_array.shape
    
    # Define the dithering matrix (Floyd-Steinberg)
    dithering_matrix = np.array([
        [0, 0, 7],
        [3, 5, 1]
    ]) / 16.0
    
    # Apply dithering
    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x]
            new_pixel = 255 if old_pixel > 180 else 0  # Adjust threshold for less dithering
            img_array[y, x] = new_pixel
            quant_error = old_pixel - new_pixel
            
            # Distribute the quantization error
            for dy in range(2):
                for dx in range(3):
                    if x + dx - 1 < 0 or x + dx - 1 >= width or y + dy >= height:
                        continue
                    img_array[y + dy, x + dx - 1] += quant_error * dithering_matrix[dy, dx]
    
    return Image.fromarray(img_array.astype(np.uint8))

def process_image(input_path, output_path):
    # Load the image
    image = Image.open(input_path)
    
    # Convert to grayscale
    grayscale_image = image.convert("L")
    
    # Apply blur
    blurred_image = grayscale_image.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Adjust brightness and contrast to make the image darker and washed out
    enhancer = ImageEnhance.Brightness(blurred_image)
    dark_image = enhancer.enhance(0.6)  # Reduce brightness to 60%
    
    enhancer = ImageEnhance.Contrast(dark_image)
    contrast_image = enhancer.enhance(2.0)  # Increase contrast to 200%
    
    # Apply dithering
    dithered_image = apply_dithering(contrast_image)
    
    # Save the processed image
    dithered_image.save(output_path)

def upload_image():
    global input_path
    input_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
    if input_path:
        img = Image.open(input_path)
        img.thumbnail((200, 200))
        img = ImageTk.PhotoImage(img)
        panel.configure(image=img)
        panel.image = img

def save_image():
    if not input_path:
        messagebox.showerror("Error", "No image uploaded.")
        return
    output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if output_path:
        process_image(input_path, output_path)
        messagebox.showinfo("Success", f"Processed image saved to {output_path}")

if __name__ == "__main__":
    input_path = None

    # Create the main window
    root = tk.Tk()
    root.title("Image Retro-Processing Tool")

    # Create a frame for the buttons
    frame = tk.Frame(root)
    frame.pack(pady=20)

    # Create and pack the buttons
    upload_button = tk.Button(frame, text="Upload Image", command=upload_image)
    upload_button.pack(side=tk.LEFT, padx=10)

    save_button = tk.Button(frame, text="Save Image", command=save_image)
    save_button.pack(side=tk.LEFT, padx=10)

    # Create and pack the image panel
    panel = tk.Label(root)
    panel.pack(pady=20)

    # Run the main loop
    root.mainloop()