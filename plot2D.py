import matplotlib.pyplot as plt
import numpy as np
import os

def OpenTimeSeries(path,path_output):
    print("Plotting",path,"using time series approach.")

    # Data format example (blocks continue like this but with different amount of data points):
    # timestep      3   time(s)  0.184731E-01   temperature(GK) 0.100000E+02   density(g/cm^3) 0.531701E+08   radius(arb.units) 0.100000E+09
    # 0     1    0.899782E+00
    # 1     1    0.997817E-01
    # 1     2    0.436210E-03
    # 1     3    0.479214E-06
    # 2     3    0.220333E-07
    # 2     4    0.181096E-09

    # we need to iterate line by line and extract the third column of every block that starts with 'timestep':
    with open(path) as f:
        current_index = -1
        data_list = [] # structured data, N,Z,abundance 
        # loop over lines:
        for line in f:
            if line.startswith('timestep'): # if line starts with 'timestep', it's metadata otherwise it's data, if metadata: first column is "timestep", second column is current_index (to be extracted)
                # if current index is set, plot data_list, reset it and continue
                if current_index > -1:
                    # plot y:
                    # print(data_list)
                    print("Plotting, time:",current_index,"        ", end="\r", flush=True)

                    # plot 2d-grid with x=Z, y=A, z=abundance
                    # grid dimensions: 150x150 (value color scale: -15..0)

                    # Create mesh grid with dimensions 150x150
                    DIM_N = 120
                    DIM_Z = 120

                    A, Z = np.meshgrid(range(DIM_N), range(DIM_Z))

                    # Create a 2D array to hold the y data
                    data_y_2d = np.full(A.shape, -15)  # Initialize with -15

                    for data_point in data_list: # zip(data_list_N, data_list_Z, data_list_y):
                        # range sanity check
                        if data_point[0] < DIM_N and data_point[1] < DIM_Z:
                            data_y_2d[data_point[1], data_point[0]] = data_point[2]

                    # Now plot using data_y_2d with fire color scale
                    plt.pcolormesh(A, Z, data_y_2d, vmin=-15, vmax=0, cmap='hot')

                    #add color bar
                    plt.colorbar()

                    plt.xlabel('N')
                    plt.ylabel('Z')


                    # save plot into into subfolder "time":
                    plt.savefig(path_output+path[:-4]+'_'+str(current_index)+'.png')
                    plt.clf()

                    # reset data_list:
                    data_list = []


                # extract current_index:
                current_index = int(line.split()[1])
            else:
                # only continue if current_index is set:
                if current_index > -1:
                    # extract data:
                    extract = line.split()
                    if len(extract) > 2:
                        data_Z = int(extract[0]) # Z
                        data_A = int(extract[1]) # A
                        data_y = float(extract[2]) # abundance

                        # log scale (with sanity check)
                        if data_y > 0:
                            data_y = np.log10(data_y)
                        else:
                            data_y = -15

                        # append to data_list:
                        data_list.append( (data_A - data_Z, data_Z, data_y) )

        print("Plotting, time:",current_index,"        "))


def OpenBasicFile(file):
    # "basic" approach
    print("Plotting",file,"using basic approach.")

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


def plot_dir_contents(input_folder, output_path):
    #### load all files in the directory and plot x-y
    # get list of output_dir contents:
    os.chdir(input_folder)

    #### load all files in the directory and plot x-y
    # get list of directory contents:
    files = os.listdir()

    # if it does not exist yet, create subfolder "time":
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # loop over txt files:
    for file in files:
        if file.endswith('.txt'):
            # if path contains "XTime", we need a more sophisticated way to load the data:
            if 'Time' in file:
                OpenTimeSeries(file,output_path)

            else:
                OpenBasicFile(file)




# main method, read input_folder, output_path and delay from command line arguments
if __name__ == '__main__':
    import sys
    if not (len(sys.argv) in [3]):
        print('Usage: python to_binary.py <input_folder> <output_path>')
        sys.exit(1)

    # read arguments:
    import argparse
    parser = argparse.ArgumentParser(description='Create a gif from a folder of png files.')
    parser.add_argument('input_folder', type=str, help='The folder containing the png files.')
    parser.add_argument('output_path', type=str, help='The path to the output gif file.')
    args = parser.parse_args()

    plot_dir_contents(args.input_folder, args.output_path)