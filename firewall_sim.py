import tkinter as tk
from tkinter import messagebox
import mysql.connector

class FirewallSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Firewall Simulator")
        self.root.geometry("400x300")  # Basic window size

        # Database connection
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Fluffy14",
                database="cert_study"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect: {err}")
            self.root.destroy()
            return

        # GUI elements
        # Source IP
        tk.Label(root, text="Source IP:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.source_ip_entry = tk.Entry(root)
        self.source_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        # Destination IP
        tk.Label(root, text="Destination IP:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.dest_ip_entry = tk.Entry(root)
        self.dest_ip_entry.grid(row=1, column=1, padx=5, pady=5)

        # Port
        tk.Label(root, text="Port:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5)

        # Protocol
        tk.Label(root, text="Protocol:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.protocol_var = tk.StringVar(value="TCP")
        tk.OptionMenu(root, self.protocol_var, "TCP", "UDP", "ICMP").grid(row=3, column=1, padx=5, pady=5)

        # Check button
        tk.Button(root, text="Check Packet", command=self.check_packet).grid(row=4, column=0, columnspan=2, pady=10)

        # Result label
        self.result_label = tk.Label(root, text="Result: None", fg="black")
        self.result_label.grid(row=5, column=0, columnspan=2, pady=5)

    def check_packet(self):
        # Get user input
        source_ip = self.source_ip_entry.get().strip()
        dest_ip = self.dest_ip_entry.get().strip()
        port = self.port_entry.get().strip()
        protocol = self.protocol_var.get()

        # Input validation
        if not all([source_ip, dest_ip, port]):
            messagebox.showwarning("Input Error", "All fields are required!")
            return
        try:
            port = int(port)
            if port < 0 or port > 65535:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Port must be a number between 0 and 65535!")
            return

        # Fetch rules from database, sorted by priority
        try:
            self.cursor.execute(
                "SELECT source_ip, dest_ip, port, protocol, action, description "
                "FROM firewall_rules ORDER BY priority ASC"
            )
            rules = self.cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to query rules: {err}")
            return

        # Check rules (exact matching for simplicity)
        for rule in rules:
            rule_source, rule_dest, rule_port, rule_protocol, action, description = rule
            if (source_ip == rule_source and
                dest_ip == rule_dest and
                port == rule_port and
                protocol == rule_protocol):
                action_text = action.upper()
                result_text = f"Result: Packet {action_text}"
                if description:
                    result_text += f" ({description})"
                self.result_label.config(
                    text=result_text,
                    fg="green" if action_text == "ALLOW" else "red"
                )
                return

        # Default action if no rule matches
        self.result_label.config(text="Result: Packet DENIED (no matching rule)", fg="red")

    def __del__(self):
        if hasattr(self, 'db') and self.db.is_connected():
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallSimulator(root)
    root.mainloop()