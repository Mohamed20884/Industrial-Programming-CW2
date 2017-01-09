import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class Histograms():
    """
    Creates Matplotlib Histograms
    Parameters:
        data: a dictionary with bins as keys and numbers as values
        title: string that stores the title of the histogram
        independent: this is a boolean value used to create an independent window or embed it into the gui
    """
    def __init__(self, data, title, independent):
        n = len(data)
        if independent:
            # creates a bar chart with the values of the dictionary
            plt.bar(range(n), list(data.values()), align='center')
            # sets the bins to the keys of the dictionary
            plt.xticks(range(n), list(data.keys()), rotation=90)  # counts.values())
            plt.title(title)
            plt.show()
        else:
            f = Figure(figsize=(n, 5), dpi=100)
            a = f.add_subplot(111)
            # creates a bar chart with the values of the dictionary
            a.bar(range(n), list(data.values()), align='center')
            # sets the bins to the keys of the dictionary
            a.set_xticklabels([""] + list(data.keys()), rotation=90)
            plt.setp(a, title=title)
            # tightens the layout of the chart
            f.tight_layout()
            self.figure = f
