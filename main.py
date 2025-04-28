import tkinter
import sqlite3
from tkinter import messagebox
import re
import datetime
import random


def login():
    global session, cnt
    user = txtUser.get()
    pas = txtPass.get()

    query = "SELECT * FROM users WHERE username=?"
    result = cnt.execute(query, (user,))
    data = result.fetchone()

    if not data:
        lblMsg.configure(text='User does not exist!', fg='red')
        return

    password = data[2]
    failed_attempts = data[5]
    lock_until = data[6]

    try:
        failed_attempts = int(failed_attempts) if failed_attempts is not None else 0
    except Exception:
        failed_attempts = 0

    if lock_until:
        try:
            lock_until_dt = datetime.datetime.strptime(lock_until, "%Y-%m-%d %H:%M:%S")
            if lock_until_dt > datetime.datetime.now():
                lblMsg.configure(text=f'Account locked until {lock_until}', fg='red')
                return
        except Exception:
            pass

    max_attempts = 5
    if pas != password:
        failed_attempts += 1
        remaining_attempts = max_attempts - failed_attempts

        if remaining_attempts <= 0:
            lock_until = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
            cnt.execute("UPDATE users SET failed_attempts=?, lock_until=? WHERE username=?", (failed_attempts, lock_until, user))
            cnt.commit()
            lblMsg.configure(text='Account locked for 48 hours due to too many failed attempts!', fg='red')
        else:
            cnt.execute("UPDATE users SET failed_attempts=? WHERE username=?", (failed_attempts, user))
            cnt.commit()
            lblMsg.configure(text=f'Wrong password! {remaining_attempts} attempts left.', fg='red')
        return

    #lblMsg.configure(text='Welcome to your account!', fg='green')
    session = data
    win.lblWelcome.config(text=f"Welcome, {session[1]}!")
    txtUser.delete(0, 'end')
    txtPass.delete(0, 'end')
    btnLogin.configure(state='disabled')
    #btnLogout.configure(state='active')
    btnDelete.configure(state='active')
    btnshop.configure(state='active')
    btnQuickLogout.configure(state='active') 
    cnt.execute("UPDATE users SET failed_attempts=0, lock_until=NULL WHERE username=?", (user,))
    cnt.commit()

def logout():
    global session
    session = False
    lblMsg.configure(text='You are logged out now!', fg='green')
    btnLogin.configure(state='active')
    #btnLogout.configure(state='disabled')
    btnshop.configure(state='disabled')
    btnDelete.configure(state='disabled')
    btnQuickLogout.configure(state='disabled')  

def delAc():
    global session
    result = messagebox.askyesno(title='Delete Account', message='Are you sure?')
    if not result:
        lblMsg.configure(text='Delete canceled by user', fg='red')
        return
    query = f"DELETE FROM users WHERE id=?"
    cnt.execute(query, (session[0],))
    cnt.commit()
    lblMsg.configure(text='Your account deleted!', fg='green')
    session = False
    btnLogin.configure(state='active')
    #btnLogout.configure(state='disabled')
    btnDelete.configure(state='disabled')
    btnshop.configure(state='disabled')

def signup():
    def signValidate(user, pas, cpas, addr):
        if user == '' or pas == '' or cpas == '' or addr == '':
            return False, "empty field error!"
        if pas != cpas:
            return False, "password and confirmation mismatch!"
        if len(pas) < 8:
            return False, "password length error!"
        sql = "SELECT * FROM users WHERE username=?"
        result = cnt.execute(sql, (user,))
        data = result.fetchall()
        if len(data) > 0:
            return False, "username already exist!"
        exp = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(exp, pas):
            return False, "invalid password!"
        return True, ""

    def newUser():
        user = txtUser.get()
        pas = txtPass.get()
        cpas = txtcPass.get()
        addr = txtAddr.get()
        result, msg = signValidate(user, pas, cpas, addr)
        if result == False:
            lblMsg.configure(text=msg, fg='red')
        else:
            sql = 'INSERT INTO users (username,password,address,grade) VALUES (?, ?, ?, 0)'
            cnt.execute(sql, (user, pas, addr))
            cnt.commit()
            lblMsg.configure(text='submit done!', fg='green')
            txtUser.delete(0, 'end')
            txtPass.delete(0, 'end')
            txtcPass.delete(0, 'end')
            txtAddr.delete(0, 'end')

    winSignup = tkinter.Toplevel(win)
    winSignup.title('Signup panel')
    winSignup.geometry('320x340')
    winSignup.resizable(False, False)
    lblUser = tkinter.Label(winSignup, text='Username:')
    lblUser.pack()
    txtUser = tkinter.Entry(winSignup)
    txtUser.pack()
    lblPass = tkinter.Label(winSignup, text='Password:')
    lblPass.pack()
    txtPass = tkinter.Entry(winSignup)
    txtPass.pack()
    lblcPass = tkinter.Label(winSignup, text='Password confirm:')
    lblcPass.pack()
    txtcPass = tkinter.Entry(winSignup)
    txtcPass.pack()
    lblAddr = tkinter.Label(winSignup, text='Address:')
    lblAddr.pack()
    txtAddr = tkinter.Entry(winSignup)
    txtAddr.pack()
    lblMsg = tkinter.Label(winSignup, text='')
    lblMsg.pack()
    btnSignup = tkinter.Button(winSignup, text='Signup', command=newUser)
    btnSignup.pack(pady=10)
    apply_theme(winSignup)
    add_hover_effects(winSignup)

def getAllproducts():
    sql="SELECT * FROM products"
    result=cnt.execute(sql)
    products=result.fetchall()
    return products

def shopPanel():
    winShop = tkinter.Toplevel(win)
    winShop.title('SHOP PANEL')
    winShop.geometry('500x600')
    winShop.resizable(False, False)
    lstbox = tkinter.Listbox(winShop, width=65, height=18)
    lstbox.pack()
    products = getAllproducts()
    for product in products:
        text = f'id:{product[0]} name:{product[1]} price:{product[2]} numbers:{product[3]}'
        lstbox.insert('end', text)
    lblid = tkinter.Label(winShop, text='id:')
    lblid.pack()
    txtid = tkinter.Entry(winShop)
    txtid.pack()
    lblnum = tkinter.Label(winShop, text='number:')
    lblnum.pack()
    txtnum = tkinter.Entry(winShop)
    txtnum.pack()
    lblmsg2 = tkinter.Label(winShop, text='')
    lblmsg2.pack()

    cart = []

    
    lblCartSummary = tkinter.Label(winShop, text='Cart: 0 items | Total: 0')
    lblCartSummary.pack(pady=10)

    def update_cart_summary():
        total_items = sum(item['quantity'] for item in cart)
        total_price = sum(item['quantity'] * item['price'] for item in cart)
        lblCartSummary.config(text=f'Cart: {total_items} items | Total: {total_price}')

    def addToCart():
        product_id = txtid.get()
        product_num = txtnum.get()
        if not product_id.isdigit() or not product_num.isdigit():
            lblmsg2.configure(text='Invalid ID or number!', fg='red')
            return
        sql = "SELECT * FROM products WHERE id=?"
        result = cnt.execute(sql, (int(product_id),))
        product = result.fetchone()
        if not product:
            lblmsg2.configure(text='Product not found!', fg='red')
        elif int(product_num) > product[3]:
            lblmsg2.configure(text='Not enough stock!', fg='red')
        else:
            cart_item = {
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': int(product_num)
            }
            cart.append(cart_item)
            
            new_stock = product[3] - int(product_num)
            cnt.execute("UPDATE products SET numbers=? WHERE id=?", (new_stock, product[0]))
            cnt.commit()
            lblmsg2.configure(text='Added to cart! ✔️', fg='green')
            winShop.after(700, lambda: lblmsg2.configure(text='', fg='black'))
            
            
            lstbox.delete(0, 'end')
            products = getAllproducts()
            for product in products:
                text = f'id:{product[0]} name:{product[1]} price:{product[2]} numbers:{product[3]}'
                lstbox.insert('end', text)
            
            update_cart_summary()

    def viewCart():
        winCart = tkinter.Toplevel(winShop)
        winCart.title('Cart')
        winCart.geometry('420x340')
        winCart.resizable(False, False)
        lblUserName = tkinter.Label(winCart, text=f'Username: {session[1]}')
        lblUserName.pack()
        cartListbox = tkinter.Listbox(winCart, width=50, height=15)
        cartListbox.pack()
        for item in cart:
            cart_text = f"id:{item['id']} name:{item['name']} price:{item['price']} quantity:{item['quantity']}"
            cartListbox.insert('end', cart_text)
        apply_theme(winCart)
        add_hover_effects(winCart)

    btnBuy = tkinter.Button(winShop, text='BUY', command=addToCart, bg='lightgreen', width=15, height=1)
    btnBuy.pack(pady=(10, 2))
    btnCart = tkinter.Button(winShop, text='View Cart', command=viewCart, bg='lightblue', width=15, height=1)
    btnCart.pack(pady=(2, 10))
    apply_theme(winShop)
    add_hover_effects(winShop)

def forgotPassword():
    winForgot = tkinter.Toplevel(win)
    winForgot.title('Forgot Password')
    winForgot.geometry('320x220')
    winForgot.resizable(False, False)

    lblUser = tkinter.Label(winForgot, text='Username:')
    lblUser.pack()
    txtUser = tkinter.Entry(winForgot)
    txtUser.pack()


    a = random.randint(1, 9)
    b = random.randint(1, 9)
    lblQ = tkinter.Label(winForgot, text=f'What is {a} + {b}?')
    lblQ.pack()
    txtAns = tkinter.Entry(winForgot)
    txtAns.pack()

    lblMsg = tkinter.Label(winForgot, text='')
    lblMsg.pack()

    def checkAnswer():
        user = txtUser.get()
        ans = txtAns.get()
        if not user or not ans.isdigit():
            lblMsg.configure(text='Fill all fields correctly!', fg='red')
            return
        if int(ans) == a + b:
            result = cnt.execute("SELECT * FROM users WHERE username=?", (user,))
            data = result.fetchone()
            if not data:
                lblMsg.configure(text='User not found!', fg='red')
                return
            lock_until = data[6]
            if not lock_until:
                lblMsg.configure(text='Account is not locked!', fg='blue')
                return
            # آنلاک کردن اکانت
            cnt.execute("UPDATE users SET failed_attempts=0, lock_until=NULL WHERE username=?", (user,))
            cnt.commit()
            lblMsg.configure(text='Account unlocked!', fg='green')
        else:
            lblMsg.configure(text='Wrong answer!', fg='red')

    btnCheck = tkinter.Button(winForgot, text='Unlock', command=checkAnswer)
    btnCheck.pack(pady=10)
    apply_theme(winForgot)
    add_hover_effects(winForgot)

def apply_theme(window):
    global dark_mode
    if dark_mode:
        bg = '#222'
        fg = '#fff'
        btn_bg = '#444'
        entry_bg = '#333'
    else:
        bg = '#f0f0f0'
        fg = '#000'
        btn_bg = 'SystemButtonFace'
        entry_bg = '#fff'

    window.configure(bg=bg)
    for widget in window.winfo_children():
        if isinstance(widget, tkinter.Label):
            widget.configure(bg=bg, fg=fg)
        elif isinstance(widget, tkinter.Entry):
            widget.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        elif isinstance(widget, tkinter.Button):
            text = widget.cget('text').lower()
            if 'login' in text:
                widget.configure(bg='lightgreen', fg=fg)
            elif 'logout' in text:
                widget.configure(bg='lightcoral', fg=fg)
            elif 'delete' in text:
                widget.configure(bg='lightpink', fg=fg)
            elif 'signup' in text:
                widget.configure(bg='lightblue', fg=fg)
            elif 'forgot' in text:
                widget.configure(bg='lightgray', fg=fg)
            elif 'shop' in text:
                widget.configure(bg='lightyellow', fg='black')
            elif 'unlock' in text:
                widget.configure(bg='gold', fg=fg)
            elif 'buy' in text:
                widget.configure(bg='lightgreen', fg=fg)
            elif 'view cart' in text:
                widget.configure(bg='lightblue', fg=fg)
            elif 'toggle theme' in text:
                widget.configure(bg='orange', fg=fg)
            else:
                widget.configure(bg=btn_bg, fg=fg)
        elif isinstance(widget, tkinter.Listbox):
            widget.configure(bg=entry_bg, fg=fg)
        if isinstance(widget, tkinter.Toplevel):
            apply_theme(widget)

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme(win)
    for w in win.winfo_children():
        if isinstance(w, tkinter.Toplevel):
            apply_theme(w)

def add_hover_effects(window):
    for widget in window.winfo_children():
        if isinstance(widget, tkinter.Button):
            normal_bg = widget.cget('bg')
            def on_enter(e, w=widget):
                w['bg'] = '#888'
            def on_leave(e, w=widget, bg=normal_bg):
                w['bg'] = bg
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        if isinstance(widget, tkinter.Toplevel):
            add_hover_effects(widget)

def update_datetime():
    now = datetime.datetime.now().strftime('%Y-%m-%d   %H:%M:%S')
    lblDateTime.config(text=now)
    win.after(1000, update_datetime)


#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-main-_-_-_-_-_-_-_-_-_-_--_-_-_-_-_-_-_-


session = False
cnt = sqlite3.connect('shop.db')
dark_mode = False

win = tkinter.Tk()
win.title('Login Panel')
win.geometry('400x430')
win.resizable(False, False)
win.lblWelcome = tkinter.Label(win, text='', fg='blue', font=('Arial', 14, 'bold'))
win.lblWelcome.pack(pady=(5, 10))

lblUser = tkinter.Label(win, text='Username:')
lblUser.pack(pady=(20, 2))
txtUser = tkinter.Entry(win)
txtUser.pack(pady=2)
lblPass = tkinter.Label(win, text='Password:')
lblPass.pack(pady=2)
txtPass = tkinter.Entry(win)
txtPass.pack(pady=2)
lblMsg = tkinter.Label(win, text='')
lblMsg.pack(pady=5)


btnLogin = tkinter.Button(win, text='Login', command=login, bg='lightgreen', width=16, height=2)
btnLogin.pack(pady=(10, 2))
btnSignup = tkinter.Button(win, text='Signup', command=signup, bg='lightblue', width=16, height=2)
btnSignup.pack(pady=2)
frame_actions = tkinter.Frame(win, bg=win['bg'])
frame_actions.pack(pady=8)
#btnLogout = tkinter.Button(frame_actions, text='Logout', state='disabled', command=logout, bg='lightcoral', width=10)
#btnLogout.grid(row=0, column=0, padx=2)
btnDelete = tkinter.Button(frame_actions, text='Delete account!', state='disabled', command=delAc, bg='lightpink', width=13)
btnDelete.grid(row=0, column=1, padx=2)
btnTheme = tkinter.Button(frame_actions, text='Toggle Theme', command=toggle_theme, bg='orange', width=11)
btnTheme.grid(row=0, column=2, padx=2)
btnshop = tkinter.Button(win, text='shop', state='disabled', command=shopPanel, bg='lightyellow', fg='black', width=20, height=1)
btnshop.pack(pady=(10, 2))
btnForgot = tkinter.Button(win, text='Forgot Password', command=forgotPassword, bg='lightgray', width=20, height=1)
btnForgot.pack(pady=(2, 15))
btnQuickLogout = tkinter.Button(win, text='❌', command=logout, bg='white', fg='red', font=('Arial', 12, 'bold'), width=2, height=1, relief='flat', cursor='hand2')
btnQuickLogout.place(x=365, y=5) 
btnQuickLogout.configure(state='disabled') 

lblDateTime = tkinter.Label(win, text='', fg='gray', bg=win['bg'], font=('Arial', 9))
lblDateTime.place(x=220, y=410) 
update_datetime()

apply_theme(win)
add_hover_effects(win)

win.mainloop()


