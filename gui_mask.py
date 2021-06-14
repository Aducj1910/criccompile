import tkinter as tk
from pymongo import MongoClient
import via_gui_top, certifi

connection = MongoClient('mongodb+srv://admin:21441@cluster0.7y5hx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = connection['cricmanagerrecent']
document = db['tokens']



root = tk.Tk()
root.geometry("230x200")
root.title("Cricket Data Engine")

def all_children (refe) :
    _list = refe.winfo_children()

    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())

    return _list

def runEngine(switch):
	if(switch == 't20' or switch == 'test' or switch == 'odi'):
		result = via_gui_top.main(switch)
		completion = tk.Label(root, text=f"Complete! {str(result)} new balls were found & updated\nCheck updates/{switch}.xlsx")
		completion.grid(row=2, column=0)
	else:
		tk.Label(root, text="Invalid Format Entered", fg="#ff0000").grid(row=3, column=0)

def postauth():
	game_formatlbl = tk.Label(root, text="Enter 't20', 'odi' or 'test'")
	game_format = tk.Entry(root, text="Enter format")
	game_formatlbl.grid(row=0, column=0)
	game_format.grid(row=1, column=0)
	run_engine = tk.Button(root, text="Run Engine", command=lambda: runEngine(game_format.get()))
	run_engine.grid(row=2, column=0)

def authenticate(token):
	loading = tk.Label(root, text="Authenticating...")
	error = tk.Label(root, text="AUTHENTICATION DENIED, \n EITHER YOU EXCEEDED YOUR MAXIMUM CALLS \nOR THE TOKEN IS INCORRECT", fg="#ff0000")

	loading.grid(row=3, column=0)


	if(document.find_one({"_id": token}) == None or document.find_one({"_id": token})['calls'] > 35):
		error.grid(row=3, column=0)
		loading.destroy()
	else:
		document.update({'_id': token}, {'$inc': {'calls': 1}})
		widget_list = all_children(root)
		print(widget_list)
		for item in widget_list:
			item.destroy()
			postauth()


tokenlbl = tk.Label(root, text="Enter Auth Token")
tokenlbl.grid(row=0, column=0)

token = tk.Entry(root, text="Enter Auth Token")
token.grid(row=1,column=0)

login = tk.Button(root, text="Login", command=lambda: authenticate(token.get()))
login.grid(row=2, column=0)


root.mainloop()