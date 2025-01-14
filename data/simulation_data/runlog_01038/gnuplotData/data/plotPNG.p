set key bottom right
set xr[0:50]
set terminal png
set output '/mnt/code/data/simulation_data/runlog_01038/gnuplotData/drag_23536.png'
plot '/mnt/code/data/simulation_data/runlog_01038/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
