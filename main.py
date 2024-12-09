import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import datetime

mydb = mysql.connector.connect(host='localhost', password='', user='root', database='djrangas_db')
mycursor = mydb.cursor()

def open_main_program():

    def set_placeholder(entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(foreground="gray")

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(foreground="white")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def basic_tab(frame):

        def fetch_data():
            for row in tree.get_children():
                tree.delete(row)

            query = """
            SELECT MYID, Name, Phone, MT, 
            JoinDate, DATE_ADD(JoinDate, INTERVAL MT MONTH) AS ExpDate, 
            Level, Role, Payment FROM basic_plan WHERE 1=1"""
            params = []
            if search_id_entry.get() != "eg: Search MYID":
                query += " AND MYID = %s"
                params.append(search_id_entry.get())
            try:
                mycursor.execute(query, params)
                results = mycursor.fetchall()

                current_date = datetime.date.today()

                tree.tag_configure("green", background="green")
                tree.tag_configure("blue", background="blue")
                tree.tag_configure("red", background="red")
                green_count = 0
                blue_count = 0
                red_count = 0
                selected_filter = filter_combobox.get()
                for row in results:
                    exp_date = row[5]
                    days_left = (exp_date - current_date).days
                    if days_left > 3:
                        tag = "green"
                        green_count += 1
                    elif days_left > 0:
                        tag = "blue"
                        blue_count += 1
                    else:
                        tag = "red"
                        red_count += 1
                    if selected_filter == "Green" and tag != "green":
                        continue
                    elif selected_filter == "Blue" and tag != "blue":
                        continue
                    elif selected_filter == "Red" and tag != "red":
                        continue
                    elif selected_filter == "All":
                        pass
                    tree.insert("", "end", values=row, tags=(tag,))
                green_label.config(text=f"Green - {green_count}")
                blue_label.config(text=f"Blue - {blue_count}")
                red_label.config(text=f"Red - {red_count}")

            except Exception as e:
                print("Error fetching data:", e)

        def levelup_data():
            try:
                myid = search_id_entry.get()
                if not myid or myid == "eg: Search MYID":
                    messagebox.showerror("Error", "Please search for a valid MYID first.")
                    return
                mycursor.execute("SELECT Level, Role FROM basic_plan WHERE MYID = %s", (myid,))
                result = mycursor.fetchone()
                if result:
                    current_level, current_role = result
                    new_level = current_level + int(MT_combobox.get())
                    new_role = current_role
                    if new_level > 7:
                        new_level = 1
                        new_role += 1
                    mycursor.execute(
                        "UPDATE basic_plan SET MT = %s, JoinDate = %s, Level = %s, Role = %s, Payment= %s WHERE MYID = %s",
                        (
                            MT_combobox.get(), 
                            joindate_entry.get(), 
                            new_level, 
                            new_role, 
                            payment_option.get(),
                            myid),
                    )
                    mydb.commit()
                    messagebox.showinfo("Success", "Data updated successfully.")
                    fetch_data()
                else:
                    messagebox.showerror("Error", "MYID not found.")
            except Exception as e:
                print("Error updating data:", e)

        def register_data():
            try:
                mycursor.execute("SELECT MAX(MYID) FROM basic_plan WHERE MYID LIKE 'BS2024%'")
                result = mycursor.fetchone()
                next_id = "BS20240001"
                if result and result[0]:
                    last_id_num = int(result[0][-4:]) + 1
                    next_id = f"BS2024{last_id_num:04}"

                mycursor.execute(
                    "INSERT INTO basic_plan (MYID, Name, Phone, MT, JoinDate, Level, Role, Payment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        next_id,
                        name_entry.get(),
                        phone_entry.get(),
                        MT_combobox.get(),
                        joindate_entry.get(),
                        MT_combobox.get(),
                        1,
                        payment_option.get(),
                    ),
                )
                mydb.commit()
                messagebox.showinfo("Success", f"New MYID registered: {next_id}")
                fetch_data()
            except Exception as e:
                print("Error registering data:", e)

        columns = ("MYID", "Name", "Phone", "MT", "Join Date", "Exp Date", "Level", "Role", "Payment")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=30)
        tree.grid(row=1, column=3, rowspan=28, padx=0, pady=5, sticky="nsew")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=2, columnspan=2, padx=0, pady=5, sticky="e")
        search_id_entry = ttk.Entry(search_frame, width=30)
        search_id_entry.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        set_placeholder(search_id_entry, "eg: Search MYID")
        filter_combobox = ttk.Combobox(search_frame, values=["All", "Red", "Blue", "Green"], state="readonly", width=10)
        filter_combobox.set("All")
        filter_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(search_frame, text="Search", command=fetch_data).grid(row=0, column=2, pady=5)

        ttk.Label(frame, text="Name").grid(row=2, column=0, padx=0, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(name_entry, "eg: Ko Htoo Aunk Linn")

        ttk.Label(frame, text="Phone").grid(row=3, column=0, padx=0, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.grid(row=3, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(phone_entry, "eg: 09974448285")

        ttk.Label(frame, text="Membership Time").grid(row=4, column=0, padx=0, pady=5)
        MT_combobox = ttk.Combobox(frame, values=["1", "2", "3", "4", "5", "6", "7", "8"], width=4)
        MT_combobox.grid(row=4, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(MT_combobox, "eg: 1")

        ttk.Label(frame, text="Join Date").grid(row=5, column=0, padx=0, pady=5)
        joindate_entry = ttk.Entry(frame, width=11)
        joindate_entry.grid(row=5, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(joindate_entry, "eg: 2000-12-12")

        ttk.Label(frame, text="Payment Method").grid(row=6, column=0, padx=0, pady=5)
        payment_frame = ttk.Frame(frame)
        payment_frame.grid(row=6, column=1, columnspan=2, padx=0, pady=5)
        payment_option = tk.StringVar(value="Cash")
        ttk.Radiobutton(payment_frame, text="Cash", variable=payment_option, value="Cash").grid(row=0, column=0, padx=0, pady=5)
        ttk.Radiobutton(payment_frame, text="KBZPay", variable=payment_option, value="KBZPay").grid(row=0, column=1, padx=0, pady=5)
        ttk.Radiobutton(payment_frame, text="Banking", variable=payment_option, value="Banking").grid(row=0, column=2, padx=0, pady=5)

        ttk.Button(frame, text="Level Up", command=levelup_data).grid(row=8, column=0, padx=0, pady=5)
        ttk.Button(frame, text="Register Basic", command=register_data).grid(row=8, column=1, padx=0, pady=5)

        red_label = ttk.Label(frame, text="Red - 0")
        red_label.grid(row=9, column=0, padx=5, pady=5)

        blue_label = ttk.Label(frame, text="Blue - 0")
        blue_label.grid(row=10, column=0, padx=5, pady=5)

        green_label = ttk.Label(frame, text="Green - 0")
        green_label.grid(row=11, column=0, padx=5, pady=5)

        fetch_data()

    def premium_tab(frame):

        def fetch_data():
            for row in tree.get_children():
                tree.delete(row)

            query = """
            SELECT MYID, Name, Phone, MT, 
            Trainer, Weight, GT, 
            JoinDate, DATE_ADD(JoinDate, INTERVAL MT MONTH) AS ExpDate, 
            Level, Role, Payment FROM premium_plan  WHERE 1=1"""
            params = []
            if search_id_entry.get() != "eg: Search MYID":
                query += " AND MYID = %s"
                params.append(search_id_entry.get())
            try:
                mycursor.execute(query, params)
                results = mycursor.fetchall()

                current_date = datetime.date.today()

                tree.tag_configure("green", background="green")
                tree.tag_configure("blue", background="blue")
                tree.tag_configure("red", background="red")
                green_count = 0
                blue_count = 0
                red_count = 0
                selected_filter = filter_combobox.get()
                for row in results:
                    exp_date = row[8]
                    days_left = (exp_date - current_date).days
                    if days_left > 3:
                        tag = "green"
                        green_count += 1
                    elif days_left > 0:
                        tag = "blue"
                        blue_count += 1
                    else:
                        tag = "red"
                        red_count += 1
                    if selected_filter == "Green" and tag != "green":
                        continue
                    elif selected_filter == "Blue" and tag != "blue":
                        continue
                    elif selected_filter == "Red" and tag != "red":
                        continue
                    elif selected_filter == "All":
                        pass
                    tree.insert("", "end", values=row, tags=(tag,))
                green_label.config(text=f"Green - {green_count}")
                blue_label.config(text=f"Blue - {blue_count}")
                red_label.config(text=f"Red - {red_count}")

            except Exception as e:
                print("Error fetching data:", e)

        def levelup_data():
            try:
                myid = search_id_entry.get()
                if not myid or myid == "eg: Search MYID":
                    messagebox.showerror("Error", "Please search for a valid MYID first.")
                    return
                mycursor.execute("SELECT Level, Role FROM premium_plan WHERE MYID = %s", (myid,))
                result = mycursor.fetchone()
                if result:
                    current_level, current_role = result
                    new_level = current_level + int(MT_combobox.get())
                    new_role = current_role
                    if new_level > 7:
                        new_level = 1
                        new_role += 1
                    mycursor.execute(
                        "UPDATE premium_plan SET MT = %s, Trainer = %s, Weight = %s , GT = %s, JoinDate = %s, Level = %s, Role = %s, Payment = %s WHERE MYID = %s",
                        (
                            MT_combobox.get(), 
                            trainer_combobox.get(), 
                            weight_entry.get() + " " + typeweight_combobox.get(), 
                            alarm_entry.get() + " " + typealarm_combobox.get(), 
                            joindate_entry.get(), 
                            new_level, 
                            new_role, 
                            payment_option.get(), 
                            myid),
                    )
                    mydb.commit()
                    messagebox.showinfo("Success", "Data updated successfully.")
                    fetch_data()
                else:
                    messagebox.showerror("Error", "MYID not found.")
            except Exception as e:
                print("Error updating data:", e)

        def register_data():
            try:
                mycursor.execute("SELECT MAX(MYID) FROM premium_plan WHERE MYID LIKE 'PR2024%'")
                result = mycursor.fetchone()
                next_id = "PR20240001"
                if result and result[0]:
                    last_id_num = int(result[0][-4:]) + 1
                    next_id = f"PR2024{last_id_num:04}"

                mycursor.execute(
                    "INSERT INTO premium_plan (MYID, Name, Phone, MT, Trainer, Weight, GT, JoinDate, Level, Role, Payment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        next_id,
                        name_entry.get(),
                        phone_entry.get(),
                        MT_combobox.get(),
                        trainer_combobox.get(),
                        weight_entry.get() + " " + typeweight_combobox.get(),
                        alarm_entry.get() + " " + typealarm_combobox.get(),
                        joindate_entry.get(),
                        MT_combobox.get(),
                        1,
                        payment_option.get()
                    ),
                )
                mydb.commit()
                messagebox.showinfo("Success", f"New MYID registered: {next_id}")
                fetch_data()
            except Exception as e:
                print("Error registering data:", e)
        
        columns = ("MYID", "Name", "Phone", "MT", "Trainer", "Weight", "GT", "Join Date", "Exp Date", "Level", "Role", "Payment")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=30)
        tree.grid(row=1, column=3, rowspan=28, padx=0, pady=5, sticky="nsew")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=2, columnspan=2, padx=0, pady=5, sticky="e")
        search_id_entry = ttk.Entry(search_frame, width=30)
        search_id_entry.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        set_placeholder(search_id_entry, "eg: Search MYID")
        filter_combobox = ttk.Combobox(search_frame, values=["All", "Red", "Blue", "Green"], state="readonly", width=10)
        filter_combobox.set("All")
        filter_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(search_frame, text="Search", command=fetch_data).grid(row=0, column=2, pady=5)
        
        ttk.Label(frame, text="Name").grid(row=2, column=0, padx=0, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(name_entry, "eg: Ko Htoo Aunk Linn")

        ttk.Label(frame, text="Phone").grid(row=3, column=0, padx=0, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.grid(row=3, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(phone_entry, "eg: 09974448285")

        ttk.Label(frame, text="Membership Time").grid(row=4, column=0, padx=0, pady=5)
        MT_combobox = ttk.Combobox(frame, values=["1", "2", "3", "4", "5", "6", "7", "8"], width=4)
        MT_combobox.grid(row=4, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(MT_combobox, "eg: 1")

        ttk.Label(frame, text="Trainer").grid(row=5, column=0, padx=0, pady=5)
        trainer_combobox = ttk.Combobox(frame, values=["Paing Myint Myint", "La Min Paing Phyo", "Ko Shein", "Yu Ya Thin", "Zin Ko"], width=20)
        trainer_combobox.grid(row=5, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(trainer_combobox, "eg: Trainer Name")

        ttk.Label(frame, text="Weight").grid(row=6, column=0, padx=0, pady=5)
        weight_frame = ttk.Frame(frame)
        weight_frame.grid(row=6, column=1, columnspan=2, padx=0, pady=5, sticky="w")
        weight_entry = ttk.Entry(weight_frame, width=9)
        weight_entry.grid(row=0, column=0)
        set_placeholder(weight_entry, "eg: 180 or 81")
        typeweight_combobox = ttk.Combobox(weight_frame, values=["lb", "kg"], width=8)
        typeweight_combobox.grid(row=0, column=1)
        set_placeholder(typeweight_combobox, "eg: lb or kg")

        ttk.Label(frame, text="Gym Time").grid(row=7, column=0, padx=0, pady=5)
        alarm_frame = ttk.Frame(frame)
        alarm_frame.grid(row=7, column=1, columnspan=2, padx=0, pady=5, sticky="w")
        alarm_entry = ttk.Entry(alarm_frame, width=7)
        alarm_entry.grid(row=0, column=0)
        set_placeholder(alarm_entry, "eg: 10:00")
        typealarm_combobox = ttk.Combobox(alarm_frame, values=["AM", "PM"], width=5)
        typealarm_combobox.grid(row=0, column=1)
        set_placeholder(typealarm_combobox, "eg: AM")

        ttk.Label(frame, text="Join Date").grid(row=8, column=0, padx=0, pady=5)
        joindate_entry = ttk.Entry(frame, width=11)
        joindate_entry.grid(row=8, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(joindate_entry, "eg: 2000-12-12")

        ttk.Label(frame, text="Payment Method").grid(row=9, column=0, padx=0, pady=5)
        payment_frame = ttk.Frame(frame)
        payment_frame.grid(row=9, column=1, columnspan=2, padx=0, pady=5)
        payment_option = tk.StringVar(value="Cash")
        ttk.Radiobutton(payment_frame, text="Cash", variable=payment_option, value="Cash").grid(row=0, column=0, padx=0, pady=5)
        ttk.Radiobutton(payment_frame, text="KBZPay", variable=payment_option, value="KBZPay").grid(row=0, column=1, padx=0, pady=5)
        ttk.Radiobutton(payment_frame, text="Banking", variable=payment_option, value="Banking").grid(row=0, column=2, padx=0, pady=5)

        ttk.Button(frame, text="Level Up", command=levelup_data).grid(row=11, column=0, padx=0, pady=5)
        ttk.Button(frame, text="Register Basic", command=register_data).grid(row=11, column=1, padx=0, pady=5)

        red_label = ttk.Label(frame, text="Red - 0")
        red_label.grid(row=12, column=0, padx=5, pady=5)

        blue_label = ttk.Label(frame, text="Blue - 0")
        blue_label.grid(row=13, column=0, padx=5, pady=5)

        green_label = ttk.Label(frame, text="Green - 0")
        green_label.grid(row=14, column=0, padx=5, pady=5)
        
        fetch_data()

    def group_tab(frame):

        def fetch_data():
            for row in tree.get_children():
                tree.delete(row)

            query = "SELECT MYID, Name, Phone, TeamName, GM, Trainer, GT, JoinDate, DATE_ADD(JoinDate, INTERVAL 1 MONTH) AS ExpDate, Level, Role, Payment FROM group_plan WHERE 1=1"
            params = []

            if search_id_entry.get() != "eg: Search MYID":
                query += " AND MYID = %s"
                params.append(search_id_entry.get())

            try:
                mycursor.execute(query, params)
                results = mycursor.fetchall()

                current_date = datetime.date.today()

                tree.tag_configure("green", background="green")
                tree.tag_configure("blue", background="blue")
                tree.tag_configure("red", background="red")

                green_count = 0
                blue_count = 0
                red_count = 0

                selected_filter = filter_combobox.get()

                for row in results:
                    exp_date = row[8]
                    days_left = (exp_date - current_date).days
                    if days_left > 3:
                        tag = "green"
                        green_count += 1
                    elif days_left > 0:
                        tag = "blue"
                        blue_count += 1
                    else:
                        tag = "red"
                        red_count += 1

                    if selected_filter == "Green" and tag != "green":
                        continue
                    elif selected_filter == "Blue" and tag != "blue":
                        continue
                    elif selected_filter == "Red" and tag != "red":
                        continue
                    elif selected_filter == "All":
                        pass
                    tree.insert("", "end", values=row, tags=(tag,))
                
                red_label.config(text=f"Red - {red_count}")
                blue_label.config(text=f"Blue - {blue_count}")
                green_label.config(text=f"Green - {green_count}")
            except Exception as e:
                print("Error fetching data:", e)
                print("Error fetching data:", e)

        def levelup_data():
            try:
                myid = search_id_entry.get()
                if not myid or myid == "eg: Search MYID":
                    messagebox.showerror("Error", "Please search for a valid MYID first.")
                    return
                mycursor.execute("SELECT Level, Role FROM group_plan WHERE MYID = %s", (myid,))
                result = mycursor.fetchone()

                if result:
                    current_level, current_role = result
                    new_level = current_level + 1
                    new_role = current_role

                    if new_level > 7:
                        new_level = 1
                        new_role += 1

                    mycursor.execute(
                        "UPDATE group_plan SET Trainer = %s, GT = %s, JoinDate = %s, Level = %s, Role = %s, Payment = %s  WHERE MYID = %s",
                        (trainer1_combobox.get() + "/ " + trainer2_combobox.get(), alarm_entry.get() + " " + typealarm_combobox.get(), joindate_entry.get(), new_level, new_role, payment_option.get(), myid),
                    )
                    mydb.commit()
                    messagebox.showinfo("Success", "Data updated successfully.")
                    fetch_data()
                else:
                    messagebox.showerror("Error", "MYID not found.")
            except Exception as e:
                print("Error updating data:", e)

        def register_data():
            try:
                mycursor.execute("SELECT MAX(MYID) FROM group_plan WHERE MYID LIKE 'GP2024%'")
                result = mycursor.fetchone()
                next_id = "GP20240001"
                if result and result[0]:
                    last_id_num = int(result[0][-4:]) + 1
                    next_id = f"GP2024{last_id_num:04}"

                mycursor.execute(
                    "INSERT INTO group_plan (MYID, Name, Phone, TeamName, GM, Trainer, GT, JoinDate, Level, Role, Payment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        next_id,
                        name_entry.get(),
                        phone_entry.get(),
                        teamname_entry.get(),
                        groupofmember_combobox.get(),
                        trainer1_combobox.get() + "/ " + trainer2_combobox.get(),
                        alarm_entry.get() + " " + typealarm_combobox.get(),
                        joindate_entry.get(),
                        1,
                        1,
                        payment_option.get(),
                    ),
                )
                mydb.commit()
                messagebox.showinfo("Success", f"New MYID registered: {next_id}")
                fetch_data()
            except Exception as e:
                print("Error registering data:", e) 

        columns = ("MYID", "Name", "Phone", "Team Name", "GM", "Trainer", "GT", "Join Date", "Exp Date", "Level", "Role", "Payment")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=30)
        tree.grid(row=1, column=3, rowspan=28, padx=0, pady=5, sticky="nsew")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=2, columnspan=2, padx=0, pady=5, sticky="e")
        search_id_entry = ttk.Entry(search_frame, width=30)
        search_id_entry.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        set_placeholder(search_id_entry, "eg: Search MYID")
        filter_combobox = ttk.Combobox(search_frame, values=["All", "Red", "Blue", "Green"], state="readonly", width=10)
        filter_combobox.set("All")
        filter_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(search_frame, text="Search", command=fetch_data).grid(row=0, column=2, pady=5)

        ttk.Label(frame, text="Name").grid(row=2, column=0, padx=0, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(name_entry, "eg: Ko Htoo Aunk Linn")

        ttk.Label(frame,text="Phone").grid(row=3, column=0, padx=0, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.grid(row=3, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(phone_entry, "eg: 09974448285")

        ttk.Label(frame,text="Team Name").grid(row=4, column=0, padx=0, pady=5)
        teamname_entry = ttk.Entry(frame, width=30)
        teamname_entry.grid(row=4, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(teamname_entry, "eg: Cobra")

        ttk.Label(frame,text="Group's Member").grid(row=5, column=0, padx=0, pady=5)
        groupofmember_combobox = ttk.Combobox(frame, values=["3", "4", "5"], width=4)
        groupofmember_combobox.grid(row=5, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(groupofmember_combobox, "eg: 3")

        ttk.Label(frame,text="Select Trainer 1").grid(row=6, column=0, padx=0, pady=5)
        trainer1_combobox = ttk.Combobox(frame, values=["Trainer 1", "Trainer 2", "Trainer 3", "Trainer 4", "Trainer 5"], width=9)
        trainer1_combobox.grid(row=6, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(trainer1_combobox, "eg: Trainer 1")

        ttk.Label(frame,text="Select Trainer 2").grid(row=7, column=0, padx=0, pady=5)
        trainer2_combobox = ttk.Combobox(frame, values=["Trainer 1", "Trainer 2", "Trainer 3", "Trainer 4", "Trainer 5"], width=9)
        trainer2_combobox.grid(row=7, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(trainer2_combobox, "eg: Trainer 2")

        ttk.Label(frame, text="Gym Time").grid(row=8, column=0, padx=0, pady=5)
        alarm_frame = ttk.Frame(frame)
        alarm_frame.grid(row=8, column=1, columnspan=2, padx=0, pady=5, sticky="w")
        alarm_entry = ttk.Entry(alarm_frame, width=7)
        alarm_entry.grid(row=0, column=0)
        set_placeholder(alarm_entry, "eg: 10:00")
        typealarm_combobox = ttk.Combobox(alarm_frame, values=["AM", "PM"], width=5)
        typealarm_combobox.grid(row=0, column=1)
        set_placeholder(typealarm_combobox, "eg: AM")

        ttk.Label(frame,text="Join Date").grid(row=9, column=0, padx=0, pady=5)
        joindate_entry = ttk.Entry(frame, width=11)
        joindate_entry.grid(row=9, column=1, padx=0, pady=5, sticky="w")
        set_placeholder(joindate_entry, "eg: 2000-12-12")

        ttk.Label(frame, text="Payment Method").grid(row=10, column=0, padx=0, pady=5)
        payment_frame = ttk.Frame(frame)
        payment_frame.grid(row=10, column=1, columnspan=2, padx=0, pady=5)
        payment_option = tk.StringVar(value="Cash")
        ttk.Radiobutton(payment_frame, text="Cash", variable=payment_option, value="Cash").grid(row=0, column=0, padx=0, pady=5)
        ttk.Radiobutton(payment_frame, text="KBZPay", variable=payment_option, value="KBZPay").grid(row=0, column=1, padx=0, pady=5)
        ttk.Radiobutton(payment_frame, text="Banking", variable=payment_option, value="Banking").grid(row=0, column=2, padx=0, pady=5)

        ttk.Button(frame, text="Level Up", command=levelup_data).grid(row=12, column=0, padx=0, pady=5)
        ttk.Button(frame, text="Register Group", command=register_data).grid(row=12, column=1, padx=0, pady=5)

        red_label = ttk.Label(frame, text="Red - 0")
        red_label.grid(row=13, column=0, padx=5, pady=5)

        blue_label = ttk.Label(frame, text="Blue - 0")
        blue_label.grid(row=14, column=0, padx=5, pady=5)

        green_label = ttk.Label(frame, text="Green - 0")
        green_label.grid(row=15, column=0, padx=5, pady=5)
        
        fetch_data()

    root = tk.Tk()
    root.title("DJ Rangas's Gym Memberships Update to Date Registration")
    root.geometry("4260x1600") # for Macbook Pro 13-inch, M2, 2022
    root.attributes('-fullscreen', True)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10)

    basic_frame = ttk.Frame(notebook)
    notebook.add(basic_frame, text="Basic")
    basic_tab(basic_frame)

    premium_frame = ttk.Frame(notebook)
    notebook.add(premium_frame, text="Premium")
    premium_tab(premium_frame)

    group_frame = ttk.Frame(notebook)
    notebook.add(group_frame, text="Group")
    group_tab(group_frame)

    root.mainloop()

def authenticate():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "root":
        login_window.destroy()
        open_main_program()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x200")

tk.Label(login_window, text="Username:").pack(pady=10)
username_entry = tk.Entry(login_window)
username_entry.pack()

tk.Label(login_window, text="Password:").pack(pady=10)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

login_button = tk.Button(login_window, text="Login", command=authenticate)
login_button.pack(pady=10)

login_window.mainloop()