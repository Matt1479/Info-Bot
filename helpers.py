from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
import matplotlib.pyplot as plt


class Plotter:
    def __init__(self):
        """
        Initializes plotter.
        """
        self._figure, self._ax = plt.subplots()

    def setup(
        self,
        x_label="Default x label",
        y_label="Default y label",
        title="Default title",
        grid=False,
        legend=False,
    ):
        """
        Sets up labels, title, enable grid and legend if set explicitly.
        Should be called after Plotter.plot() method.
        """
        self._ax.set_xlabel(x_label)
        self._ax.set_ylabel(y_label)
        self._ax.set_title(title)

        self._ax.grid(grid)
        if legend:
            self._ax.legend()

        # Rotate x label by 30 degrees so it won't overlap
        plt.setp(
            self._ax.get_xticklabels(),
            rotation=30,
            horizontalalignment="right",
            fontsize="xx-small",
        )

        # Add padding to x_label
        plt.subplots_adjust(bottom=0.15)

    def plot(self, data0, data1, label=None):
        """
        A helper function to make a graph.
        """
        self._out = self._ax.plot(data0, data1, label=label)

    def show(self):
        """
        Show the plot.
        """
        plt.show()

    def save(self, filename):
        """
        Save the plot a a file.
        """
        plt.savefig(filename)

    def clear(self):
        plt.cla()


def list_dict_to_list(l_dict: list, key: str):
    """
    Convert a list of dictionaries to a list
    of values associated to key `key`.
    """
    return [d[key] for d in l_dict]


def calc_n_months_between_dates(start, end):
    """
    Calculate the number of months between two dates.
    """
    start_dt = datetime.strptime(start, "%Y-%m")
    end_dt = datetime.strptime(end, "%Y-%m")
    return len([dt for dt in rrule(MONTHLY, dtstart=start_dt, until=end_dt)]) - 1
