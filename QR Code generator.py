import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import qrcode
from PIL import Image, ImageTk
import validators
import os
import io

class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Main container that will hold all frames
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        # Dictionary to store different frames
        self.frames = {}
        
        # Set up the main menu frame
        self.setup_main_menu()
        
        # Store the selected platform
        self.selected_platform = None
        
        # Store the generated QR code
        self.qr_image = None
        self.logo_path = None
        
    def setup_main_menu(self):
        # Create main menu frame
        main_frame = tk.Frame(self.container, bg="#f0f0f0")
        main_frame.pack(pady=20, fill="both", expand=True)
        self.frames["main_menu"] = main_frame
        
        # Title
        title_label = tk.Label(main_frame, text="QR Code Generator", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # Create platform buttons
        platforms = ["YouTube", "Instagram", "WhatsApp", "Twitch", "Discord", "Custom"]
        
        # Create a new frame just for the buttons
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.pack(pady=20)
        
        for platform in platforms:
            # Create platform-specific colors
            colors = {
                "YouTube": ("#FF0000", "#FFFFFF"),  # Red and white
                "Instagram": ("#E1306C", "#FFFFFF"),  # Instagram pink and white
                "WhatsApp": ("#25D366", "#FFFFFF"),  # WhatsApp green and white
                "Twitch": ("#6441A4", "#FFFFFF"),  # Twitch purple and white
                "Discord": ("#5865F2", "#FFFFFF"),  # Discord blue and white
                "Custom": ("#333333", "#FFFFFF"),  # Dark grey and white
            }
            
            button = tk.Button(
                buttons_frame, 
                text=platform,
                width=20,
                height=2,
                font=("Helvetica", 12),
                bg=colors[platform][0],
                fg=colors[platform][1],
                command=lambda p=platform: self.open_platform_page(p)
            )
            button.pack(pady=10)
    
    def open_platform_page(self, platform):
        # Store the selected platform
        self.selected_platform = platform
        
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Check if URL frame already exists
        if "url_frame" not in self.frames:
            url_frame = tk.Frame(self.container, bg="#f0f0f0")
            self.frames["url_frame"] = url_frame
            
            # Add a back button
            back_button = tk.Button(url_frame, text="Back", command=self.go_back_to_main)
            back_button.pack(anchor="nw", padx=10, pady=10)
            
            # Add a title with the selected platform
            platform_label = tk.Label(url_frame, text=f"Generate QR Code for {platform}", 
                                    font=("Helvetica", 18, "bold"), bg="#f0f0f0")
            platform_label.pack(pady=20)
            
            # URL entry
            url_label = tk.Label(url_frame, text="Enter URL:", font=("Helvetica", 12), bg="#f0f0f0")
            url_label.pack(pady=5)
            
            self.url_entry = tk.Entry(url_frame, width=50, font=("Helvetica", 12))
            self.url_entry.pack(pady=10)
            
            # Prefill URL based on platform
            prefill_urls = {
                "YouTube": "https://www.youtube.com/",
                "Instagram": "https://www.instagram.com/",
                "WhatsApp": "https://wa.me/",
                "Twitch": "https://www.twitch.tv/",
                "Discord": "https://discord.gg/",
                "Custom": "https://"
            }
            self.url_entry.insert(0, prefill_urls.get(platform, "https://"))
            
            # For custom option, add a button to upload logo
            if platform == "Custom":
                logo_button = tk.Button(url_frame, text="Upload Logo", command=self.upload_logo)
                logo_button.pack(pady=10)
                
                self.logo_label = tk.Label(url_frame, text="No logo selected", bg="#f0f0f0")
                self.logo_label.pack(pady=5)
            
            # Generate button
            generate_button = tk.Button(url_frame, text="Generate QR Code", 
                                      command=self.generate_and_display,
                                      bg="#4CAF50", fg="white", font=("Helvetica", 12),
                                      width=20, height=2)
            generate_button.pack(pady=20)
            
            # Area to display the QR code
            self.qr_display_label = tk.Label(url_frame, bg="#f0f0f0")
            self.qr_display_label.pack(pady=20)
            
            # Save button (initially hidden)
            self.save_button = tk.Button(url_frame, text="Save QR Code", 
                                       command=self.save_qr_code,
                                       bg="#2196F3", fg="white", font=("Helvetica", 12),
                                       width=20, height=2)
            self.save_button.pack(pady=10)
            self.save_button.pack_forget()  # Hide initially
        else:
            # Update existing frame for the selected platform
            platform_label = self.frames["url_frame"].winfo_children()[2]  # The platform label
            platform_label.config(text=f"Generate QR Code for {platform}")
            
            # Clear previous QR code
            self.qr_display_label.config(image=None)
            self.save_button.pack_forget()
            
            # Update URL entry with platform-specific prefix
            self.url_entry.delete(0, tk.END)
            prefill_urls = {
                "YouTube": "https://www.youtube.com/",
                "Instagram": "https://www.instagram.com/",
                "WhatsApp": "https://wa.me/",
                "Twitch": "https://www.twitch.tv/",
                "Discord": "https://discord.gg/",
                "Custom": "https://"
            }
            self.url_entry.insert(0, prefill_urls.get(platform, "https://"))
            
            # Show/hide logo upload button
            logo_button_exists = len(self.frames["url_frame"].winfo_children()) > 6
            if platform == "Custom" and not logo_button_exists:
                logo_button = tk.Button(self.frames["url_frame"], text="Upload Logo", command=self.upload_logo)
                logo_button.pack(after=self.url_entry)
                
                self.logo_label = tk.Label(self.frames["url_frame"], text="No logo selected", bg="#f0f0f0")
                self.logo_label.pack(after=logo_button)
                
        # Show the URL frame
        self.frames["url_frame"].pack(fill="both", expand=True)
    
    def go_back_to_main(self):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show main menu
        self.frames["main_menu"].pack(fill="both", expand=True)
        
        # Clear stored logo path
        self.logo_path = None
    
    def upload_logo(self):
        # Open file dialog to select an image
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.gif")]
        self.logo_path = filedialog.askopenfilename(filetypes=filetypes)
        
        if self.logo_path:
            # Update the logo label
            filename = os.path.basename(self.logo_path)
            self.logo_label.config(text=f"Selected logo: {filename}")
    
    def validate_url(self, url):
        # Using validators library to check if URL is valid
        if validators.url(url):
            return True
        else:
            messagebox.showerror("Invalid URL", "Please enter a valid URL starting with http:// or https://")
            return False
    
    def generate_and_display(self):
        url = self.url_entry.get().strip()
        
        if not self.validate_url(url):
            return
        
        # Generate QR code
        qr_img = self.generate_qr_code(url, self.logo_path if self.selected_platform == "Custom" else None)
        
        if qr_img:
            # Convert PIL image to Tkinter PhotoImage
            self.qr_image = ImageTk.PhotoImage(qr_img)
            
            # Display the QR code
            self.qr_display_label.config(image=self.qr_image)
            
            # Show save button
            self.save_button.pack(pady=10)
    
    def generate_qr_code(self, url, logo_path=None):
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            
            # Add data to the QR code
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create an image from the QR code
            img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
            
            # If logo is provided, add it to the center of QR code
            if logo_path and os.path.exists(logo_path):
                img = self.add_logo_to_qr(img, logo_path)
            
            # Resize for display
            img = img.resize((300, 300), Image.LANCZOS)
            
            return img
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None
    
    def add_logo_to_qr(self, qr_img, logo_path):
        try:
            # Open the logo image
            logo = Image.open(logo_path)
            
            # Calculate logo size (about 1/4 of the QR code)
            logo_size = int(qr_img.size[0] / 4)
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            # Make sure the logo has an alpha channel
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Calculate position to put the logo
            pos = ((qr_img.size[0] - logo.size[0]) // 2,
                  (qr_img.size[1] - logo.size[1]) // 2)
            
            # Create a new image for the combined QR code and logo
            combined = Image.new('RGBA', qr_img.size, (0, 0, 0, 0))
            combined.paste(qr_img, (0, 0))
            combined.paste(logo, pos, logo)
            
            return combined
            
        except Exception as e:
            messagebox.showerror("Error", f"An error adding logo: {str(e)}")
            return qr_img
    
    def save_qr_code(self):
        if not self.qr_image:
            messagebox.showerror("Error", "No QR code to save")
            return
        
        # Open file dialog to save the QR code
        filetypes = [("PNG files", "*.png"), ("All files", "*.*")]
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        
        if save_path:
            try:
                # Save the PIL image
                img = ImageTk.getimage(self.qr_image)
                img.save(save_path)
                messagebox.showinfo("Success", f"QR code saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()