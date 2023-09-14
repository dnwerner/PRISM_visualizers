import matplotlib.pyplot as plt
import numpy as np
import os

max_diff = 0.0
min_diff = 0.0

# define data series entry class with timestep and data:
class DataSeriesEntry:
    def __init__(self, timestep, data):
        self.timestep = timestep
        self.data = data

def ReadDataFromFile(file, DIM_N, DIM_Z):
    # data is structured in blocks, we'll keep reading blocks until EOF:
    data_array = []
    timestep = 0
    while True:
        # try to read timestep, if EOF, break:
        try:
            # read first 4 bytes as int32:
            timestep_bytes = file.read(4)
            if len(timestep_bytes) == 0:
                print("Reached EOF after reading",len(data_array),"timesteps. Last timestep:",timestep)
                break

            timestep = int.from_bytes(timestep_bytes, byteorder='little', signed=True)
        except:
            print("Failed to convert timestep to int32 or reached EOF after reading",len(data_array),"timesteps.")
            break

        # read data amount (DIM_N1*DIM_Z1*4 bytes):
        data = np.frombuffer(file.read(DIM_N*DIM_Z*4), dtype=np.float32)
        # reshape data:
        data = data.reshape(DIM_N, DIM_Z)

        # append tuple to data_array:
        data_array.append( (timestep, data) )

    return data_array



def CompareTimeSeries(path1, path2, path_out, delta_TS, output_range, threshold):
    global max_diff
    global min_diff

    # load both files, format is the same as the write format (first header with dimensions, then data)
    # Data is structured in blocks, each block has a timestep and a 2D array of abundances. For simplicity we assume that the dimensions are the same for both files (120x120),
    # but we will still read the dimensions from the header to make sure and break if they are not the same.

    # create output directory (if it does not exist yet):
    if not os.path.exists(path_out):
        os.makedirs(path_out)

    # open file 1:
    try:
        f1 = open(path1, 'rb')
    except:
        print("Error: Could not open file 1:",path1)
        return

    # open file 2:
    try:
        f2 = open(path2, 'rb')
    except:
        print("Error: Could not open file 2:",path2)
        return

    # read header:
    DIM_N1 = int.from_bytes(f1.read(4), byteorder='little', signed=True)
    DIM_Z1 = int.from_bytes(f1.read(4), byteorder='little', signed=True)

    # read header:
    DIM_N2 = int.from_bytes(f2.read(4), byteorder='little', signed=True)
    DIM_Z2 = int.from_bytes(f2.read(4), byteorder='little', signed=True)

    print("File 1:",DIM_N1,"x",DIM_Z1," (",path1,")")
    print("File 2:",DIM_N2,"x",DIM_Z2," (",path2,")")

    # sanity check:
    if DIM_N1 != DIM_N2 or DIM_Z1 != DIM_Z2:
        print("Error: Dimensions of files do not match!")
        return

    # read data:
    data1 = ReadDataFromFile(f1, DIM_N1, DIM_Z1)
    data2 = ReadDataFromFile(f2, DIM_N2, DIM_Z2)

    # debug output:
    print("File 1: Read",len(data1),"timesteps.")
    print("File 2: Read",len(data2),"timesteps.")

    # Create mesh grid with dimensions DIM_N x DIM_Z
    A, Z = np.meshgrid(range(DIM_N1), range(DIM_Z1))

    # For time tracking: get current time
    import time
    start_time = time.time()

    rendered_entries = 0

    # loop over timesteps:
    for i in range(len(data1)):
        timestep1 = data1[i][0]
        
        # first: find corresponding timestep in data2:
        for j in range(len(data2)):
            timestep2 = data2[j][0]
            if timestep2 == timestep1 + delta_TS:
                data_y_2d_1 = data1[i][1]
                data_y_2d_2 = data2[j][1]

                # debug output: max and min values:
                # print("data_y_2d_1 max:",np.amax(data_y_2d_1),"min:",np.amin(data_y_2d_1))
                # print("data_y_2d_2 max:",np.amax(data_y_2d_2),"min:",np.amin(data_y_2d_2))


                # found corresponding timestep, now calculate difference as element wise ratio of data1/data2:
                # if data2 element is 0, set difference to DEFAULT_DIFF_0:
                
                # print content of data_y_2d_1 and data_y_2d_2:
                # print("data_y_2d_1:")
                # print(data_y_2d_1)

                data_y_2d_diff = data_y_2d_2 - data_y_2d_1
                # data_y_2d_diff = np.ma.masked_array(data_y_2d_diff, abs(data_y_2d_diff) < 0.0001)

                current_max = np.amax(data_y_2d_diff)
                current_min = np.amin(data_y_2d_diff)

                max_diff = max(max_diff, current_max)
                min_diff = min(min_diff, current_min)

                # only plot if diff exceeds threshold in either direction:
                if current_max < threshold and current_min > -threshold:
                    break
                
                # plot using data_y_2d_diff with fire color scale
                plt.pcolormesh(A, Z, data_y_2d_diff, vmin=-output_range, vmax=output_range, cmap='seismic') #RdBu

                # add scale, set axis labels:
                plt.colorbar()
                plt.xlabel("N")
                plt.ylabel("Z")

                # save plot, write timestep padded with zeroes:
                save_name = path_out+'/diff_'+str(timestep1).zfill(5)+'.png'

                # add timestamp to plot (aligned to left side, top)
                plt.text(0.01, 0.99, "timestep: "+str(timestep1)+"\nmax diff: "+str(round(max_diff, 4))+"\nmin diff: "+str(round(min_diff, 4)), horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes)

                # print("Saving",save_name)
                plt.savefig(save_name)
                plt.clf()

                rendered_entries += 1

                # break inner loop:
                break

        # progress output, rounded to seconds
        time_elapsed_time = time.time() - start_time
        time_elapsed_string = "(elapsed: "+str(round(time.time() - start_time, 0))+"s"

        # total without unrendered entries:
        total_render_count = len(data1) - (i - rendered_entries)

        time_remaining_string = ""
        if rendered_entries > 20:
            time_remaining_time = ((total_render_count/rendered_entries)-1)*time_elapsed_time
            time_remaining_string = ", remaining: "+str(round(time_remaining_time, 0))+"s"

        print("Progress: ",i+1,"/",len(data1),time_elapsed_string,time_remaining_string,")      Currend diff.= (",current_min,",",current_max,")                ",end='\r', flush=True)

    # close files:
    f1.close()
    f2.close()

    print("Done.         ")


# main: read arguments and call function
if __name__ == "__main__":
    # read arguments:
    import argparse
    parser = argparse.ArgumentParser(description='Compare two time series files.')
    parser.add_argument('path1', metavar='path1', type=str, nargs=1, help='path to first file')
    parser.add_argument('path2', metavar='path2', type=str, nargs=1, help='path to second file')
    parser.add_argument('output_paths', metavar='output_paths', type=str, nargs=1, help='path to output directory')
    parser.add_argument('delta_TS', metavar='delta_TS', type=float, nargs=1, help='temporal offset between files')
    parser.add_argument('output_range', metavar='output_range', type=float, nargs=1, help='output range')
    parser.add_argument('threshold', metavar='threshold', type=float, nargs=1, help='deviation needs to exceed threshold to be plotted')
    args = parser.parse_args()

    # call function:
    CompareTimeSeries(args.path1[0], args.path2[0], args.output_paths[0], args.delta_TS[0], args.output_range[0], args.threshold[0])
