import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
import random
import json
from PIL import Image, ImageTk
import os

class NetworkSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Simulator")
        self.devices = []
        self.max_devices = 10
        self.ip_counter = 10  # For assigning IPs like 192.168.1.10
        self.server_ip_counter = 10  # For server IPs like 10.0.0.10
        self.firewall_rules = []  # Start with empty rules
        self.connections = []  # Store device connections
        self.prompt = None
        self.db = None  # Initialize db as None
        self.icons = {}  # Store device icons

        # Database connection
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="Fluffy14",  # Replace with your MySQL password
                database="cert_study"
            )
            self.cursor = self.db.cursor()
            # Clear firewall rules from database on startup
            self.cursor.execute("DELETE FROM firewall_rules WHERE scenario_id = 1")
            self.db.commit()
            print("Cleared firewall rules from database.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            raise

        # Load icons
        self.load_icons()

        # GUI setup
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(pady=10)

        # Control frame
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Configure Firewall", command=self.configure_firewall).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Test Network", command=self.test_network).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Simulate Attack", command=self.simulate_attack).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Give Prompt", command=self.give_prompt).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Give Answer", command=self.give_answer).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear Network", command=self.clear_network).pack(side=tk.LEFT, padx=5)

    def load_icons(self):
        icon_info = {
            "Desktop": {"path": "desktop.png", "color": "blue"},
            "Server": {"path": "server.png", "color": "green"},
            "Router": {"path": "router.png", "color": "yellow"},
            "Firewall": {"path": "firewall.png", "color": "red"}
        }
        
        for device_type, info in icon_info.items():
            try:
                img = Image.open(info["path"]).resize((50, 50), Image.Resampling.LANCZOS)
                self.icons[device_type] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                print(f"Warning: {info['path']} not found. Using colored oval for {device_type}.")
                self.icons[device_type] = {"color": info["color"]}

    def add_item(self):
        if len(self.devices) >= self.max_devices:
            messagebox.showerror("Error", "Maximum of 10 devices reached!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Device")
        dialog.geometry("200x200")
        
        tk.Label(dialog, text="Select Device Type:").pack(pady=5)
        device_types = ["Desktop", "Server", "Router", "Firewall"]
        for device_type in device_types:
            tk.Button(dialog, text=device_type, 
                     command=lambda dt=device_type: self.add_device(dt, dialog)).pack(pady=2)

    def add_device(self, device_type, dialog):
        dialog.destroy()
        x, y = random.randint(50, 750), random.randint(50, 550)
        ip = None
        if device_type == "Desktop":
            ip = f"192.168.1.{self.ip_counter}"
            self.ip_counter += 1
        elif device_type == "Server":
            ip = f"10.0.0.{self.server_ip_counter}"
            self.server_ip_counter += 1
        elif device_type == "Firewall":
            if any(d["type"] == "Firewall" for d in self.devices):
                messagebox.showerror("Error", "Only one firewall allowed!")
                return

        if isinstance(self.icons[device_type], ImageTk.PhotoImage):
            device_id = self.canvas.create_image(x, y, image=self.icons[device_type], tags=device_type)
        else:
            device_id = self.canvas.create_oval(
                x-25, y-25, x+25, y+25, fill=self.icons[device_type]["color"], tags=device_type
            )

        device = {
            "type": device_type,
            "ip": ip,
            "x": x,
            "y": y,
            "id": device_id,
            "text_id": self.canvas.create_text(x, y+30, text=f"{device_type}\n{ip or ''}")
        }
        self.devices.append(device)
        
        self.canvas.tag_bind(device["id"], "<B1-Motion>", lambda e: self.drag_device(e, device))
        self.canvas.tag_bind(device["text_id"], "<B1-Motion>", lambda e: self.drag_device(e, device))
        self.canvas.tag_bind(device["id"], "<Double-Button-1>", lambda e: self.show_device_info(device))
        self.canvas.tag_bind(device["text_id"], "<Double-Button-1>", lambda e: self.show_device_info(device))

        self.update_connections()

    def show_device_info(self, device):
        ip_text = device["ip"] if device["ip"] else "No IP assigned"
        messagebox.showinfo("Device Info", f"Device: {device['type']}\nIP: {ip_text}")

    def drag_device(self, event, device):
        if isinstance(self.icons[device["type"]], ImageTk.PhotoImage):
            self.canvas.coords(device["id"], event.x, event.y)
        else:
            self.canvas.coords(device["id"], event.x-25, event.y-25, event.x+25, event.y+25)
        self.canvas.coords(device["text_id"], event.x, event.y+30)
        device["x"], device["y"] = event.x, event.y
        self.update_connections()

    def update_connections(self):
        for conn_id in self.connections:
            self.canvas.delete(conn_id)
        self.connections.clear()

        router = next((d for d in self.devices if d["type"] == "Router"), None)
        firewall = next((d for d in self.devices if d["type"] == "Firewall"), None)
        hub = firewall or router
        if hub:
            for device in self.devices:
                if device != hub and device["type"] not in ["Router", "Firewall"]:
                    conn_id = self.canvas.create_line(
                        hub["x"], hub["y"], device["x"], device["y"], fill="black"
                    )
                    self.connections.append(conn_id)

    def configure_firewall(self):
        firewall = next((d for d in self.devices if d["type"] == "Firewall"), None)
        if not firewall:
            messagebox.showerror("Error", "No firewall in the network!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Firewall")
        dialog.geometry("400x400")

        tk.Label(dialog, text="Firewall Rules").pack(pady=5)
        tree = ttk.Treeview(dialog, columns=("Source", "Dest", "Port", "Protocol", "Action"), show="headings")
        tree.heading("Source", text="Source IP")
        tree.heading("Dest", text="Dest IP")
        tree.heading("Port", text="Port")
        tree.heading("Protocol", text="Protocol")
        tree.heading("Action", text="Action")
        tree.pack(fill=tk.BOTH, expand=True)

        for rule in self.firewall_rules:
            tree.insert("", tk.END, values=(
                rule["source_ip"], rule["dest_ip"], rule["port"], rule["protocol"], rule["action"]
            ))

        def add_rule():
            source_ip = simpledialog.askstring("Input", "Source IP (e.g., 192.168.1.10 or any)", parent=dialog)
            dest_ip = simpledialog.askstring("Input", "Destination IP (e.g., 10.0.0.10 or any)", parent=dialog)
            port = simpledialog.askinteger("Input", "Port (e.g., 80, 0 for any)", parent=dialog)
            protocol = simpledialog.askstring("Input", "Protocol (TCP/UDP/ANY)", parent=dialog)
            action = simpledialog.askstring("Input", "Action (allow/deny)", parent=dialog)
            if all([source_ip, dest_ip, port is not None, protocol, action]):
                rule = {
                    "source_ip": source_ip.lower(),
                    "dest_ip": dest_ip.lower(),
                    "port": port,
                    "protocol": protocol.upper(),
                    "action": action.lower()
                }
                self.firewall_rules.append(rule)
                tree.insert("", tk.END, values=(source_ip, dest_ip, port, protocol.upper(), action.lower()))
                try:
                    self.cursor.execute(
                        """
                        INSERT INTO firewall_rules (scenario_id, source_ip, dest_ip, port, protocol, action, priority)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (1, source_ip.lower(), dest_ip.lower(), port, protocol.upper(), action.lower(), len(self.firewall_rules))
                    )
                    self.db.commit()
                    print(f"Added rule: {rule}")
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Failed to save rule: {err}")

        tk.Button(dialog, text="Add Rule", command=add_rule).pack(pady=5)
        tk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)

    def test_network(self):
        firewall = next((d for d in self.devices if d["type"] == "Firewall"), None)
        desktops = [d for d in self.devices if d["type"] == "Desktop"]
        servers = [d for d in self.devices if d["type"] == "Server"]

        if not desktops or not servers:
            messagebox.showerror("Error", "Network requires at least one desktop and one server!")
            return

        for desktop in desktops:
            for server in servers:
                success = True
                if firewall:
                    allowed = False
                    for rule in self.firewall_rules:
                        if (rule["source_ip"] in [desktop["ip"], "any"] and
                            rule["dest_ip"] in [server["ip"], "any"] and
                            rule["port"] in [80, 0] and
                            rule["protocol"] in ["TCP", "ANY"] and
                            rule["action"] == "allow"):
                            allowed = True
                            break
                    if not allowed:
                        success = False
                    print(f"Test network: Rule match for {desktop['ip']} -> {server['ip']} port 80: {allowed}")

                self.animate_transfer(desktop, server, success)

        messagebox.showinfo("Test Result", "Network test completed. Check animations for results.")

    def animate_transfer(self, source, dest, success):
        hub = next((d for d in self.devices if d["type"] in ["Firewall", "Router"]), None)
        if not hub:
            return

        color = "green" if success else "red"
        total_duration = 5000  # 5 seconds
        dot_interval = 500  # 0.5 seconds
        steps_per_segment = 20
        total_steps = steps_per_segment * 2

        def animate_dot(start_time):
            dot = self.canvas.create_oval(source["x"]-5, source["y"]-5, source["x"]+5, source["y"]+5, fill=color)
            
            dx1 = (hub["x"] - source["x"]) / steps_per_segment
            dy1 = (hub["y"] - source["y"]) / steps_per_segment
            dx2 = (dest["x"] - hub["x"]) / steps_per_segment
            dy2 = (dest["y"] - hub["y"]) / steps_per_segment

            def move_dot(step=0):
                if step < steps_per_segment:
                    self.canvas.move(dot, dx1, dy1)
                    self.root.after(50, move_dot, step+1)
                elif step < total_steps:
                    self.canvas.move(dot, dx2, dy2)
                    self.root.after(50, move_dot, step+1)
                else:
                    self.canvas.delete(dot)

            move_dot()

        for i in range(0, total_duration, dot_interval):
            self.root.after(i, animate_dot, i)

    def simulate_attack(self):
        firewall = next((d for d in self.devices if d["type"] == "Firewall"), None)
        servers = [d for d in self.devices if d["type"] == "Server"]

        if not servers:
            messagebox.showerror("Error", "No servers to attack!")
            return

        for server in servers:
            blocked = False
            if firewall:
                print(f"Checking rules for attack to {server['ip']} port 23:")
                for rule in self.firewall_rules:
                    print(f"  Rule: {rule}")
                    if (rule["source_ip"] == "any" and
                        rule["dest_ip"] in [server["ip"], "any"] and
                        rule["port"] in [23, 0] and
                        rule["protocol"] in ["TCP", "ANY"] and
                        rule["action"] == "deny"):
                        blocked = True
                        break
                print(f"Attack simulation: Rule match for any -> {server['ip']} port 23: {blocked}")

            self.animate_attack(server, blocked)

        messagebox.showinfo("Attack Result", "Attack simulation completed. Green = blocked, Red = success.")

    def animate_attack(self, target, blocked):
        hub = next((d for d in self.devices if d["type"] in ["Firewall", "Router"]), None)
        if not hub:
            return

        color = "green" if blocked else "red"
        total_duration = 5000
        dot_interval = 500
        steps_per_segment = 20
        total_steps = steps_per_segment * 2
        start_x, start_y = 400, 0

        def animate_dot(start_time):
            dot = self.canvas.create_oval(start_x-5, start_y-5, start_x+5, start_y+5, fill=color)
            
            dx1 = (hub["x"] - start_x) / steps_per_segment
            dy1 = (hub["y"] - start_y) / steps_per_segment
            dx2 = (target["x"] - hub["x"]) / steps_per_segment
            dy2 = (target["y"] - hub["y"]) / steps_per_segment

            def move_dot(step=0):
                if step < steps_per_segment:
                    self.canvas.move(dot, dx1, dy1)
                    self.root.after(50, move_dot, step+1)
                elif step < total_steps:
                    self.canvas.move(dot, dx2, dy2)
                    self.root.after(50, move_dot, step+1)
                else:
                    self.canvas.delete(dot)

            move_dot()

        for i in range(0, total_duration, dot_interval):
            self.root.after(i, animate_dot, i)

    def give_prompt(self):
        self.cursor.execute("SELECT prompt_text, solution FROM prompts WHERE scenario_id = 1 ORDER BY RAND() LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            prompt_text, solution = result
            self.prompt = {"text": prompt_text, "solution": json.loads(solution)}
            messagebox.showinfo("Prompt", prompt_text)
        else:
            messagebox.showerror("Error", "No prompts available!")

    def give_answer(self):
        if not self.prompt:
            messagebox.showerror("Error", "No active prompt! Click 'Give Prompt' first.")
            return
        
        solution = self.prompt["solution"]
        answer_text = "Solution to the prompt:\n\n"
        
        if "firewall_rules" in solution:
            answer_text += "Required Firewall Rules:\n"
            for rule in solution["firewall_rules"]:
                answer_text += (f"- Source: {rule['source_ip']}, "
                               f"Dest: {rule['dest_ip']}, "
                               f"Port: {rule['port']}, "
                               f"Protocol: {rule['protocol']}, "
                               f"Action: {rule['action']}\n")
        else:
            answer_text += "No specific firewall rules provided in solution.\n"
        
        messagebox.showinfo("Prompt Solution", answer_text)

    def clear_network(self):
        self.canvas.delete("all")
        self.devices.clear()
        self.firewall_rules.clear()
        self.connections.clear()
        self.ip_counter = 10
        self.server_ip_counter = 10
        self.prompt = None
        # Clear firewall rules from database
        try:
            self.cursor.execute("DELETE FROM firewall_rules WHERE scenario_id = 1")
            self.db.commit()
            print("Cleared firewall rules from database.")
        except mysql.connector.Error as err:
            print(f"Error clearing firewall rules: {err}")

    def __del__(self):
        if hasattr(self, 'db') and self.db is not None:
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkSimulator(root)
    root.mainloop()