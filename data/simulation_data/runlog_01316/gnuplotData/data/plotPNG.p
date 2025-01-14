set key bottom right
set xr[0:50]
set terminal png
set output '/mnt/code/data/simulation_data/runlog_01316/gnuplotData/drag_22958.png'
plot '/mnt/code/data/simulation_data/runlog_01316/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
