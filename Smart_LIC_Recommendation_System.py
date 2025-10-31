import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import sqlite3
import re
import webbrowser
import tkinter.font as tkFont

# ------------------ Data Preparation ------------------
def load_and_prepare_data():
    df = pd.read_csv("C:/Bhavana/project_phase1/LIC_Dataset.csv")

    # Encode categorical columns
    encoders = {}
    for col in ["Smoker_Required", "Health_Check_Required", "Type"]:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # Features to scale and check for NaN
    features = [
        "Sum of Minimum_Age",
        "Sum of Maximum_Age",
        "Sum of Monthly_Premium",
        "Sum of Policy_Term_Years"
    ]
    # Fill missing numerical values with mean
    for col in features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col].fillna(df[col].mean(), inplace=True)

    # Fill missing categorical values with mode
    for col in ["Smoker_Required", "Health_Check_Required", "Type"]:
        if col in df.columns:
            df[col].fillna(df[col].mode()[0], inplace=True)

    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])

    used_cols = features + ["Smoker_Required", "Health_Check_Required"]
    df.dropna(subset=used_cols, inplace=True)

    return df, encoders, scaler

def train_knn_model(df):
    features = [
        "Sum of Minimum_Age",
        "Sum of Maximum_Age",
        "Sum of Monthly_Premium",
        "Sum of Policy_Term_Years",
        "Smoker_Required",
        "Health_Check_Required"
    ]
    knn = NearestNeighbors(n_neighbors=10)
    knn.fit(df[features])
    return knn

# ------------------ Database Functions ------------------
def init_db():
    conn = sqlite3.connect("customer_registration.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_registration(name, email, mobile, location):
    conn = sqlite3.connect("customer_registration.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, email, mobile, location)
        VALUES (?, ?, ?, ?)
    """, (name, email, mobile, location))
    conn.commit()
    conn.close()

def check_duplicate(email, mobile):
    conn = sqlite3.connect("customer_registration.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE email = ? OR mobile = ?", (email, mobile))
    exists = cursor.fetchone()
    conn.close()
    return exists is not None

# ------------------ Policy URLs ------------------
policy_urls = {
    "LIC Jeevan Labh": "https://licindia.in/lic-s-jeevan-labh-plan-no.-936-uin-no.-512n304v02-",
    "LIC Jeevan Lakshya": "https://licindia.in/lic-s-jeevan-lakshya-plan-no.-933-uin-no.-512n297v02-",
    "LIC New Children's Money Back Plan": "https://licindia.in/lic-s-new-children-s-money-back-plan-plan-no.-932-uin-no.-512n296v02-",
    "LIC Jeevan Umang": "https://licindia.in/lics-jeevan-umang-plan-no.-945-uin-no.-512n312v02-",
    "LIC Tech Term": "https://licindia.in/web/guest/lic-s-new-tech-term-954-512n351v01",
    "LIC Jeevan Amar": "https://licindia.in/lic-s-jeevan-amar-plan-no.-855-uin-no.-512n332v01-1",
    "LIC New Endowment Plan": "https://licindia.in/lic-s-new-endowment-plan-no.-914-uin-no.-512n277v02-",
    "LIC Bima Jyoti": "https://licindia.in/lic-s-bima-jyoti-plan-no.-860-uin-no.-512n339v01-",
    "LIC New Bima Bachat": "https://licindia.in/lic-s-new-bima-bachat-plan-no.-916-uin-no.-512n284v02-",
    "LIC Jeevan Tarun": "https://licindia.in/lic-s-jeevan-tarun",
    "LIC Saral Pension": "https://licindia.in/lic-s-saral-pension-plan-no.-862-uin-512n342v03-",
    "LIC Jeevan Shanti": "https://licindia.in/lic-s-new-jeevan-shanti-plan-no.-858-uin-512n338v03-",
    "LIC Aadhaar Stambh": "https://licindia.in/lic-s-aadhaar-stambh-plan-no.-943-uin-no.-512n310v03-",
    "LIC Aadhaar Shila": "https://licindia.in/lic-s-aadhaar-shila-plan-no-844-uin-512n309v01-",
    "LIC Single Premium Endowment Plan": "https://licindia.in/lic-s-single-premium-endowment-plan-plan-no-817-uin-512n283v01-",
    "LIC New Jeevan Anand": "https://licindia.in/lic-s-new-jeevan-anand-plan-no.-915-uin-no.-512n279v02-",
    "LIC Bachat Plus": "https://licindia.in/lic-s-bachat-plus-plan-no.-861-uin-512n340v01-",
    "LIC Dhan Rekha": "https://licindia.in/lic-s-dhan-rekha-plan-no.-863-uin-no.-512n343v01-",
    "LIC Dhan Varsha": "https://licindia.in/lic-s-dhan-varsha-plan-no.-866-uin-no.-512n349v01-",
    "LIC Dhan Sanchay": "https://licindia.in/lic-s-dhan-sanchay-plan-no.-865-uin-512n346v01-",
    "LIC Pension Plus": "https://licindia.in/lic-s-new-pension-plus-867-512l347v01",
    "LIC Saral Jeevan Bima": "https://licindia.in/lic-s-saral-jeevan-bima-plan-no.-859-uin-no.-512n341v01-",
    "LIC Micro Bachat": "https://licindia.in/lic-s-micro-bachat-plan-plan-no.-951-uin-no.-512n329v02-",
    "LIC Bhagya Lakshmi": "https://licindia.in/lic-s-bhagya-lakshmi-plan-no.-939-uin-no.-512n292v04-",
    "LIC Jeevan Mangal": "https://licindia.in/lic-s-new-jeevan-mangal-plan-no.-940-uin-no.-512n287v04-",
    "LIC Pradhan Mantri Vaya Vandana Yojana": "https://licindia.in/hi/pradhan-mantri-vaya-vandana-yojana-plan-no.-856-uin-512g336v01-",
    "LIC Cancer Cover": "https://licindia.in/hi/lic-s-cancer-cover-plan-no.-905-uin-512n314v02-",
    "LIC Anmol Jeevan II": "https://licindia.in/hi/lic-s-anmol-jeevan-ii-plan-no-822-uin-512n285v01-",
    "LIC Amulya Jeevan II": "https://licindia.in/hi/lic-s-amulya-jeevan-ii-plan-no.-823-uin-512n286v01-",
    "LIC New Money Back Plan - 20 Years": "https://licindia.in/hi/the-money-back-policy-20-years-plan-no.-75-uin-512n066v01-",
    "LIC New Money Back Plan - 25 Years": "https://licindia.in/hi/lic-s-new-money-back-plan-25-years-plan-no.-821-uin-no.-512n278v01-",
}

def get_policy_url(policy_name):
    for url_name in policy_urls:
        if url_name.lower() in str(policy_name).lower():
            return policy_urls[url_name]
    return None

# ------------------ App Class ------------------
class LICRecommenderApp:
    def __init__(self, root):
        init_db()
        self.df, self.encoders, self.scaler = load_and_prepare_data()
        self.knn = train_knn_model(self.df)
        self.customer_data = {}

        self.root = root
        self.root.title("LIC Policy Recommender")
        self.root.geometry("1050x800")
        self.root.configure(bg="#f0fdff")

        # Custom fonts
        self.heading_font = tkFont.Font(family="Calibri", size=24, weight="bold")
        self.section_font = tkFont.Font(family="Verdana", size=14, weight="bold")
        self.label_font = tkFont.Font(family="Segoe UI", size=12)
        self.textbox_font = tkFont.Font(family="Consolas", size=12)
        self.button_font = tkFont.Font(family="Verdana", size=13, weight="bold")

        # Custom ttk styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#f0fdff", font=self.label_font)
        self.style.configure("TEntry",
                             padding=8,
                             font=self.textbox_font,
                             foreground="#1d3557",
                             fieldbackground="#e0f7fa",
                             borderwidth=3,
                             relief="groove")
        self.style.configure("TButton",
                             font=self.button_font,
                             foreground="white",
                             background="#457b9d",
                             borderwidth=2,
                             padding=8)
        self.style.map("TButton",
                       background=[("active", "#1d3557")])

        self.create_registration_window()

    def create_registration_window(self):
        self.clear_window()
        # Top Banner
        banner = tk.Frame(self.root, bg="#457b9d")
        banner.pack(fill="x")
        tk.Label(banner, text="LIC Policy Recommender", font=self.heading_font, bg="#457b9d", fg="#f1faee").pack(pady=14)

        # Registration Section
        reg_frame = tk.Frame(self.root, bg="#e0f7fa", bd=3, relief="ridge")
        reg_frame.pack(padx=40, pady=32, fill="x")

        tk.Label(reg_frame, text="Customer Registration", font=self.section_font, bg="#e0f7fa", fg="#023047").pack(pady=8)

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.mobile_var = tk.StringVar()
        self.location_var = tk.StringVar()

        for i, (label, var) in enumerate([
            ("Full Name:", self.name_var),
            ("Email Address:", self.email_var),
            ("Mobile Number:", self.mobile_var),
            ("Location:", self.location_var),
        ]):
            tk.Label(reg_frame, text=label, font=self.label_font, bg="#e0f7fa").pack(anchor="w", pady=(14 if i == 0 else 8, 3), padx=24)
            ttk.Entry(reg_frame, textvariable=var, width=40, style="TEntry").pack(padx=24, pady=4, ipady=5)

        ttk.Button(reg_frame, text="Next ▶", command=self.handle_registration).pack(pady=20)

    def handle_registration(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        mobile = self.mobile_var.get().strip()
        location = self.location_var.get().strip()

        if not name or not email or not mobile or not location:
            messagebox.showerror("Error", "All fields are required!")
            return
        if not re.fullmatch(r"\d{10}", mobile):
            messagebox.showerror("Error", "Mobile number must be exactly 10 digits.")
            return

        if check_duplicate(email, mobile):
            messagebox.showwarning("Duplicate Entry", "This email or mobile number is already registered.\nPlease log in instead.")
            self.create_login_window()
            return

        save_registration(name, email, mobile, location)
        self.create_profile_input_window()

    def create_login_window(self):
        login_win = tk.Toplevel(self.root)
        login_win.geometry("500x400")
        login_win.title("Customer Login")
        login_win.configure(bg="#e0f7fa")

        tk.Label(login_win, text="Customer Login", font=self.section_font, bg="#e0f7fa", fg="#023047").pack(pady=14)

        login_frame = tk.Frame(login_win, bg="#e0f7fa")
        login_frame.pack(fill="x", padx=35, pady=10)

        login_email_var = tk.StringVar()
        login_mobile_var = tk.StringVar()

        tk.Label(login_frame, text="Email Address:", font=self.label_font, bg="#e0f7fa").pack(anchor="w", pady=8, padx=8)
        ttk.Entry(login_frame, textvariable=login_email_var, width=28, style="TEntry").pack(padx=8, pady=4, ipady=5)
        tk.Label(login_frame, text="Mobile Number:", font=self.label_font, bg="#e0f7fa").pack(anchor="w", pady=8, padx=8)
        ttk.Entry(login_frame, textvariable=login_mobile_var, width=28, style="TEntry").pack(padx=8, pady=4, ipady=5)

        def do_login():
            email = login_email_var.get().strip()
            mobile = login_mobile_var.get().strip()
            if not email or not mobile:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            conn = sqlite3.connect("customer_registration.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE email = ? AND mobile = ?", (email, mobile))
            user = cursor.fetchone()
            conn.close()
            if user:
                messagebox.showinfo("Success", "Login successful!")
                login_win.destroy()
                self.create_profile_input_window()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

        ttk.Button(login_frame, text="Login ✅", command=do_login).pack(pady=15)
        ttk.Button(login_frame, text="Cancel ❌", command=login_win.destroy).pack(pady=5)

    def create_profile_input_window(self):
        self.clear_window()

        profile_frame = tk.Frame(self.root, bg="#fbf6f0", bd=3, relief="ridge")
        profile_frame.pack(padx=40, pady=32, fill="x")

        tk.Label(profile_frame, text="Customer Profile", font=self.section_font, bg="#fbf6f0", fg="#bc6c25").pack(pady=8)

        self.age_var = tk.StringVar()
        self.investment_var = tk.StringVar()
        self.maturity_var = tk.StringVar()
        self.smoker_var = tk.StringVar()
        self.health_var = tk.StringVar()

        for i, (label, var) in enumerate([
            ("Age:", self.age_var),
            ("Monthly Investment (₹):", self.investment_var),
            ("Policy Term (Years):", self.maturity_var),
        ]):
            tk.Label(profile_frame, text=label, font=self.label_font, bg="#fbf6f0").pack(anchor="w", pady=(14 if i == 0 else 8, 3), padx=24)
            ttk.Entry(profile_frame, textvariable=var, width=40, style="TEntry").pack(padx=24, pady=4, ipady=5)

        tk.Label(profile_frame, text="Smoker Status:", font=self.label_font, bg="#fbf6f0").pack(anchor="w", pady=8, padx=24)
        self.smoker_dropdown = ttk.Combobox(profile_frame, textvariable=self.smoker_var, values=["Yes", "No"], state="readonly", width=38)
        self.smoker_dropdown.pack(padx=24, pady=4)
        self.smoker_dropdown.set("No")

        tk.Label(profile_frame, text="Health Check Required:", font=self.label_font, bg="#fbf6f0").pack(anchor="w", pady=8, padx=24)
        self.health_dropdown = ttk.Combobox(profile_frame, textvariable=self.health_var, values=["Yes", "No"], state="readonly", width=38)
        self.health_dropdown.pack(padx=24, pady=4)
        self.health_dropdown.set("No")

        ttk.Button(profile_frame, text="Get Recommendations 📊", command=self.generate_recommendations).pack(pady=20)

    def generate_recommendations(self):
        try:
            age = int(self.age_var.get())
            investment = int(self.investment_var.get())
            maturity = int(self.maturity_var.get())
            smoker = self.encoders["Smoker_Required"].transform([self.smoker_var.get()])[0]
            health = self.encoders["Health_Check_Required"].transform([self.health_var.get()])[0]

            if not (18 <= age <= 65):
                messagebox.showerror("Input Error", "Age must be between 18 and 65.")
                return
            if investment <= 0:
                messagebox.showerror("Input Error", "Monthly Investment must be a positive number.")
                return
            if not (5 <= maturity <= 50):
                messagebox.showerror("Input Error", "Policy Term must be between 5 and 50 years.")
                return

            input_data = pd.DataFrame([[age, age, investment, maturity, smoker, health]],
                columns=["Sum of Minimum_Age", "Sum of Maximum_Age", "Sum of Monthly_Premium", "Sum of Policy_Term_Years", "Smoker_Required", "Health_Check_Required"])

            input_scaled = input_data.copy()
            input_scaled[["Sum of Minimum_Age", "Sum of Maximum_Age", "Sum of Monthly_Premium", "Sum of Policy_Term_Years"]] = \
                self.scaler.transform(input_scaled[["Sum of Minimum_Age", "Sum of Maximum_Age", "Sum of Monthly_Premium", "Sum of Policy_Term_Years"]])

            neighbors = self.knn.kneighbors(input_scaled, return_distance=False)[0]
            recommended = self.df.iloc[neighbors].copy()

            recommended["Monthly_Premium_Real"] = recommended["Sum of Monthly_Premium"] * self.scaler.scale_[2] + self.scaler.mean_[2]
            recommended["Policy_Term_Real"] = recommended["Sum of Policy_Term_Years"] * self.scaler.scale_[3] + self.scaler.mean_[3]
            recommended["Diff"] = abs(recommended["Monthly_Premium_Real"] - investment)

            self.final_recommendations = recommended.sort_values(by="Diff").head(10)
            self.create_recommendation_window()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for Age, Monthly Investment, and Policy Term.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def create_recommendation_window(self):
        self.clear_window()
        rec_frame = tk.Frame(self.root, bg="#f4f1de", bd=3, relief="ridge")
        rec_frame.pack(padx=40, pady=32, fill="both", expand=True)

        tk.Label(rec_frame, text=f"Policy Recommendations for {self.name_var.get()}", font=self.section_font, bg="#f4f1de", fg="#3d405b").pack(pady=8)

        canvas = tk.Canvas(rec_frame, bg="#f4f1de", highlightthickness=0)
        scrollbar = ttk.Scrollbar(rec_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f4f1de")

        for idx, row in self.final_recommendations.iterrows():
            policy_name = row.get('Policy_Name', None)
            if not policy_name or pd.isnull(policy_name):
                try:
                    policy_name = self.encoders['Type'].inverse_transform([int(row['Type'])])[0]
                except Exception:
                    policy_name = f"Policy Type: {row['Type']}"

            pol_frame = tk.Frame(scroll_frame, bg="#ffe5ec", bd=2, relief="groove")
            pol_frame.pack(fill="x", padx=20, pady=10)
            tk.Label(pol_frame, text=policy_name, font=self.section_font, bg="#ffe5ec", fg="#c9184a").pack(anchor="w", padx=10, pady=3)
            tk.Label(pol_frame, text=f"Policy ID: {row['Policy_ID']}", font=self.label_font, bg="#ffe5ec").pack(anchor="w", padx=10)
            tk.Label(pol_frame, text=f"Monthly Premium: ₹{round(row['Monthly_Premium_Real'],2):,.2f}", font=self.label_font, bg="#ffe5ec").pack(anchor="w", padx=10)
            tk.Label(pol_frame, text=f"Policy Term: {round(row['Policy_Term_Real'],0):.0f} years", font=self.label_font, bg="#ffe5ec").pack(anchor="w", padx=10)
            url = get_policy_url(policy_name)
            if url:
                btn = ttk.Button(pol_frame, text="🌐 View Details", command=lambda u=url: webbrowser.open_new(u))
                btn.pack(anchor="e", padx=10, pady=8)

        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Bottom controls
        bottom_frame = tk.Frame(self.root, bg="#f4f1de")
        bottom_frame.pack(pady=10, fill='x')
        ttk.Button(bottom_frame, text="Show Investment Graph 📈", command=self.plot_graph).pack(side=tk.LEFT, padx=15)
        ttk.Button(bottom_frame, text="Restart ↩️", command=self.create_registration_window).pack(side=tk.LEFT, padx=15)

    def plot_graph(self):
        premiums = self.final_recommendations["Monthly_Premium_Real"]
        types = []
        for t, row in zip(self.final_recommendations['Type'], self.final_recommendations.itertuples()):
            policy_name = getattr(row, 'Policy_Name', None)
            if not policy_name or pd.isnull(policy_name):
                try:
                    policy_name = self.encoders['Type'].inverse_transform([int(t)])[0]
                except Exception:
                    policy_name = str(t)
            types.append(policy_name)

        plt.figure(figsize=(12, 6))
        plt.bar(types, premiums, color='#c9184a')
        plt.xlabel("Policy Name", fontsize=12)
        plt.ylabel("Monthly Premium (INR)", fontsize=12)
        plt.title("Recommended Policies vs Premium", fontsize=14, weight='bold')
        plt.grid(True, axis="y", linestyle="--", alpha=0.7)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.show()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# ------------------ Main ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LICRecommenderApp(root)
    root.mainloop()
