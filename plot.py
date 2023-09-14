import matplotlib.pyplot as plt
import numpy as np
import os

#### load all files in the directory and plot x-y
# get list of directory contents:
files = os.listdir()

# if it does not exist yet, create subfolder "time":
path_time_series = 'time2/'
if not os.path.exists(path_time_series):
    os.makedirs(path_time_series)


# loop over txt files:
for file in files:
    if file.endswith('.txt'):
        # if path contains "XTime", we need a more sophisticated way to load the data:
        if 'XTime' in file:
            # Data format example:
            # timestep      3   time(s)  0.184731E-01   temperature(GK) 0.100000E+02   density(g/cm^3) 0.531701E+08   radius(arb.units) 0.100000E+09
            # 0     1    0.899782E+00
            # 1     1    0.997817E-01
            # 1     2    0.436210E-03
            # 1     3    0.479214E-06
            # 2     3    0.220333E-07
            # 2     4    0.181096E-09

            # we need to iterate line by line and extract the third column of every block that starts with 'timestep':
            # load file line by line (without np)
            
            current_index = -1
            with open(file) as f:
                lines = f.readlines()

                data_list_x = []
                data_list_y = []

                # loop over lines:
                # if line starts with 'timestep', it's metadata otherwise it's data, if metadata: first column is "timestep", second column is current_index (to be extracted)
                for line in lines:
                    if line.startswith('timestep'):
                        # if current index is set, plot data_list, reset it and continue
                        if current_index > -1:
                            # plot y:
                            # print(data_list)
                            print("Plotting, time:",current_index)

                            #set y scale to 0-1, and x-scale to 0-200
                            plt.ylim(-15,0)
                            plt.xlim(0,150)

                            # plot with point style:
                            plt.plot(data_list_x,data_list_y,'o')
                            plt.legend(file)

                            plt.xlabel('Z')
                            plt.ylabel('abundance')


                            # save plot into into subfolder "time":
                            plt.savefig(path_time_series+file[:-4]+'_'+str(current_index)+'.png')
                            plt.clf()

                            # reset data_list:
                            data_list_x = []
                            data_list_y = []

                        # extract current_index:
                        current_index = int(line.split()[1])
                    else:
                        # only continue if current_index is set:
                        if current_index > -1:
                            # extract data:
                            extract = line.split()
                            if len(extract) > 2:
                                data_x = float(extract[0]) # Z
                                data_y = float(extract[2]) # abundance

                                # log scale (with sanity check):
                                if data_y > 0:
                                    data_y = np.log10(data_y)
                                else:
                                    data_y = -15

                                # append to data_list:
                                data_list_x.append(data_x)
                                data_list_y.append(data_y)
            


            # #We want to plot extract the third column of every block that starts with 'timestep':
            # # load file, but be careful since it contains strings and floats
            # data = np.genfromtxt(file, dtype=None, encoding=None)

            # # get indices of lines that start with 'timestep':
            # indices = np.where(data[:,0] == b'timestep')[0]

            # # loop over blocks:
            # for i in range(len(indices)-1):
            #     # get start and end index of block:
            #     start = indices[i]+1
            #     end = indices[i+1]
                
            #     # print block:
            #     print(data[start:end,2])


                
                # # plot y:
                # plt.plot(data[start:end,2])
                # plt.legend(file)

                # plt.xlabel('x')
                # plt.ylabel('y')

                # # save plot into into subfolder "time":
                # plt.savefig('time/'+file[:-4]+'_'+str(i)+'.png')
                # plt.clf()

        else:
            # "basic" approach

            # load file:
            data = np.loadtxt(file)
            # plot x-y:
            plt.plot(data[:,0],data[:,1])
            plt.legend(file)

            plt.xlabel('x')
            plt.ylabel('y')

            # save plot:
            plt.savefig(file[:-4]+'.png')
            plt.clf()
