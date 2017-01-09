from json_parser import JsonParser
import re
import httpagentparser
from histograms import Histograms
from reader import Reader
from json import JSONDecodeError
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Listbox, END, RIGHT, BOTTOM
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg


class TaskManager():
    """
        Static class used to call functions
    """
    p = JsonParser()
    """
        gets all user ids from the data supplied
    """
    @staticmethod
    def get_all_users(data):
        users = []
        for i in data:
            if i.get("visitor_uuid") not in users:
                users.append(i.get("visitor_uuid"))
        return users

    """
        gets all document ids from the data supplied
    """
    @staticmethod
    def get_all_documents(data):
        documents = []
        for i in data:
            if i.get("subject_doc_id") not in documents:
                documents.append(i.get("subject_doc_id"))
        return documents

    """
        gets all the document ids from the data supplied which has been visited by a certain user
    """
    @staticmethod
    def get_all_documents_by_user(user_id, data):
        data = TaskManager.filter_data(data, "visitor_uuid", user_id)
        return TaskManager.get_all_documents(data)

    """
        gets all the user ids from the data supplied who have visited a certain document
    """
    @staticmethod
    def get_all_users_by_doc(doc_id, data):
        data = TaskManager.filter_data(data, "subject_doc_id", doc_id)
        return TaskManager.get_all_users(data)

    """
        loads, reads and parses in a file, using the supplied filename
    """
    @staticmethod
    def load_file(file):
        if file is not None:
            r = Reader(file)
        else:
            r = Reader("sample_100k_lines.json")
        while True:
            try:
                TaskManager.p.add(r.read_line())
            except JSONDecodeError:
                print("Completed Parsing File")
                break
        return TaskManager.p.get_all()

    """
        handles all the tasks by calling the corresponding functions which fulfill the tasks objectives
    """
    @staticmethod
    def task_handler(doc_id, user_id, task_id, data, g, cmd):
        if g is not None:
            if g.canvas is not None:
                g.canvas.get_tk_widget().destroy()
            if g.toolbar is not None:
                g.toolbar.destroy()
                g.toolbar = None
            if g.listbox is not None:
                g.listbox.destroy()
        if task_id == "2a":
            if cmd and doc_id not in TaskManager.get_all_documents(data) or doc_id is None:
                print("Please Provide a Valid Document ID")
            else:
                histogram = Histograms(TaskManager.get_countries(doc_id, TaskManager.filter_data(data, "subject_doc_id", doc_id)), "Task 2A", cmd)
                if not cmd:
                    TaskManager.plot_figure_gui(g, histogram)
        elif task_id == "2b":
            if cmd and doc_id not in TaskManager.get_all_documents(data) or doc_id is None:
                print("Please Provide a Valid Document ID")
            else:
                histogram = Histograms(TaskManager.get_continents(doc_id, TaskManager.filter_data(data, "subject_doc_id", doc_id)), "Task 2B", cmd)
                if not cmd:
                    TaskManager.plot_figure_gui(g, histogram)
        elif task_id == "3a":
            histogram = Histograms(TaskManager.simple_get_all_browser(data), "Task 3A", cmd)
            if not cmd:
                TaskManager.plot_figure_gui(g, histogram)
        elif task_id == "3b":
            histogram = Histograms(TaskManager.get_all_browser(data), "Task 3B", cmd)
            if not cmd:
                TaskManager.plot_figure_gui(g, histogram)
        elif task_id == "4":
            top10 = TaskManager.get_top_10(data)
            if cmd:
                print(top10)
            else:
                TaskManager.load_list(g, top10)
        elif task_id == "5a":
            users = TaskManager.get_all_users_by_doc(doc_id, data)
            if cmd:
                print(users)
            else:
                TaskManager.load_list(g, users)
        elif task_id == "5b":
            docs = TaskManager.get_all_documents_by_user(user_id, data)
            if cmd:
                print(docs)
            else:
                TaskManager.load_list(g, docs)
        elif task_id == "5c":
            also_likes = TaskManager.task5(data, doc_id, user_id, None)
            if cmd:
                print(also_likes)
            else:
                TaskManager.load_list(g, also_likes)
        elif task_id == "5d":
            also_likes = TaskManager.task5(data, doc_id, user_id, TaskManager.sort_by_readership)
            if cmd:
                print(also_likes)
            else:
                TaskManager.load_list(g, also_likes)
        elif task_id == "5e":
            also_likes = TaskManager.task5(data, doc_id, user_id, TaskManager.sort_by_number)
            if cmd:
                print(also_likes)
            else:
                TaskManager.load_list(g, also_likes)
        else:
            if cmd:
                print("Invalid Task")

    """
        filters data based on a specific key satisfying a specific value and return the filter list
    """
    @staticmethod
    def filter_data(data, filter_key, value):
        results = []
        for i in data:
            if i.get(filter_key) == value:
                results.append(i)
        return results
    """
        filters data based on a specific key not satisfying a specific value and return the filter list
    """
    @staticmethod
    def inverse_filter_data(data, filter_key, value):
        results = []
        for i in data:
            if not i.get(filter_key) == value:
                results.append(i)
        return results

    """
        gets the top 10 users who spend the most time reading in a descending order
    """
    @staticmethod
    def get_top_10(data):
        count = dict()
        users = TaskManager.get_all_users(data)
        for i in users:
            count.update({i: 0})
        for j in data:
            if not j.get("event_readtime") is None:
                count[j["visitor_uuid"]] += j.get("event_readtime")
        results = sorted(count, key=count.get, reverse=True)
        results = results[:10]
        return results

    """
        gets how frequently each browser has been used to visit the application, this does distinguish versions
        of browsers
    """
    @staticmethod
    def simple_get_all_browser(data):
        browsers = {}
        for i in data:
            b = httpagentparser.simple_detect(i["visitor_useragent"])[1]
            if b not in browsers:
                browsers.update({b: 1})
            else:
                browsers[b] += 1
        return browsers

    """
        gets how frequently each browser has been used to visit the application, this does not distinguish versions
        of browsers
    """
    @staticmethod
    def get_all_browser(data):
        results = {}
        browsers = TaskManager.simple_get_all_browser(data)
        for i in browsers.keys():
            r = re.findall('.+ [0-9]', i)
            for j in r:
                if j[:-2] not in results:
                    results.update({j[:-2]: browsers[i]})
                else:
                    results[j[:-2]] += browsers[i]
        return results

    """
        gets how frequently users have visited a specific document by their country
    """
    @staticmethod
    def get_countries(doc_id, data):
        countries = dict()
        for k in data:
            if k.get("subject_doc_id") == doc_id:
                if k.get("visitor_country") in countries.keys():
                    countries[k["visitor_country"]] += 1
                else:
                    countries.update({k.get("visitor_country"): 1})
        return countries

    """
        gets how frequently users have visited a specific document by their continents
    """
    @staticmethod
    def get_continents(doc_id, data):
        continents = {"AF": 0, "EU": 0, "OC": 0, "NA": 0, "SA": 0, "AS": 0}
        data = TaskManager.get_countries(doc_id, data)
        if data is None:
            return
        for i in data.keys():
            if TaskManager.cntry_to_cont[i] == "AF":
                continents["AF"] += data[i]
            elif TaskManager.cntry_to_cont[i] == "EU":
                continents["EU"] += data[i]
            elif TaskManager.cntry_to_cont[i] == "OC":
                continents["OC"] += data[i]
            elif TaskManager.cntry_to_cont[i] == "NA":
                continents["NA"] += data[i]
            elif TaskManager.cntry_to_cont[i] == "SA":
                continents["SA"] += data[i]
            elif TaskManager.cntry_to_cont[i] == "AS":
                continents["AS"] += data[i]
        return continents

    """
        gets all the documents other users have read based on a document the supplied user has read
    """
    @staticmethod
    def task5(data, doc_id, user, sorting):
        users_read = []
        if doc_id is not None:
            d = TaskManager.filter_data(data, "subject_doc_id", doc_id)
            u = TaskManager.get_all_users(d)
            if user in u:
                for i in u:
                    if i is not user:
                        u2 = TaskManager.filter_data(data, "visitor_uuid", i)
                        users_read.append(
                            TaskManager.get_all_documents(TaskManager.filter_data(TaskManager.inverse_filter_data(u2, "subject_doc_id", doc_id), "event_type", "read")))
                docs = dict()
                for i in users_read:
                    for j in i:
                        if j is not None:
                            if j not in docs.keys():
                                docs.update({j: 1})
                            else:
                                docs[j] += 1
                if sorting is not None:
                    result = sorting(docs)
                else:
                    result = docs
            else:
                result = []
                print("Please Enter a Valid User ID")
        else:
            result = []
            print("Please Enter a Valid Document ID")
        return result

    """
        sorts the documents by the time spent reading them and returns them in a descending order
    """
    @staticmethod
    def sort_by_readership(data):
        result = dict()
        for i in data.keys():
            temp = TaskManager.filter_data(TaskManager.p.get_all(), "subject_doc_id", i)
            for j in temp:
                if j.get("event_readtime") is not None:
                    if i not in result:
                        result.update({i: j.get("event_readtime")})
                    else:
                        result[i] += j.get("event_readtime")
        print(result)
        return TaskManager.sort_by_number(result)

    """
        sorts the documents by the number of users who read them and returns them in a descending order
    """
    @staticmethod
    def sort_by_number(data):
        if len(data) < 11:
            return sorted(data.keys(), reverse=True, key=data.__getitem__)
        else:
            return sorted(data.keys(), reverse=True, key=data.__getitem__)[:10]

    """
        embeds a chart to the GUI
    """
    @staticmethod
    def plot_figure_gui(g, histogram):
        g.canvas = FigureCanvasTkAgg(histogram.figure, g.main)
        g.canvas.show()
        g.canvas.get_tk_widget().pack(expand=1, side=RIGHT)
        g.toolbar = NavigationToolbar2TkAgg(g.canvas, g.main)
        g.toolbar.update()
        g.main.mainloop()

    """
        embeds a listbox with the supplied data items to the GUI
    """
    @staticmethod
    def load_list(g, data):
        g.listbox = Listbox(width=60    )
        g.listbox.pack(expand=True, side=BOTTOM)
        for i in data:
            g.listbox.insert(END, i)
        g.main.mainloop()

    # dictionary used to assign countries to continents
    cntry_to_cont = {
        'AP': 'AS',
        'AF': 'AS',
        'AX': 'EU',
        'AL': 'EU',
        'DZ': 'AF',
        'AS': 'OC',
        'AD': 'EU',
        'AO': 'AF',
        'AI': 'NA',
        'AQ': 'AN',
        'AG': 'NA',
        'AR': 'SA',
        'AM': 'AS',
        'AW': 'NA',
        'AU': 'OC',
        'AT': 'EU',
        'AZ': 'AS',
        'BS': 'NA',
        'BH': 'AS',
        'BD': 'AS',
        'BB': 'NA',
        'BY': 'EU',
        'BE': 'EU',
        'BZ': 'NA',
        'BJ': 'AF',
        'BM': 'NA',
        'BT': 'AS',
        'BO': 'SA',
        'BQ': 'NA',
        'BA': 'EU',
        'BW': 'AF',
        'BV': 'AN',
        'BR': 'SA',
        'IO': 'AS',
        'VG': 'NA',
        'BN': 'AS',
        'BG': 'EU',
        'BF': 'AF',
        'BI': 'AF',
        'KH': 'AS',
        'CM': 'AF',
        'CA': 'NA',
        'CV': 'AF',
        'KY': 'NA',
        'CF': 'AF',
        'TD': 'AF',
        'CL': 'SA',
        'CN': 'AS',
        'CX': 'AS',
        'CC': 'AS',
        'CO': 'SA',
        'KM': 'AF',
        'CD': 'AF',
        'CG': 'AF',
        'CK': 'OC',
        'CR': 'NA',
        'CI': 'AF',
        'HR': 'EU',
        'CU': 'NA',
        'CW': 'NA',
        'CY': 'AS',
        'CZ': 'EU',
        'DK': 'EU',
        'DJ': 'AF',
        'DM': 'NA',
        'DO': 'NA',
        'EC': 'SA',
        'EG': 'AF',
        'SV': 'NA',
        'GQ': 'AF',
        'ER': 'AF',
        'EE': 'EU',
        'ET': 'AF',
        'FO': 'EU',
        'FK': 'SA',
        'FJ': 'OC',
        'FI': 'EU',
        'FR': 'EU',
        'GF': 'SA',
        'PF': 'OC',
        'TF': 'AN',
        'GA': 'AF',
        'GM': 'AF',
        'GE': 'AS',
        'DE': 'EU',
        'GH': 'AF',
        'GI': 'EU',
        'GR': 'EU',
        'GL': 'NA',
        'GD': 'NA',
        'GP': 'NA',
        'GU': 'OC',
        'GT': 'NA',
        'GG': 'EU',
        'GN': 'AF',
        'GW': 'AF',
        'GY': 'SA',
        'HT': 'NA',
        'HM': 'AN',
        'VA': 'EU',
        'HN': 'NA',
        'HK': 'AS',
        'HU': 'EU',
        'IS': 'EU',
        'IN': 'AS',
        'ID': 'AS',
        'IR': 'AS',
        'IQ': 'AS',
        'IE': 'EU',
        'IM': 'EU',
        'IL': 'AS',
        'IT': 'EU',
        'JM': 'NA',
        'JP': 'AS',
        'JE': 'EU',
        'JO': 'AS',
        'KZ': 'AS',
        'KE': 'AF',
        'KI': 'OC',
        'KP': 'AS',
        'KR': 'AS',
        'KW': 'AS',
        'KG': 'AS',
        'LA': 'AS',
        'LV': 'EU',
        'LB': 'AS',
        'LS': 'AF',
        'LR': 'AF',
        'LY': 'AF',
        'LI': 'EU',
        'LT': 'EU',
        'LU': 'EU',
        'MO': 'AS',
        'MK': 'EU',
        'MG': 'AF',
        'MW': 'AF',
        'MY': 'AS',
        'MV': 'AS',
        'ML': 'AF',
        'MT': 'EU',
        'MH': 'OC',
        'MQ': 'NA',
        'MR': 'AF',
        'MU': 'AF',
        'YT': 'AF',
        'MX': 'NA',
        'FM': 'OC',
        'MD': 'EU',
        'MC': 'EU',
        'MN': 'AS',
        'ME': 'EU',
        'MS': 'NA',
        'MA': 'AF',
        'MZ': 'AF',
        'MM': 'AS',
        'NA': 'AF',
        'NR': 'OC',
        'NP': 'AS',
        'NL': 'EU',
        'NC': 'OC',
        'NZ': 'OC',
        'NI': 'NA',
        'NE': 'AF',
        'NG': 'AF',
        'NU': 'OC',
        'NF': 'OC',
        'MP': 'OC',
        'NO': 'EU',
        'OM': 'AS',
        'PK': 'AS',
        'PW': 'OC',
        'PS': 'AS',
        'PA': 'NA',
        'PG': 'OC',
        'PY': 'SA',
        'PE': 'SA',
        'PH': 'AS',
        'PN': 'OC',
        'PL': 'EU',
        'PT': 'EU',
        'PR': 'NA',
        'QA': 'AS',
        'RE': 'AF',
        'RO': 'EU',
        'RU': 'EU',
        'RW': 'AF',
        'BL': 'NA',
        'SH': 'AF',
        'KN': 'NA',
        'LC': 'NA',
        'MF': 'NA',
        'PM': 'NA',
        'VC': 'NA',
        'WS': 'OC',
        'SM': 'EU',
        'ST': 'AF',
        'SA': 'AS',
        'SN': 'AF',
        'RS': 'EU',
        'SC': 'AF',
        'SL': 'AF',
        'SG': 'AS',
        'SX': 'NA',
        'SK': 'EU',
        'SI': 'EU',
        'SB': 'OC',
        'SO': 'AF',
        'ZA': 'AF',
        'GS': 'AN',
        'SS': 'AF',
        'ES': 'EU',
        'LK': 'AS',
        'SD': 'AF',
        'SR': 'SA',
        'SJ': 'EU',
        'SZ': 'AF',
        'SE': 'EU',
        'CH': 'EU',
        'SY': 'AS',
        'TW': 'AS',
        'TJ': 'AS',
        'TZ': 'AF',
        'TH': 'AS',
        'TL': 'AS',
        'TG': 'AF',
        'TK': 'OC',
        'TO': 'OC',
        'TT': 'NA',
        'TN': 'AF',
        'TR': 'AS',
        'TM': 'AS',
        'TC': 'NA',
        'TV': 'OC',
        'UG': 'AF',
        'UA': 'EU',
        'AE': 'AS',
        'GB': 'EU',
        'US': 'NA',
        'UM': 'OC',
        'VI': 'NA',
        'UY': 'SA',
        'UZ': 'AS',
        'VU': 'OC',
        'VE': 'SA',
        'VN': 'AS',
        'WF': 'OC',
        'EH': 'AF',
        'YE': 'AS',
        'ZM': 'AF',
        'ZW': 'AF',
        'ZZ': 'Unknown',
        'EU': 'Unknown'
    }