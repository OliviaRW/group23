from dependencies import *

class dst_api():
    def __init__(self, logfile):
        self.connector = Connector(logfile)
        self.delay = 0.5
        self.dst_data_list = [] #list containing filenames of data gathered with the get_data method
    
    def get_data(self, url, filename, column = None, project_name = 'DST data collection'):
        response, _ = self.connector.get(url, project_name = project_name)
        text = json.loads(response.text)
        dataset = text['dataset']
        
        index = list(dataset['dimension']['Tid']['category']['index'].keys())
        data = dataset['value']

        pds = pd.Series(data = data, index = index, name = column)
        pds.index.name = 'Date'
        pds.to_csv(filename, header = True, index = True)
        self.dst_data_list.append(filename)

    def plot_data(self):
        data_list = [(pd.read_csv(filename, header = 0, index_col = 'Date'), filename[:-4]) for filename in self.dst_data_list]
        fig, ax1 = plt.subplots()

        ax2 = ax1.twinx()

        axs = [ax1, ax2]
        linestyles = ['r-', 'b-']

        for i in range(2):
            axs[i].plot(data_list[i][0], linestyles[i])
            axs[i].set_ylabel(data_list[i][1], color = linestyles[i][0])
            axs[i].tick_params('y', colors = linestyles[i][0])

        ax1.set_xticklabels(data_list[0][0].index, rotation = 45) #rotate labels

        #remove most labels
        for i, label in enumerate(ax1.get_xticklabels()):
            if i % 4 != 0:
                label.set_visible(False)

        plt.show()

if __name__ == "__main__":
    dst_api_ = dst_api('dr_log.csv')

    url = r'https://api.statbank.dk/v1/data/VAN5/JSONSTAT?valuePresentation=Value&timeOrder=Ascending&ASYLTYPE=BRU&Tid=%3E%3D2007K1'
    filename = 'asylansøgninger.csv'
    dst_api_.get_data(url, filename, column = 'Asylansøgninger')

    url = r'https://api.statbank.dk/v1/data/VAN77/JSONSTAT?valuePresentation=Value&timeOrder=Ascending&OPHOLD=sum(1%2C2)&Tid=%3E%3D2007K1'
    filename = 'opholdstilladelser.csv'
    dst_api_.get_data(url, filename, column = 'Opholdstilladelser')

    dst_api_.plot_data()