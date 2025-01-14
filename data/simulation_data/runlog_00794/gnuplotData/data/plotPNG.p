set key bottom right
set xr[0:50]
set terminal png
set output '/mnt/code/data/simulation_data/runlog_00794/gnuplotData/drag_28036.png'
plot '/mnt/code/data/simulation_data/runlog_00794/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
