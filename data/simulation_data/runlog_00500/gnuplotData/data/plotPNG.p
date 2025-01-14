set key bottom right
set xr[0:50]
set terminal png
set output '/mnt/code/data/simulation_data/runlog_00500/gnuplotData/drag_43380.png'
plot '/mnt/code/data/simulation_data/runlog_00500/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
