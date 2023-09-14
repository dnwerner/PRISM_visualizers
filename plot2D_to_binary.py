import matplotlib.pyplot as plt
import numpy as np
import os

# define nuclide chart grid dimensions that we want to compare:
DIM_N = 120
DIM_Z = 120

path_time_series = 'time2D_bin/'

def OpenTimeSeries(path):
    # Get raw input path (without extension):
    file_name_raw = path[:-4]
    print("Converting",file_name_raw,"to binary: Starting...        ", end="\r", flush=True)

    # Data format example (blocks continue like this but with different amount of data points):
    # timestep      3   time(s)  0.184731E-01   temperature(GK) 0.100000E+02   density(g/cm^3) 0.531701E+08   radius(arb.units) 0.100000E+09
    # 0     1    0.899782E+00
    # 1     1    0.997817E-01
    # 1     2    0.436210E-03
    # 1     3    0.479214E-06
    # 2     3    0.220333E-07
    # 2     4    0.181096E-09

    # open output binary file and keep reference to file, which will later be written to:
    f_out = open(path_time_series+file_name_raw+'.dat', 'wb')

    # write header to output file (dimensions):
    f_out.write(DIM_N.to_bytes(4, byteorder='little', signed=True))
    f_out.write(DIM_Z.to_bytes(4, byteorder='little', signed=True))

    # Create mesh grid with dimensions DIM_N x DIM_Z
    A, Z = np.meshgrid(range(DIM_N), range(DIM_Z))

    DEBUG_CACHE = []

    # we need to iterate line by line and extract the third column of every block that starts with 'timestep':
    current_index = -1
    with open(path) as f:
        data_list = [] # structured data, N,Z,abundance 
        # loop over lines:
        for line in f:
            if line.startswith('timestep'): # if line starts with 'timestep', it's metadata otherwise it's data, if metadata: first column is "timestep", second column is current_index (to be extracted)
                # if current index is set, plot data_list, reset it and continue
                if current_index > -1:
                    print("Converting",file_name_raw,"to binary: Time step:",current_index,"        ", end="\r", flush=True)

                    # Create a 2D array to hold the y data
                    data_y_2d = np.full(A.shape, -15.0)  # Initialize with 0

                    for data_point in data_list:
                        if data_point[0] < DIM_N and data_point[1] < DIM_Z: # range sanity check
                            data_y_2d[data_point[1], data_point[0]] = np.log10( data_point[2] )
                            # print("DEBUG: Appending data point",data_point[0],data_point[1],data_point[2])

                    # print("DEBUG: Appending data for timestep",current_index)
                    # # also print data:
                    # for i in range(10):
                    #     for j in range(10):
                    #         print(data_y_2d[i,j], end=" ", flush=True)
                    #     print("")

                    # print("DEBUG: Range:")
                    # print("DEBUG: min:",np.amin(data_y_2d))
                    # print("DEBUG: max:",np.amax(data_y_2d))

                    # print("DEBUG: -")
                    DEBUG_CACHE.append(data_y_2d)

                    # Now plot using data_y_2d with fire color scale
                    #plt.pcolormesh(A, Z, data_y_2d, vmin=-15, vmax=0, cmap='hot')

                    # Write current mesh in binary format, format, assuming DIM_N=150, DIM_Z=150:
                    # first write timestep as int32, then write data_y_2d as float32
                    f_out.write(current_index.to_bytes(4, byteorder='little', signed=True))
                    f_out.write(data_y_2d.astype(np.float32).tobytes())

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
                        # if data_y > 0:
                        #     data_y = np.log10(data_y)
                        # else:
                        #     data_y = -15

                        # append to data_list:
                        data_list.append( (data_A - data_Z, data_Z, data_y) )


    # DEBUG test: read back data and compare:
    f_out.close()

    # # re-open file:
    # f_out = open(path_time_series+file_name_raw+'.dat', 'rb')

    # # read header:
    # deb_DIM_N = int.from_bytes(f_out.read(4), byteorder='little', signed=True)
    # deb_DIM_Z = int.from_bytes(f_out.read(4), byteorder='little', signed=True)

    # print("DEBUG: File:",deb_DIM_N,"x",deb_DIM_Z)

    # # read data:
    # for i in range(len(DEBUG_CACHE)):
    #     # read timestep:
    #     try:
    #         deb_timestep = int.from_bytes(f_out.read(4), byteorder='little', signed=True)
    #     except:
    #         print("DEBUG: Could not read timestep!")
    #         return
        
    #     print("DEBUG: Reading timestep:",deb_timestep,"        ", end="\r", flush=True)

    #     # read data:
    #     try:
    #         deb_data = np.frombuffer(f_out.read(deb_DIM_N*deb_DIM_Z*4), dtype=np.float32)
    #         deb_data = deb_data.reshape((deb_DIM_N, deb_DIM_Z))
    #     except:
    #         print("DEBUG: Could not read data!")
    #         return

    #     # compare:
    #     if np.array_equal(deb_data, DEBUG_CACHE[i]):
    #         max_val = np.amax(deb_data)
    #         min_val = np.amin(deb_data)
    #         print("DEBUG: Time step",deb_timestep,"matches ( min:",min_val,"max:",max_val,")")
    #     else:
    #         print("DEBUG: Time step",deb_timestep,"does not match!")
    #         return


    # # close output file:
    # f_out.close()
    print("Converting",file_name_raw,"to binary: Completed.        ")


def plot_dir_contents(input_folder, output_path):
    #### load all files in the directory and plot x-y
    # get list of output_dir contents:
    os.chdir(input_folder)

    # get list of input files:
    files = os.listdir()

    print(files)

    # if it does not exist yet, create subfolder "time":
    if not os.path.exists(path_time_series):
        os.makedirs(path_time_series)

    # loop over txt files:
    for file in files:
        if file.endswith('.txt'):
            # if path contains "XTime", we need a more sophisticated way to load the data:
            if 'Time' in file:
                print("Loading time series from file:",file)
                OpenTimeSeries(file)

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
