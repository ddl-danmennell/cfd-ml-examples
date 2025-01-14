set key bottom right
set xr[0:50]
set terminal png
set output '/mnt/code/data/simulation_data/runlog_01664/gnuplotData/drag_28100.png'
plot '/mnt/code/data/simulation_data/runlog_01664/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
